"""Typed engineering state carried by LangGraph, separate design/evaluation subgraphs."""
from __future__ import annotations

import hashlib
import json
from typing import TypedDict, Callable
from langgraph.graph import StateGraph, START, END
from .roles import RoleClient
from .schema import (BeamParameters, EngineeringState, EvaluationResult, TaskRequest,
                     TeachingProfile, ProgressEvent, missing_fields, normalize, parameter_python)
from .tools import execute_tool

COMMON = ["section_sizing", "section_geometry", "load_combination", "beam_analysis"]
DESIGN = COMMON + ["flexural_design", "shear_design"]
ProgressCallback = Callable[[ProgressEvent], None]


def emit_progress(state: EngineeringState, callback: ProgressCallback | None, event: ProgressEvent):
    state.progress_events.append(event.model_copy(deep=True))
    if callback:
        try:
            callback(event.model_copy(deep=True))
        except Exception:
            warning = "进度显示失败；计算记录仍已保存，请查看最终报告。"
            if warning not in state.presentation_warnings:
                state.presentation_warnings.append(warning)


class GraphState(TypedDict):
    state: EngineeringState


def values(state: EngineeringState) -> dict:
    return {k: parameter_python(k, v) for k, v in state.request.parameters.items()}


def stamp(state: EngineeringState) -> str:
    payload = {"request": state.request.model_dump(), "profile": state.profile.model_dump()}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, allow_nan=False).encode()).hexdigest()


def prepare(request: TaskRequest, profile: TeachingProfile | None = None) -> EngineeringState:
    # A non-supported request is never forced through the beam schema.
    if request.task_type == "unsupported":
        return EngineeringState(request=request, errors=["不支持的结构或任务"])
    request = normalize(request)
    if request.task_type == "new_design":
        request.targets = ["flexure", "shear", "elastic_deflection"]
    return EngineeringState(request=request, profile=profile or TeachingProfile(),
                            missing_parameters=missing_fields(request))


def confirm(state: EngineeringState) -> EngineeringState:
    state = prepare(state.request, state.profile)
    if state.errors or state.missing_parameters:
        raise ValueError("无法确认：" + ", ".join(state.errors + state.missing_parameters))
    # Construction validates cross-field numeric types before any role/tool runs.
    BeamParameters.model_validate(values(state))
    for item in state.request.parameters.values():
        item.confirmed = True
    state.confirmed = True
    state.confirmation_hash = stamp(state)
    return state


def evaluation_steps(state: EngineeringState) -> list[str]:
    steps = COMMON.copy()
    if "flexure" in state.request.targets:
        steps += ["flexural_check", "detailing_check"]
    if "shear" in state.request.targets:
        steps.append("shear_check")
    if "elastic_deflection" in state.request.targets:
        steps.append("elastic_deflection")
    return steps


def error_state(state: EngineeringState, message: str) -> EngineeringState:
    state.errors.append(message)
    state.evaluation.status = "error"
    return state


def invoke_role(state: EngineeringState, roles: RoleClient, name: str, steps: list[str], on_event=None) -> bool:
    phase = "design" if name == "Design" else "evaluation"
    emit_progress(state, on_event, ProgressEvent(phase=phase, kind="planning", name=name,
                                                status="running", total_steps=len(steps)))
    try:
        decision = roles.plan(name, {"required_steps": steps, "parameters": values(state),
                                     "candidate": state.candidate, "profile": state.profile.model_dump()})
        # Validate fake/custom provider responses, not just hosted model output.
        from .roles import RolePlan
        decision = RolePlan.model_validate(decision)
        if decision.steps != steps:
            raise ValueError("模型工具计划违反顺序或白名单")
        state.role_events.append({"role": name, "status": "success", "steps": steps})
        emit_progress(state, on_event, ProgressEvent(phase=phase, kind="planning", name=name,
                                                    status="success", total_steps=len(steps)))
        return True
    except Exception as exc:
        state.role_events.append({"role": name, "status": "error"})
        error_state(state, f"{name} 模型调用或结构化输出失败（{type(exc).__name__}）")
        emit_progress(state, on_event, ProgressEvent(phase=phase, kind="planning", name=name,
                                                    status="failed", total_steps=len(steps)))
        return False


