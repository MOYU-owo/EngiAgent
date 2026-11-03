"""Explicit UI actions over existing business interfaces; no Streamlit dependency."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Callable, Literal
import json

from engi_agent.engineering.cn_schema import EngineeringState, TaskRequest, ParameterValue
from engi_agent.engineering.cn_workflow import prepare, confirm, run_engineering
from engi_agent.engineering.cn_workflow import revise, ALL_TARGETS
from engi_agent.engineering.cn_schema import CN_UNITS
from engi_agent.engineering.roles import FixtureRoles, DeepSeekRoles, RolePlan, ProgramRoles, CandidateDecision
from engi_agent.engineering.cn_presentation import markdown_report

ROOT = Path(__file__).resolve().parents[3]
CASES = {
    '完整新方案设计': 'cn_design', '截面与配筋联合设计': 'cn_section_search', '已有梁独立验算': 'cn_existing',
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

    @property
    def supports_candidate_planning(self):
        return getattr(self.inner,'supports_candidate_planning',False)

    def choose_candidate(self,payload):
        return self._invoke('DesignDecision',payload,
            lambda:CandidateDecision.model_validate(self.inner.choose_candidate(payload)))


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
    consultations: list[dict] = field(default_factory=list)
    preference_comparison: dict = field(default_factory=dict)

    def mark_dirty(self):
        if self.stage != 'running':
            self.stage = 'editing'
            if self.draft:
                self.draft.confirmed=False
                self.draft.confirmation_hash=None
                for value in self.draft.request.parameters.values():value.confirmed=False

    def load(self, request: TaskRequest, name: str, *, record_read=True):
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
        self.consultations = []
        self.completed_runs = 0
        self.executed_mode = None
        self.editor_generation += 1
        if record_read:
            self.calls.append(AgentCall('Dispatcher', 'structured_file', {'case': name}, request.model_dump(), 'success'))

    def parse(self, query: str, base: TaskRequest | None = None, roles=None, *, image_evidence=None):
        if not query.strip(): raise ValueError('请先输入自然语言需求。')
        self.stage, self.errors = 'parsing', []
        calls: list[AgentCall] = []
        if image_evidence is not None:
            calls.append(AgentCall('VisionOCR', 'DeepSeek',
                                   {'image_sha256': image_evidence['image_sha256']},
                                   image_evidence, 'success'))
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
            if image_evidence is not None:
                self.case_name = '图片识别任务'
        except Exception as exc:
            self.stage = 'error'
            self.errors = ['任务解析失败（'+type(exc).__name__+'）；未确认或执行工程计算。']
            self.calls.extend(calls)
            raise ValueError(self.errors[0]) from None

    def apply(self, rows: list[dict], task_type: str, targets: list[str], auto: bool, iterations: int, *, search_diameters=None, solution_count=1):
        if self.draft is None: raise ValueError('请先加载案例或解析需求。')
        self.stage, self.errors = 'editing', []
        candidate = self.draft.request.model_copy(deep=True)
        candidate.task_type = task_type
        candidate.targets = ALL_TARGETS.copy() if task_type == 'new_design' else targets
        candidate.auto_redesign = bool(auto) if task_type == 'new_design' else False
        candidate.max_iterations = iterations
        candidate.search_diameters_mm = list(search_diameters or []) if task_type == 'new_design' else []
        candidate.solution_count = solution_count if task_type == 'new_design' else 1
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

    def run(self, mode: Literal['offline','DeepSeek','program'], callback: Callable | None = None, roles=None):
        if self.stage != 'confirmed' or self.draft is None:
            raise ValueError('只能运行已确认的当前参数；刷新与重复点击不会再次执行。')
        self.stage, self.errors, self.progress = 'running', [], []
        start_call = len(self.calls)
        try:
            inner=roles or (FixtureRoles(self.draft.request) if mode=='offline' else ProgramRoles() if mode=='program' else DeepSeekRoles())
            client = RecordingRoles(inner, self.calls, mode,self.completed_runs+1)
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

    def ask_expert(self, query: str, mode='offline', client=None):
        from engi_agent.engineering.consultation import consult, DeepSeekConsultant, RuleConsultant
        if self.stage != 'completed' or self.result is None:
            raise ValueError('请先完成当前参数的计算，再针对当前结果咨询。')
        if mode not in ('offline','DeepSeek'):raise ValueError('不支持的咨询模式')
        try:
            inner=client or (DeepSeekConsultant() if mode=='DeepSeek' else RuleConsultant())
        except Exception:
            raise ValueError('咨询模型配置不可用，请检查本机配置或选择离线咨询。') from None
        recorder=RecordingRoles(inner,self.calls,mode,self.completed_runs)
        class RecordedConsultant:
            def consult(_, question, evidence, history):
                return recorder._invoke('ExpertConsultation',
                    {'query':question,'current':evidence,'recent_consultations':history[-4:]},
                    lambda:inner.consult(question,evidence,history))
        history=[{'query':r['query'],'answer':r.get('answer',''),'decision':r['decision']} for r in self.consultations[-4:]]
        try:
            reply=consult(self.result,query,RecordedConsultant(),history)
        except ValueError as exc:
            # Our validation errors are useful; provider payloads are not displayed.
            if self.calls and self.calls[-1].status=='error':
                raise ValueError('咨询解析未完成，请重试；当前工程结果没有改变。') from None
            raise ValueError('咨询建议未通过校验：'+str(exc)) from None
        except Exception:
            raise ValueError('咨询请求失败；当前工程结果没有改变。') from None
        self.consultations.append(reply.model_dump())
        return reply

    def adopt_expert_proposal(self, reply_id):
        from engi_agent.engineering.consultation import ConsultationReply, apply_proposal
        if self.stage!='completed' or self.result is None:
            raise ValueError('已有待处理草稿，请先完成或重新加载任务。')
        record=next((r for r in self.consultations if r['id']==reply_id),None)
        if record is None:raise ValueError('没有此咨询记录')
        pending=apply_proposal(self.result,ConsultationReply.model_validate(record))
        self.draft=pending
        self.stage='validated'
        self.errors=[]
        self.editor_generation+=1
        record['applied']=True
        return pending

    def select_design_alternative(self, revision):
        from engi_agent.engineering.cn_schema import ToolResult, EvaluationResult
        if self.stage != 'completed' or self.result is None:
            raise ValueError('请先完成当前草稿，才能选择已验证候选。')
        if not any(r['revision'] == revision for r in self.result.design_alternatives):
            raise ValueError('只能选择当前任务中已通过全部请求检查的候选。')
        chosen = next(r for r in self.result.revisions if r['revision'] == revision)
        if chosen['evaluation']['status'] != 'pass':
            raise ValueError('候选未通过，不能选用。')
        state = self.result.model_copy(deep=True)
        state.candidate = chosen['candidate'].copy()
        state.tool_results = {k:ToolResult.model_validate(v) for k,v in chosen['tools'].items()}
        state.evaluation = EvaluationResult.model_validate(chosen['evaluation'])
        state.plan_trace = [t.copy() for t in chosen['trace']]
        state.execution_plan = list(state.tool_results)
        state.design_revision = revision
        self.result = state
        self.draft = state.model_copy(deep=True)
        self.editor_generation += 1
        self.calls.append(AgentCall('EngineerSelection','user_selection',{'revision':revision},state.candidate.copy(),'success'))
        return state

    def downloads(self):
        if self.result is None: return {}
        return {
            'md': markdown_report(self.result,'engiagent_result.json').encode('utf-8'),
            'json': self.result.model_dump_json(indent=2).encode('utf-8'),
            'audit': json.dumps({'calls':[vars(c) for c in self.calls], 'runs':self.audit_runs,
                                 'consultations':self.consultations},ensure_ascii=False,indent=2).encode('utf-8'),
        }

    def configure_preference(self,enabled,source='real'):
        from engi_agent.engineering.preferences import PreferenceStore
        if self.draft is None:raise ValueError('先加载任务')
        r=self.draft.request.model_copy(deep=True)
        r.preference_guidance=enabled
        r.preference_snapshot=PreferenceStore(source).load()[0] if enabled else None
        fresh=prepare(r)
        fresh.cache=self.draft.cache.copy();fresh.revisions=self.draft.revisions.copy()
        fresh.design_revision=self.draft.design_revision
        self.draft=fresh;self.stage='validated' if not fresh.missing_parameters else 'editing'
        self.editor_generation+=1

    def compare_preferences(self,source='real'):
        from engi_agent.engineering.preferences import PreferenceStore,pool,score
        if not self.result or self.result.request.task_type!='new_design':raise ValueError('请先完成新设计')
        snapshot=PreferenceStore(source).load()[0]
        results={}
        for name,enabled in [('off',False),('on',True)]:
            r=self.result.request.model_copy(deep=True)
            r.auto_redesign=True;r.preference_guidance=enabled;r.preference_snapshot=snapshot if enabled else None
            # Independent empty caches and identical confirmed inputs/budgets.
            state=run_engineering(confirm(prepare(r)),ProgramRoles())
            items=pool(state)
            results[name]=dict(state=state.model_dump(),metrics=dict(
                tested=len(state.revisions),passed=sum(h['evaluation']['status']=='pass' for h in state.revisions),
                unique_passed=len(items),best_score=min((score(i,snapshot) for i in items),default=None)))
        self.preference_comparison=dict(source=source,snapshot=snapshot.model_dump(),results=results)
        return self.preference_comparison
