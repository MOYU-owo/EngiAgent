"""Engineer-readable reports projected only from actual confirmed/tool data."""
from pathlib import Path
from uuid import uuid4
from .schema import EngineeringState
from .presentation import (PARAMETER_HEADERS, PHASES, TOOLS, parameter_rows,
                           profile_rows, result_overview, result_view, table, unimplemented_labels, friendly_message)


def markdown_report(state: EngineeringState, json_filename: str | None = None) -> str:
    lines = ["# EngiAgent RC 梁教学试算报告", "", "## 1. 结论与方案", "",
             result_overview(state, markdown=True), "",
             "本报告为教学试算；分项通过不代表中国规范或完整工程合规。",
             "数值按工程阅读精度显示；计算与判定使用未取整的原始数值。", ""]
    if json_filename:
        lines += [f"完整结构化数据与原始计算记录：[下载/查看 JSON]({json_filename})", ""]
    if state.request.task_type == "evaluate_existing":
        lines += ["本任务直接验算确认的已有尺寸及配筋，没有生成新设计方案。", ""]
    elif state.candidate:
        lines += ["方案状态：" + {"checked": "已完成所请求校核", "rejected": "校核未通过",
                  "draft": "候选草案，校核未完成"}.get(state.candidate.get("status"), "待核实"), ""]
    lines += ["## 2. 原始任务", ""]
    if state.request.user_query:
        lines += ["> " + line for line in state.request.user_query.splitlines()] + [""]
    else:
        lines += ["使用结构化任务文件。", ""]
    lines += ["## 3. 参数确认表", "", table(PARAMETER_HEADERS, parameter_rows(state), markdown=True), "",
              "表中“模型提取”表示来源；“已确认”表示用户已批准输入，不是模型保证数值正确。",
              "“输入恒载不含自重”表示程序另行计入梁自重；只有“明确忽略自重”才不计自重。", ""]
    if state.missing_parameters:
        from .presentation import field_label
        lines += ["需要补充：" + "、".join(field_label(k) for k in state.missing_parameters), ""]
    lines += ["## 4. 计算依据与教学假设", "", f"计算配置：{state.profile.version}", "",
              f"来源：{state.profile.source}", "",
              table(["系数/条件", "本次采用值"], profile_rows(state), markdown=True), "",
              "适用范围：简支矩形梁、全跨均布恒活载、单层受拉纵筋；弹性挠度采用毛截面刚度。", ""]
    lines += ["## 5. 执行流程", ""]
    trace_rows = []
    for index, (key, result) in enumerate(state.tool_results.items(), 1):
        phase, _, name = key.partition(".")
        execution = {"success": "执行完成", "failed": "执行失败", "blocked": "上游阻断"}[result.status]
        checked = "通过" if result.outputs.get("pass") is True else "不通过" if result.outputs.get("pass") is False else "—"
        trace_rows.append([str(index), PHASES.get(phase, phase), TOOLS.get(name, name), execution, checked])
    lines += [table(["序号", "阶段", "步骤", "执行状态", "分项检查"], trace_rows, markdown=True)
              if trace_rows else "没有执行工程计算。", "",
              "“执行完成”表示工具正常返回；检查结果另列，不能把工具执行成功理解为验算通过。", ""]
    if state.role_events:
        role_labels = {"Dispatcher": "任务解析", "Design": "设计计划", "Evaluation": "验算计划"}
        roles = [[role_labels.get(e.get("role"), e.get("role", "未知")),
                  "已完成" if e.get("status") == "success" else "失败",
                  "任务文件直接读取" if e.get("mode") == "structured_file" else
                  "中文需求模型提取" if e.get("mode") == "DeepSeek" else "工具计划组织"]
                 for e in state.role_events]
        lines += [table(["角色环节", "状态", "职责"], roles, markdown=True), ""]
    for prefix, heading in (("design", "6. 设计计算过程"), ("evaluation", "7. 独立验算过程")):
        lines += ["## " + heading, ""]
        items = [(key, result) for key, result in state.tool_results.items() if key.startswith(prefix + ".")]
        if not items:
            lines += ["本任务为已有梁独立验算，跳过设计阶段。" if prefix == "design" and
                      state.request.task_type == "evaluate_existing" else
                      "该阶段未执行或未得到结果，不能判断通过。", ""]
        for index, (key, result) in enumerate(items, 1):
            name = key.split(".", 1)[1]
            view = result_view(name, result.outputs, result.status, result.errors, result.warnings)
            lines += [f"### {index}. {view.label} — {view.status}", ""]
            if view.rows:
                lines += [table(["项目", "计算结果"], view.rows, markdown=True), ""]
            lines += ["- " + note for note in view.notes] + [""]
    lines += ["## 8. 未完成项与后续处理", ""]
    lines += ["- " + item for item in unimplemented_labels(state)]
    lines += ["- " + friendly_message(e) for e in state.errors + state.presentation_warnings]
    if state.evaluation.status == "fail":
        lines += ["", "请根据不通过项目调整截面、配筋或约束后重新运行；本轮未自动改设。"]
    if state.evaluation.status == "error":
        lines += ["", "本次执行存在错误，部分结果即使已显示，也不能作为完整通过结论。"]
    lines += ["", "## 9. 计算追溯", "", "以下为技术追溯信息；完整精度输入输出保存在同名 JSON 中。", "",
              "<details>", "<summary>展开公式版本、依据与输入哈希</summary>", ""]
    refs = [[key, result.formula_version, "; ".join(result.code_refs), result.inputs_hash]
            for key, result in state.tool_results.items()]
    lines += [table(["计算步骤", "公式版本", "依据", "输入哈希"], refs, markdown=True), "", "</details>", ""]
    return "\n".join(lines)


def save_reports(state: EngineeringState, directory: str | Path) -> tuple[Path, Path]:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    stem = "beam_" + uuid4().hex[:12]
    md, data = directory / (stem + ".md"), directory / (stem + ".json")
    md.write_text(markdown_report(state, data.name), encoding="utf-8")
    data.write_text(state.model_dump_json(indent=2), encoding="utf-8")
    return md.resolve(), data.resolve()