def run_steps(state: EngineeringState, p: BeamParameters, steps: list[str], prefix: str, on_event=None) -> bool:
    outputs = {}
    for index, name in enumerate(steps):
        key = f"{prefix}.{name}"
        state.execution_plan.append(key)
        emit_progress(state, on_event, ProgressEvent(phase=prefix, kind="tool", name=name, status="running",
                                                    step=index + 1, total_steps=len(steps)))
        result = execute_tool(name, p, state.profile, outputs)
        state.tool_results[key] = result
        emit_progress(state, on_event, ProgressEvent(phase=prefix, kind="tool", name=name, status=result.status,
                                                    step=index + 1, total_steps=len(steps), outputs=result.outputs,
                                                    errors=result.errors, warnings=result.warnings))
        if result.status != "success":
            state.errors += [f"{key}: {e}" for e in result.errors]
            state.evaluation.status = "fail" if result.outputs.get("engineering_failure") else "error"
            # Record explicitly blocked descendants, without invoking their code.
            from .schema import ToolResult
            for position, remaining in enumerate(steps[index + 1:], index + 2):
                blocked = f"{prefix}.{remaining}"
                state.execution_plan.append(blocked)
                state.tool_results[blocked] = ToolResult(tool=remaining, status="blocked", inputs_hash=result.inputs_hash,
                                                        inputs={}, errors=[f"上游 {name} 失败"])
                emit_progress(state, on_event, ProgressEvent(phase=prefix, kind="tool", name=remaining,
                                                            status="blocked", step=position, total_steps=len(steps),
                                                            errors=[f"上游 {name} 失败"]))
            return False
        outputs[name] = result.outputs
    return True


def build_engineering_graph(roles: RoleClient, on_event: ProgressCallback | None = None):
    def design_node(data: GraphState):
        state = data["state"]
        if invoke_role(state, roles, "Design", DESIGN, on_event):
            p = BeamParameters.model_validate(values(state))
            if run_steps(state, p, DESIGN, "design", on_event):
                flex = state.tool_results["design.flexural_design"].outputs
                shear = state.tool_results["design.shear_design"].outputs
                section = state.tool_results["design.section_sizing"].outputs
                state.candidate = {"beam_width_mm": section["beam_width_mm"],
                                   "beam_depth_mm": section["beam_depth_mm"],
                                   "bar_count": flex["bar_count"], "As_mm2": flex["As_mm2"],
                                   "stirrup_spacing_mm": shear["stirrup_spacing_mm"],
                                   "status": "draft"}
        return {"state": state}

    def evaluation_node(data: GraphState):
        state = data["state"]
        if state.evaluation.status in ("error", "fail"):
            return {"state": state}
        steps = evaluation_steps(state)
        if not invoke_role(state, roles, "Evaluation", steps, on_event):
            return {"state": state}
        supplied = values(state)
        if state.candidate:
            supplied.update({k: v for k, v in state.candidate.items()
                             if k in BeamParameters.model_fields})
        p = BeamParameters.model_validate(supplied)
        # Evaluation recomputes all required quantities from actual geometry and
        # reinforcement, deliberately not consuming Design's capacity/pass values.
        if run_steps(state, p, steps, "evaluation", on_event):
            checks = {name: state.tool_results[f"evaluation.{name}"].outputs["pass"]
                      for name in steps if "pass" in state.tool_results[f"evaluation.{name}"].outputs}
            state.evaluation = EvaluationResult(status="pass" if all(checks.values()) else "fail", checks=checks)
            omitted = {"flexure", "shear", "elastic_deflection"} - set(state.request.targets)
            state.evaluation.unimplemented += [f"本次未请求：{target}" for target in sorted(omitted)]
            if state.candidate:
                state.candidate["status"] = "checked" if state.evaluation.status == "pass" else "rejected"
        return {"state": state}

    def subgraph(name, function):
        graph = StateGraph(GraphState)
        graph.add_node(name, function)
        graph.add_edge(START, name)
        graph.add_edge(name, END)
        return graph.compile()

    graph = StateGraph(GraphState)
    graph.add_node("design", subgraph("design_tools", design_node))
    graph.add_node("evaluation", subgraph("evaluation_tools", evaluation_node))
    graph.add_conditional_edges(START, lambda data: "design" if data["state"].request.task_type == "new_design" else "evaluation")
    graph.add_edge("design", "evaluation")
    graph.add_edge("evaluation", END)
    return graph.compile()


def run_engineering(state: EngineeringState, roles: RoleClient,
                    on_event: ProgressCallback | None = None) -> EngineeringState:
    state = state.model_copy(deep=True)
    if state.request.task_type == "unsupported":
        state.evaluation.status = "incomplete"
        return state
    if (not state.confirmed or not all(p.confirmed for p in state.request.parameters.values())
            or state.confirmation_hash != stamp(state)):
        return error_state(state, "参数/假设未确认或确认后已被修改，拒绝计算")
    if state.tool_results:
        return error_state(state, "首轮不支持对已执行状态重算，请重新准备并确认任务")
    try:
        return build_engineering_graph(roles, on_event).invoke({"state": state})["state"]
    except Exception as exc:
        return error_state(state, f"工作流异常（{type(exc).__name__}），未形成通过结论")
