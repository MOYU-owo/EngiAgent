"""Three separate model roles. Their prose never supplies engineering results."""
from __future__ import annotations

import json
import re
from typing import Literal, Protocol
from pydantic import Field
from langchain.messages import HumanMessage, SystemMessage
from .cn_schema import Contract, TaskRequest
from .cn_schema import CN_UNITS


class RolePlan(Contract):
    steps: list[str]
    explanation: str = Field(description="仅解释工具顺序，不生成数值或合规结论")


class CandidateDecision(Contract):
    stop: bool = False
    beam_width_mm: float | None = Field(default=None, gt=0)
    beam_depth_mm: float | None = Field(default=None, gt=0)
    bar_diameter_mm: float | None = Field(default=None, gt=0)
    minimum_bar_count: int = Field(default=2, ge=2, le=200, strict=True)
    reason: str = Field(min_length=1, max_length=2000)


class RoleClient(Protocol):
    def parse(self, query: str) -> TaskRequest: ...
    def plan(self, role: Literal["Design", "Evaluation"], payload: dict) -> RolePlan: ...


class DeepSeekRoles:
    supports_candidate_planning = True
    def __init__(self, model=None):
        if model is None:
            from engi_agent.config import Settings
            from langchain_deepseek import ChatDeepSeek
            s = Settings.from_env()
            model = ChatDeepSeek(model=s.model, api_key=s.deepseek_api_key,
                                 temperature=0, max_retries=s.max_retries, timeout=45)
        self.model = model

    def parse(self, query: str) -> TaskRequest:
        # An explicit foreign-code request must never be silently reinterpreted.
        foreign = r'(?:ACI(?![A-Za-z])|Eurocode(?![A-Za-z])|EN\s*199\d|BS\s*8110|美标|欧标|美国规范|欧洲规范)'
        if re.search(r'(?:(?:按照?|采用|使用|依据|执行|遵循)\s*(?:美国\s*)?|\b(?:use|using|per|according to)\s+)' + foreign,
                     query, re.IGNORECASE):
            return TaskRequest(task_type='unsupported', user_query=query,
                               clarification=['仅支持中国规范，不能按指定的其他规范计算。'])
        prompt = (
            "你是工程任务 Dispatcher，仅提取用户明确提供的参数，不计算、不补齐默认值。"
            "仅支持简支矩形RC梁、全跨均布恒活载、单层受拉筋。其他结构/荷载标 unsupported。"
            "task_type: new_design/evaluate_existing/unsupported。本系统仅支持中国规范，code必须为cn-2024。"
            "targets仅允许flexure/shear/detailing/crack/deflection。明确要求其他国家规范的任务标unsupported，不得转成中国规范计算。"
            "中国规范新设计选flexure,shear,detailing,crack,deflection；既有梁按指定目标。"
            "已明确简支/矩形/均布/单层分别提取 support_type=simply_supported, section_type=rectangular,"
            "load_case=full_span_udl, reinforcement_layers=1。不要从未说明的条件推断这些值。"
            "参数值通过 parameters 字典返回，每项含value/unit/source=llm_extracted/confirmed=false。"
            "self_weight_mode: excluded 表示用户恒载不含自重需程序计入，included表示已含，"
            "不支持忽略自重，不得使用ignore。"
            "提取concrete_grade=C30等、steel_grade=HRB400等、stirrup_grade=HRB400等，不提取fc_mpa/fy_mpa/elastic_modulus_mpa。"
            "中国规范参数名称见后附CN字段；重要性、安全等级、环境、寿命、活载系数和构造输入均仅按用户明确说明提取。"
            "一类环境environment_class=I，安全等级二级safety_class=2（数值，不填汉字）。每侧腰筋根数独立于上下纵筋。"
            "已给设计弯矩用design_moment_kn_m，单位kN·m。新设计不需要用户提供bar_count或stirrup_spacing_mm，不把它们列为缺项。"
            "明确给出的梁宽、梁高必须分别提取beam_width_mm、beam_depth_mm，给出即固定；未给出的尺寸省略，允许程序有限搜索。"
            "最大梁宽/高仅提取max_width_mm/max_depth_mm，不得将其当固定尺寸。"
            "提取搜索要求到顶层search_diameters_mm（仅明确许可的直径）、solution_count（最多展示1至3项）、max_iterations（总尝试1至40轮）。"
            "挠度限值L/250提取deflection_limit_ratio=250（仅数值分母，unit=null）。"
            "纵筋、箍筋牌号分别有用户依据；箍筋肢数也必须提取。"
            "单位保留已知原单位，支持mm,m,cm,kN/m,N/mm,N/m,kN/m3,N/m3,kN·m,kN*m,N·mm,kN,N。"
            "无量纲和枚举unit=null。缺失字段留空并列入clarification；禁止补造。"
            f"中国规范字段及单位：{json.dumps(CN_UNITS, ensure_ascii=False)}"
        )
        response = self.model.with_structured_output(TaskRequest, method="function_calling").invoke(
            [SystemMessage(content=prompt), HumanMessage(content=query)])
        result = TaskRequest.model_validate(response)
        if result.task_type == 'new_design':
            result.auto_redesign = not any(text in query for text in ('关闭自动改设','不自动改设','关闭自动优化'))
        result.user_query = query
        for item in result.parameters.values():
            item.source, item.confirmed = "llm_extracted", False
        return result

    def plan(self, role: Literal["Design", "Evaluation"], payload: dict) -> RolePlan:
        response = self.model.with_structured_output(RolePlan, method="function_calling").invoke([
            SystemMessage(content=f"你是{role} Agent。根据已确认的工程参数组织下列允许工具。"
                          "这是规则约束工作流，必须原样返回 required_steps 的顺序，不增删工具。"
                          "explanation只解释职责和工具衔接，不计算数值、不判断合规；所有数据以Python工具为准。"),
            HumanMessage(content=json.dumps(payload, ensure_ascii=False))])
        return RolePlan.model_validate(response)

    def choose_candidate(self, payload: dict) -> CandidateDecision:
        response = self.model.with_structured_output(CandidateDecision, method='function_calling').invoke([
            SystemMessage(content=(
                '你是Design Agent，负责根据真实验算反馈自主决定下一轮截面与配筋探索方向。'
                '你可以调整允许变化的梁宽、梁高、纵筋直径及最少根数，或说明停止原因。'
                '不必遵循固定的加高/加筋顺序；结合失败的具体原因、历史结果、剩余预算和工程师偏好作出取舍。'
                '固定尺寸不得改变；自由尺寸只能取domain内以initial_mm为起点的step_mm离散值。'
                '纵筋直径只能从allowed_diameters中选择；未填的尺寸/直径保持当前值。'
                'minimum_bar_count是交给设计工具的最少根数，实际根数仍由工具计算，不等于最终配筋。'
                '不得重复tried中的参数与最少根数组合，不得修改荷载、材料、限值或其他已确认构造输入。'
                'preference若非空，其非负权重依次对应梁高/1000、受拉纵筋面积/1000、控制利用率，成本越低越好；'
                '它只是取舍倾向，不得用来放宽验算要求。未验算方案的利用率未知，不得编造。'
                'reason用简洁中文说明：问题在哪里、为什么改这些参数、预计权衡是什么；不能保证未验算方案通过。'
                '若已有方案通过，可继续寻找有不同取舍的方案；确无值得尝试的合法修改时stop=true并说明。')),
            HumanMessage(content=json.dumps(payload,ensure_ascii=False))])
        return CandidateDecision.model_validate(response)


class ProgramRoles:
    """Production deterministic plan adapter; requires an already structured request."""
    def parse(self, query):
        raise ValueError('程序角色不解析自然语言，请使用Dispatcher或结构化文件')

    def plan(self, role, payload):
        return RolePlan(steps=payload['required_steps'],explanation=f'工程DAG确定性执行 {role}')


class FixtureRoles:
    """Explicit offline fixture, not a natural-language parser substitute."""
    def __init__(self, request: TaskRequest):
        self.request = request

    def parse(self, query: str) -> TaskRequest:
        return self.request.model_copy(deep=True, update={"user_query": query})

    def plan(self, role, payload):
        return RolePlan(steps=payload["required_steps"], explanation=f"离线固定测试角色 {role}")
