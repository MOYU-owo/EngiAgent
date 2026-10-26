"""Explicit UI actions over existing business interfaces; no Streamlit dependency."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Callable, Literal, Any
import json

from engi_agent.engineering.schema import EngineeringState, TaskRequest, ParameterValue
from engi_agent.engineering.workflow import prepare, confirm, run_engineering
from engi_agent.engineering.cn_workflow import revise, ALL_TARGETS
from engi_agent.engineering.cn_schema import CN_UNITS
from engi_agent.engineering.roles import FixtureRoles, DeepSeekRoles, RolePlan
from engi_agent.engineering.reporting import markdown_report

ROOT = Path(__file__).resolve().parents[3]
CASES = {
    '完整新方案设计': 'cn_design', '已有梁独立验算': 'cn_existing',
    '仅抗弯局部验算': 'cn_flexure_only', '挠度超限后有限改设': 'cn_redesign',
    '改设达到上限停止': 'cn_no_solution', '梁高修改与局部重算': 'cn_existing',
}
ENUM_FIELDS = {'support_type', 'load_case', 'section_type', 'concrete_grade', 'steel_grade',
               'stirrup_grade', 'self_weight_mode', 'environment_class'}


def load_case(label: str) -> TaskRequest:
    return TaskRequest.model_validate_json((ROOT / 'examples' / 'engineering' / (CASES[label]+'.json')).read_text(encoding='utf-8'))


@dataclass
class AgentCall:
    role: str
    mode: str
    inputs: dict
    outputs: dict | None = None
    status: str = 'running'
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    elapsed_seconds: float | None = None
    diagnostic: str | None = None
    run_id: int = 0


class RecordingRoles:
    """Record real protocol-bound calls, never provider internals or credentials."""
    def __init__(self, inner, calls: list[AgentCall], mode: str, run_id=0):
        self.inner, self.calls, self.mode = inner, calls, mode
        self.run_id=run_id

    def _invoke(self, role, payload, fn):
        event = AgentCall(role, self.mode, payload)
        event.run_id=self.run_id
        self.calls.append(event)
        started = perf_counter()
        try:
            result = fn()
            event.outputs = result.model_dump()
            event.status = 'success'
            return result
        except Exception as exc:
            event.status = 'error'
            event.diagnostic = type(exc).__name__  # Never record arbitrary provider text.
            raise
        finally:
            event.elapsed_seconds = perf_counter()-started
            if event.status=='running':
                event.status='error'
                event.diagnostic='InterruptedOperation'

    def parse(self, query):
        return self._invoke('Dispatcher', {'query': query}, lambda: TaskRequest.model_validate(self.inner.parse(query)))

    def plan(self, role, payload):
        return self._invoke(role, payload, lambda: RolePlan.model_validate(self.inner.plan(role, payload)))


@dataclass
class WorkbenchSession:
    case_name: str = '未加载案例'
    stage: str = 'empty'
    draft: EngineeringState | None = None
    result: EngineeringState | None = None
    calls: list[AgentCall] = field(default_factory=list)
    progress: list[dict] = field(default_factory=list)
    audit_runs: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    editor_generation: int = 0
    completed_runs: int = 0
    executed_mode: str | None = None

    def mark_dirty(self):
        if self.stage != 'running':
            self.stage = 'editing'
            if self.draft:
                self.draft.confirmed=False
                self.draft.confirmation_hash=None
                for value in self.draft.request.parameters.values():value.confirmed=False

    def load(self, request: TaskRequest, name: str, *, record_read=True):
        if request.code != 'cn-2024':
            raise ValueError('当前工作台支持cn-2024；原教学模式请继续使用CLI。')
        if request.task_type=='unsupported':
            raise ValueError('此任务超出简支矩形RC梁、全跨均布恒活载及单层受拉筋范围，未加载或执行。')
        request=request.model_copy(deep=True)
        for value in request.parameters.values():value.confirmed=False
        # Validate before replacing a previous session.
        prepared = prepare(request)
        self.case_name, self.draft, self.result = name, prepared, None
        self.stage = 'editing' if prepared.missing_parameters or prepared.errors else 'validated'
        self.errors = prepared.errors.copy()
        self.calls, self.progress, self.audit_runs = [], [], []
        self.completed_runs = 0
        self.executed_mode = None
        self.editor_generation += 1
        if record_read:
            self.calls.append(AgentCall('Dispatcher', 'structured_file', {'case': name}, request.model_dump(), 'success'))

    def parse(self, query: str, base: TaskRequest | None = None, roles=None):
        if not query.strip(): raise ValueError('请先输入自然语言需求。')
        self.stage, self.errors = 'parsing', []
        calls: list[AgentCall] = []
        try:
            client = RecordingRoles(roles or DeepSeekRoles(), calls, 'DeepSeek')
            parsed = client.parse('按中国规范cn-2024提取任务。'+query)
            if base:
                inherited = {k: v.model_copy(deep=True) for k, v in base.parameters.items()}
                for value in inherited.values(): value.source, value.confirmed = 'template', False
                parsed.parameters = {**inherited, **parsed.parameters}
            parsed.user_query = query
            self.load(parsed, '自然语言任务', record_read=False)
            self.calls = calls
        except Exception as exc:
            self.stage = 'error'
            self.errors = ['任务解析失败（'+type(exc).__name__+'）；未确认或执行工程计算。']
            self.calls.extend(calls)
            raise ValueError(self.errors[0]) from None

    def apply(self, rows: list[dict], task_type: str, targets: list[str], auto: bool, iterations: int):
        if self.draft is None: raise ValueError('请先加载案例或解析需求。')
        self.stage, self.errors = 'editing', []
        candidate = self.draft.request.model_copy(deep=True)
        candidate.task_type = task_type
        candidate.targets = ALL_TARGETS.copy() if task_type == 'new_design' else targets
        candidate.auto_redesign = bool(auto) if task_type == 'new_design' else False
        candidate.max_iterations = iterations
        try:
            for row in rows:
                key, text = row['字段'], str(row['输入值']).strip()
                if key not in CN_UNITS: raise ValueError('未知参数：'+key)
                if not text:
                    candidate.parameters.pop(key, None)
                    continue
                unit = str(row.get('单位') or '').strip() or None
                try: value = text if key in ENUM_FIELDS else float(text)
                except ValueError: raise ValueError(row.get('参数',key)+'必须填写数值。') from None
                old = candidate.parameters.get(key)
                if old and str(old.value) == text and old.unit == unit:
                    continue
                candidate.parameters[key] = ParameterValue(value=value, unit=unit, source='user')
            if task_type == 'new_design':
                # Design quantities are computed by the existing design tools.
                for key in ('bar_count','stirrup_spacing_mm','design_moment_kn_m','design_shear_kn'):
                    candidate.parameters.pop(key,None)
            candidate = TaskRequest.model_validate(candidate.model_dump())
            prepared = prepare(candidate)
            if self.result:
                old = self.result.request.parameters
                changed = {k:v for k,v in prepared.request.parameters.items()
                           if k not in old or v.value != old[k].value or v.unit != old[k].unit}
                revision = revise(self.result,changed,targets=prepared.request.targets)
                prepared.cache, prepared.revisions = revision.cache, revision.revisions
                prepared.design_revision = revision.design_revision
                deleted = set(old)-prepared.request.parameters.keys()
                prepared.revision_reason = revision.revision_reason + ('；移除：'+','.join(sorted(deleted)) if deleted else '')
            self.draft = prepared
            self.stage = 'editing' if prepared.missing_parameters or prepared.errors else 'validated'
            self.errors = prepared.errors.copy()
            self.editor_generation += 1
        except ValueError as exc:
            self.errors = [str(exc)]
            raise

    def confirm(self):
        if self.stage != 'validated' or self.draft is None:
            raise ValueError('参数需先校验且补齐缺项，才能确认。')
        # Rebuild typed objects after Streamlit source hot-reload; keep the same
        # canonical CN profile, real cache and revision evidence. No calculation.
        prepared = prepare(TaskRequest.model_validate(self.draft.request.model_dump()))
        prepared.cache=self.draft.cache
        prepared.revisions=self.draft.revisions
        prepared.design_revision=self.draft.design_revision
        prepared.revision_reason=self.draft.revision_reason
        self.draft = confirm(prepared)
        self.stage = 'confirmed'

    def run(self, mode: Literal['offline','DeepSeek'], callback: Callable | None = None, roles=None):
        if self.stage != 'confirmed' or self.draft is None:
            raise ValueError('只能运行已确认的当前参数；刷新与重复点击不会再次执行。')
        self.stage, self.errors, self.progress = 'running', [], []
        start_call = len(self.calls)
        try:
            client = RecordingRoles(roles or (FixtureRoles(self.draft.request) if mode == 'offline' else DeepSeekRoles()), self.calls, mode,self.completed_runs+1)
            def on_event(event):
                self.progress.append(event.model_dump())
                if callback: callback(event)
            self.result = run_engineering(self.draft, client, on_event=on_event)
            self.draft = self.result.model_copy(deep=True)
            self.executed_mode = mode
            self.completed_runs += 1
            self.audit_runs.append({'run':self.completed_runs,'mode':mode,'revision':self.result.design_revision,
                                    'calls_start':start_call,'calls_end':len(self.calls),
                                    'progress':self.progress.copy()})
            self.stage = 'completed'
            self.errors = self.result.errors.copy()
        except Exception as exc:
            self.stage = 'error'
            self.errors = ['执行未完成（'+type(exc).__name__+'），不能形成通过结论。']
        finally:
            if self.stage=='running':
                self.stage='error'
                self.errors=['执行被中断，未形成新的结论；系统不会自动重试模型调用。']
        return self.result

    def downloads(self):
        if self.result is None: return {}
        return {
            'md': markdown_report(self.result,'engiagent_result.json').encode('utf-8'),
            'json': self.result.model_dump_json(indent=2).encode('utf-8'),
            'audit': json.dumps({'calls':[vars(c) for c in self.calls], 'runs':self.audit_runs},ensure_ascii=False,indent=2).encode('utf-8'),
        }


@dataclass
class ExperimentRecord:
    """Reserved input contract, with unknown measurements explicitly nullable."""
    case_id: str
    group: Literal['human','general_llm','fixed_python','engiagent']
    code_version: str
    evidence: list[str] = field(default_factory=list)
    status: Literal['not_run','completed','error'] = 'not_run'
    elapsed_seconds: float | None = None
    tokens: int | None = None
    cost: float | None = None
