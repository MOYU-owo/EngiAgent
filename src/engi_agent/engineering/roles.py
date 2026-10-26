"""Three separate model roles. Their prose never supplies engineering results."""
from __future__ import annotations

import json
from typing import Literal, Protocol
from pydantic import Field
from langchain.messages import HumanMessage, SystemMessage
from .schema import Contract, TaskRequest, UNITS


class RolePlan(Contract):
    steps: list[str]
    explanation: str = Field(description="仅解释工具顺序，不生成数值或合规结论")


class RoleClient(Protocol):
    def parse(self, query: str) -> TaskRequest: ...
    def plan(self, role: Literal["Design", "Evaluation"], payload: dict) -> RolePlan: ...


class DeepSeekRoles:
    def __init__(self, model=None):
        if model is None:
            from engi_agent.config import Settings
            from langchain_deepseek import ChatDeepSeek
            s = Settings.from_env()
            model = ChatDeepSeek(model=s.model, api_key=s.deepseek_api_key,
                                 temperature=0, max_retries=s.max_retries, timeout=45)
        self.model = model

    def parse(self, query: str) -> TaskRequest:
        prompt = (
            "你是工程任务 Dispatcher，仅提取用户明确提供的参数，不计算、不补齐默认值。"
            "仅支持简支矩形RC梁、全跨均布恒活载、单层受拉筋。其他结构/荷载标 unsupported。"
            "task_type: new_design/evaluate_existing/unsupported。先识别规范体系：用户要求中国规范时code=cn-2024，否则code=teaching。"
            "teaching的targets为flexure/shear/elastic_deflection；cn-2024为flexure/shear/detailing/crack/deflection。"
            "中国规范新设计选flexure,shear,detailing,crack,deflection；既有梁按指定目标。"
            "已明确简支/矩形/均布/单层分别提取 support_type=simply_supported, section_type=rectangular,"
            "load_case=full_span_udl, reinforcement_layers=1。不要从未说明的条件推断这些值。"
            "参数值通过 parameters 字典返回，每项含value/unit/source=llm_extracted/confirmed=false。"
            "self_weight_mode: excluded 表示用户恒载不含自重需程序计入，included表示已含，"
            "ignore只在用户明确要求忽略时使用。fc_mpa是圆柱抗压强度，不转换中国混凝土等级。"
            "cn-2024改提取concrete_grade=C30等、steel_grade=HRB400等、stirrup_grade=HRB400等，不提取fc_mpa/fy_mpa/elastic_modulus_mpa。"
            "中国规范参数名称见后附CN字段；重要性、安全等级、环境、寿命、活载系数和构造输入均仅按用户明确说明提取。"
            "一类环境environment_class=I，安全等级二级safety_class=2（数值，不填汉字）。每侧腰筋根数独立于上下纵筋。"
            "已给设计弯矩用design_moment_kn_m，单位kN·m。新设计不需要用户提供bar_count或stirrup_spacing_mm，不把它们列为缺项。"
            "fy与stirrup_fy必须分别有用户依据；箍筋肢数也必须提取。"
            "单位保留已知原单位，用mm,m,in,ft,mm2,in2,MPa,GPa,psi,ksi,kN/m,kip/ft,kN/m3,lb/ft3。"
            "无量纲和枚举unit=null。缺失字段留空并列入clarification；禁止补造。"
            f"教学字段名及单位：{json.dumps(UNITS, ensure_ascii=False)}"
        )
        from .cn_schema import CN_UNITS
        prompt += '中国规范字段及单位：'+json.dumps(CN_UNITS,ensure_ascii=False)
        response = self.model.with_structured_output(TaskRequest, method="function_calling").invoke(
            [SystemMessage(content=prompt), HumanMessage(content=query)])
        result = TaskRequest.model_validate(response)
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


class FixtureRoles:
    """Explicit offline fixture, not a natural-language parser substitute."""
    def __init__(self, request: TaskRequest):
        self.request = request

    def parse(self, query: str) -> TaskRequest:
        return self.request.model_copy(deep=True, update={"user_query": query})

    def plan(self, role, payload):
        return RolePlan(steps=payload["required_steps"], explanation=f"离线固定测试角色 {role}")
