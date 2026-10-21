"""Chinese CLI with an explicit, editable confirmation boundary."""
import argparse
import json
import shlex
from pathlib import Path
from .roles import DeepSeekRoles, FixtureRoles
from .schema import ParameterValue, TaskRequest, normalize, UNITS
from .workflow import confirm, prepare, run_engineering
from .reporting import save_reports
from .presentation import (PARAMETER_HEADERS, FIELD_ALIASES, ENUM_INPUTS, TARGETS,
                           parameter_keys, parameter_rows, profile_rows, table, field_label,
                           progress_text, result_overview, unimplemented_labels, friendly_message)


def confirmation_text(state):
    task = "新梁设计" if state.request.task_type == "new_design" else "已有梁独立验算"
    lines = ["\n=== 计算前参数确认 ===", f"任务：{task}；目标：" + "、".join(TARGETS[t] for t in state.request.targets),
             table(PARAMETER_HEADERS, parameter_rows(state)), "", "教学系数与假设（确认时一并批准）：",
             table(["系数/条件", "采用值"], profile_rows(state)), "来源：" + state.profile.source,
             "中国规范核验：未完成；不含开裂/长期挠度、裂缝、锚固搭接、耐久性和完整构造。",
             "显示值经过取整；计算和校核使用完整精度。"]
    if state.request.clarification:
        lines.append("解析阶段提示（以当前缺失项为准）：" + "; ".join(state.request.clarification))
    if state.missing_parameters:
        lines.append("缺失参数，需补充：" + "、".join(field_label(k) for k in state.missing_parameters))
    if state.errors:
        lines.append("错误：" + "; ".join(state.errors))
    return "\n".join(lines)


def edit_parameter(request, answer, state=None):
    """Chinese/numbered shorthand, plus the previous JSON edit syntax."""
    if answer.startswith("修改 "):
        parts = shlex.split(answer)
        if len(parts) not in (3, 4):
            raise ValueError("格式示例：修改 跨度 6 m；修改 纵筋根数 3")
        _, name, value, *units = parts
        if name.isdigit():
            keys = parameter_keys(state or prepare(request))
            if not 1 <= int(name) <= len(keys):
                raise ValueError("参数编号超出表格范围")
            key = keys[int(name) - 1]
        else:
            key = FIELD_ALIASES.get(name, name)
        if key not in UNITS:
            raise ValueError("没有这个参数，请使用确认表中的中文名称或编号")
        unit = units[0] if units else None
        if UNITS[key] and not unit:
            raise ValueError("数值参数请注明单位，例如：修改 跨度 6 m")
        aliases = {"毫米": "mm", "米": "m", "厘米": "cm", "千牛/米": "kN/m", "毫米²": "mm2",
                   "mm²": "mm2", "kN/m³": "kN/m3", "千牛/立方米": "kN/m3"}
        unit = aliases.get(unit, unit)
        value = ENUM_INPUTS.get(value, value)
        if key not in {"support_type", "load_case", "section_type", "self_weight_mode"}:
            value = float(value)
        item = ParameterValue(value=value, unit=unit)
    else:
        key, raw = answer.split("=", 1)
        key = FIELD_ALIASES.get(key.strip(), key.strip())
        item = ParameterValue.model_validate(json.loads(raw))
    item.source, item.confirmed = "user", False
    item.raw_value, item.raw_unit = None, None
    # Validate the edit alone, so several invalid original fields can be repaired
    # one by one instead of rejecting each edit because of another bad field.
    normalize(TaskRequest(task_type=request.task_type, targets=request.targets, parameters={key: item}))
    candidate = request.model_copy(deep=True)
    candidate.parameters[key] = item
    return candidate


def interactive_confirm(request, input_fn=input, output_fn=print):
    while True:
        try:
            state = prepare(request)
            output_fn(confirmation_text(state))
        except Exception as exc:
            output_fn(f"参数校验失败：{exc}")
            state = None
        answer = input_fn('输入“确认”开始；修改示例：修改 跨度 6 m / 修改 梁高 600 mm；输入 quit 取消：').strip()
        if answer.lower() in ("quit", "exit"):
            return None
        if answer in ("确认", "yes"):
            if state is None:
                output_fn("请先修正参数")
                continue
            try:
                return confirm(state)
            except ValueError as exc:
                output_fn("仍有参数缺失或无效，请先补充并修正。")
                continue
        try:
            request = edit_parameter(request, answer, state)
        except Exception as exc:
            output_fn(f"修改失败：{exc}")


def main(argv=None) -> int:
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="EngiAgent RC 梁教学试算")
    parser.add_argument("--engineering", action="store_true")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--request", type=Path, help="结构化任务 JSON")
    group.add_argument("--query", help="由真实 Dispatcher 提取的中文任务")
    parser.add_argument("--offline", action="store_true", help="只允许文件任务；使用固定测试角色，不接真实模型")
    parser.add_argument("--approve", action="store_true", help="显式确认文件中的全部参数及屏幕展示的教学假设，供可复现批量运行")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    args = parser.parse_args(argv)
    if args.offline and not args.request:
        parser.error("--offline 必须配合 --request；离线模式不宣称支持自然语言识别")
    try:
        if args.request:
            print("[任务解析] 正在读取参数文件…", flush=True)
            request = TaskRequest.model_validate_json(args.request.read_text(encoding="utf-8"))
            roles = FixtureRoles(request) if args.offline else DeepSeekRoles()
            dispatcher_mode = "structured_file"
        else:
            print("[任务解析] 正在调用 DeepSeek 提取参数，请稍候…", flush=True)
            roles = DeepSeekRoles()
            request = TaskRequest.model_validate(roles.parse(args.query))
            dispatcher_mode = "DeepSeek"
        print("[任务解析] 已完成，进入参数确认。", flush=True)
        if request.task_type == "unsupported":
            state = prepare(request)
        elif args.approve:
            state = prepare(request)
            print(confirmation_text(state))
            print("已通过 --approve 显式批量确认参数与教学假设。", flush=True)
            state = confirm(state)
        else:
            state = interactive_confirm(request)
            if state is None:
                print("已取消，未执行计算。")
                return 0
        state.role_events.append({"role": "Dispatcher", "status": "success", "mode": dispatcher_mode})
        state = run_engineering(state, roles, on_event=lambda event: print(progress_text(event), flush=True))
        md, data = save_reports(state, args.output_dir)
        print("\n=== 结果总览 ===\n" + result_overview(state))
        if state.errors:
            print("错误/停止原因：\n" + "\n".join(friendly_message(e) for e in state.errors))
        if state.evaluation.status == "fail":
            print("请按不通过项目调整后重新运行；本次未自动改设。")
        print("尚未完成：" + "、".join(unimplemented_labels(state)))
        print(f"\n中文计算报告（优先阅读）：{md}\n完整精度数据（用于追溯）：{data}")
        return 0 if state.evaluation.status == "pass" else 2
    except (KeyboardInterrupt, EOFError):
        print("已取消，未形成通过结论。")
        return 2
    except Exception as exc:
        # Do not echo provider exception text, which can contain request headers.
        print(f"任务失败（{type(exc).__name__}）；未形成通过结论。请检查参数、网络或模型配置。")
        if not args.query:
            from pydantic import ValidationError
            if isinstance(exc, (ValidationError, ValueError)):
                print(str(exc))
        return 2
