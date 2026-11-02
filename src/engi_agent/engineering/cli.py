"""Chinese CLI with an explicit, editable confirmation boundary."""
import argparse
import json
import shlex
from pathlib import Path
from .roles import DeepSeekRoles, FixtureRoles
from .cn_schema import ParameterValue, TaskRequest, CN_UNITS
from .cn_workflow import confirm, prepare, run_engineering, normalize
from .cn_presentation import (confirmation_text, overview, save_reports,
                              FIELD_ALIASES, ENUM_INPUTS, parameter_keys, progress_text)


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
        units_map = CN_UNITS
        if key not in units_map:
            raise ValueError("没有这个参数，请使用确认表中的中文名称或编号")
        unit = units[0] if units else None
        if units_map[key] and not unit:
            raise ValueError("数值参数请注明单位，例如：修改 跨度 6 m")
        aliases = {"毫米": "mm", "米": "m", "厘米": "cm", "千牛/米": "kN/m", "毫米²": "mm2",
                   "mm²": "mm2", "kN/m³": "kN/m3", "千牛/立方米": "kN/m3"}
        unit = aliases.get(unit, unit)
        value = ENUM_INPUTS.get(value, value)
        if key not in {"support_type", "load_case", "section_type", "self_weight_mode", "concrete_grade", "steel_grade", "stirrup_grade", "environment_class"}:
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
    normalize(TaskRequest(code=request.code, task_type=request.task_type, targets=request.targets, parameters={key: item}))
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
    parser = argparse.ArgumentParser(description="EngiAgent 中国规范 RC 梁设计与验算")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--request", type=Path, help="结构化任务 JSON")
    group.add_argument("--query", help="由真实 Dispatcher 提取的中文任务")
    parser.add_argument("--offline", action="store_true", help="只允许文件任务；使用固定测试角色，不接真实模型")
    parser.add_argument("--approve", action="store_true", help="显式确认文件中的全部参数及屏幕展示的规范参数与假设，供可复现批量运行")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument('--code', choices=['cn-2024'], help='仅支持cn-2024；省略时亦采用中国规范')
    parser.add_argument('--auto-redesign', action='store_true', help='中国规范新设计开启有限改设')
    parser.add_argument('--max-iterations', type=int, default=None)
    parser.add_argument('--session', action='store_true', help='中国规范模式计算后在当前进程继续修改参数')
    parser.add_argument('--base-request', type=Path, help='自然语言输入采用的显式参数模板；全部模板值仍需确认')
    args = parser.parse_args(argv)
    if args.offline and not args.request:
        parser.error("--offline 必须配合 --request；离线模式不宣称支持自然语言识别")
    if args.base_request and not args.query:
        parser.error('--base-request须与--query一起使用')
    try:
        if args.request:
            print("[任务解析] 正在读取参数文件…", flush=True)
            request = TaskRequest.model_validate_json(args.request.read_text(encoding="utf-8"))
            roles = FixtureRoles(request) if args.offline else DeepSeekRoles()
            dispatcher_mode = "structured_file"
        else:
            print("[任务解析] 正在调用 DeepSeek 提取参数，请稍候…", flush=True)
            roles = DeepSeekRoles()
            base_request=TaskRequest.model_validate_json(args.base_request.read_text(encoding='utf-8')) if args.base_request else None
            query = '按中国规范cn-2024提取任务。'+args.query
            request = TaskRequest.model_validate(roles.parse(query))
            if base_request:
                inherited={k:v.model_copy(deep=True) for k,v in base_request.parameters.items()}
                for v in inherited.values(): v.source='template'; v.confirmed=False
                request.parameters={**inherited,**request.parameters}
                print('采用显式参数模板：'+str(args.base_request)+'；请在确认表检查全部采用值。',flush=True)
            dispatcher_mode = "DeepSeek"
        print("[任务解析] 已完成，进入参数确认。", flush=True)
        if args.auto_redesign: request.auto_redesign=True
        if args.max_iterations is not None: request.max_iterations=args.max_iterations
        request=TaskRequest.model_validate(request.model_dump())
        if request.task_type == "unsupported":
            state = prepare(request)
        elif args.approve:
            state = prepare(request)
            print(confirmation_text(state))
            print("已通过 --approve 显式批量确认参数与规范假设。", flush=True)
            state = confirm(state)
        else:
            state = interactive_confirm(request)
            if state is None:
                print("已取消，未执行计算。")
                return 0
        state.role_events.append({"role": "Dispatcher", "status": "success", "mode": dispatcher_mode})
        return run_cn_session(state, roles, args)
    except (KeyboardInterrupt, EOFError):
        print("已取消，未形成通过结论。")
        return 2
    except Exception as exc:
        # Provider text can contain private request headers.
        print(f"任务失败（{type(exc).__name__}）；未形成通过结论。请检查参数、网络或模型配置。")
        if not args.query:
            from pydantic import ValidationError
            if isinstance(exc, (ValidationError, ValueError)):
                print(str(exc))
        return 2


def run_cn_session(state, roles, args):
    from .cn_workflow import revise
    def progress(event):
        print(progress_text(event), flush=True)
    while True:
        state=run_engineering(state,roles,on_event=progress)
        md,data=save_reports(state,args.output_dir)
        print('\n'+overview(state)); print(f'报告：{md}\nJSON：{data}',flush=True)
        if state.errors: print('\n'.join(state.errors))
        if not args.session: return 0 if state.evaluation.status=='pass' else 2
        while True:
            answer=input('继续修改，例如“修改 梁高 600 mm”；输入quit结束：').strip()
            if answer.lower() in ('quit','exit'): return 0 if state.evaluation.status=='pass' else 2
            try:
                changed=edit_parameter(state.request,answer,state)
                edits={k:v for k,v in changed.parameters.items() if v != state.request.parameters.get(k)}
                pending=revise(state,edits)
                approved=interactive_confirm_state(pending)
                if approved is None: return 0
                state=approved
                break
            except ValueError as exc:
                print('修改未执行：'+str(exc))


def interactive_confirm_state(state):
    """Preserve the cache/history while the original confirmation editor is used."""
    approved=interactive_confirm(state.request)
    if approved is None: return None
    approved.cache=state.cache
    approved.revisions=state.revisions
    approved.design_revision=state.design_revision
    approved.revision_reason=state.revision_reason
    return approved
