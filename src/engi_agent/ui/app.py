"""Streamlit workbench. All computation is dispatched through service.py."""
from __future__ import annotations
import html
import json
import streamlit as st
import pandas as pd

from engi_agent.engineering.schema import TaskRequest, EngineeringState, parameter_python
from engi_agent.engineering.cn_workflow import ALL_TARGETS
from engi_agent.engineering.dependency_graph import TARGET_TOOLS, SPECS
from engi_agent.engineering.cn_presentation import OUTPUTS
from engi_agent.engineering.presentation import number
from .service import WorkbenchSession, CASES, ROOT, load_case
from .projections import (STAGES, VERDICTS, ACTIONS, TOOL_STATUS, GROUPS, LABELS,
                          editor_rows, audit_rows, result_rows, snapshot, dag_nodes, revision_comparison, output_rows,input_rows)
from .diagrams import beam_svg, dag_dot, agent_dot
from .formulas import FORMULAS, NOTES

PAGES=['设计工作台','计算与规范复核','Agent 与动态规划','对照实验']
CSS='''
<style>
.stApp {font-family: "Segoe UI", "Microsoft YaHei", sans-serif;}
.block-container {max-width:1800px; padding:1.6rem 2.2rem 3rem;}
[data-testid="stSidebar"] {min-width:210px;max-width:210px;border-right:1px solid #dce3ec;}
[data-testid="stSidebar"] > div:first-child {padding-top:1.5rem;}
[data-testid="stHeader"] {background:transparent;}
h1 {font-size:1.65rem!important;font-weight:650!important;letter-spacing:-.025em;}
h2 {font-size:1.22rem!important;font-weight:620!important;}
h3 {font-size:1rem!important;font-weight:620!important;}
[data-testid="stMetricLabel"] {font-size:.78rem;color:#607087;}
[data-testid="stMetricValue"] {font-size:1.6rem;font-variant-numeric:tabular-nums;}
[data-testid="stVerticalBlockBorderWrapper"] > div {border-color:#dce3ec!important;border-radius:7px!important;}
[data-testid="stVerticalBlockBorderWrapper"] {background:#fff;border-radius:7px;}
div[class*="st-key-card_"] {background:#fff;border-radius:7px;}
[data-testid="stExpander"] {background:#fff;border-radius:7px;}
[data-testid="stSidebarUserContent"] {padding-top:2rem;}
[data-testid="stSidebar"] [role="radiogroup"] {gap:5px;}
button, input, textarea {font-family:inherit!important;}
button[kind="primary"] {font-weight:600;}
.brand {font-size:23px;font-weight:700;color:#173e73;letter-spacing:-.035em;}
.eyebrow {font-size:10px;letter-spacing:.14em;color:#74869b;font-weight:650;text-transform:uppercase;}
.meta {color:#607087;font-size:12px;line-height:1.8;}
.pill {display:inline-block;padding:4px 11px;border:1px solid #cad7e7;border-radius:4px;background:#eaf0f8;color:#173e73;font-size:12px;font-weight:600;}
.pill.warn {background:#faf1df;border-color:#e5d2ab;color:#84611f;}
.pill.fail {background:#faeae8;border-color:#e6c1bd;color:#9e4039;}
.pill.pass {background:#eaf4ed;border-color:#c6ddcc;color:#346548;}
.section-title {font-size:11px;letter-spacing:.1em;color:#607087;font-weight:650;margin:0 0 12px;}
[data-testid="stDataFrame"] {font-variant-numeric:tabular-nums;}
[data-testid="stCaptionContainer"] {color:#607087;}
.step-strip {font-size:12px;color:#6d7e92;border-bottom:1px solid #dce3ec;padding:0 0 14px;margin-bottom:12px;}
@media (max-width:1400px) {.block-container {padding-left:1.3rem;padding-right:1.3rem;}}
</style>
'''


def current():
    if 'workbench' not in st.session_state: st.session_state.workbench=WorkbenchSession()
    elif type(st.session_state.workbench) is not WorkbenchSession:
        # Source updates can replace Python classes while Streamlit keeps old
        # objects. Rehydrate evidence and require validation again; never rerun.
        previous=st.session_state.workbench
        restored=WorkbenchSession()
        for key in vars(restored):
            if hasattr(previous,key):setattr(restored,key,getattr(previous,key))
        for key in ('draft','result'):
            value=getattr(restored,key)
            if value is not None:setattr(restored,key,EngineeringState.model_validate_json(value.model_dump_json()))
        restored.mark_dirty()
        restored.errors=['界面源码已更新，请重新校验并确认参数；历史结果仍保留，未重新发起模型请求。']
        st.session_state.workbench=restored
    return st.session_state.workbench


def notice(ctl):
    for error in ctl.errors:st.error(error)
    if ctl.draft and ctl.draft.missing_parameters:
        from .projections import label
        st.warning('需要补充：'+'、'.join(label(k) for k in ctl.draft.missing_parameters))


def header(ctl):
    left,right=st.columns([3,2],vertical_alignment='center')
    with left:
        st.markdown('<div class="eyebrow">STRUCTURAL ENGINEERING · HUMAN IN THE LOOP</div>',unsafe_allow_html=True)
        st.title(st.session_state.get('nav',PAGES[0]))
    with right:
        state=ctl.draft
        status=VERDICTS[ctl.result.evaluation.status] if ctl.stage=='completed' and ctl.result else STAGES[ctl.stage]
        css='pass' if ctl.stage=='completed' and ctl.result.evaluation.status=='pass' else 'fail' if ctl.stage=='error' or ctl.stage=='completed' and ctl.result.evaluation.status in ('fail','error') else 'warn' if ctl.stage in ('editing','validated') else ''
        st.markdown(f'<div style="text-align:right"><span class="pill {css}">{html.escape(status)}</span><div class="meta">'
                    +html.escape(ctl.case_name)+' · '+(f'修订 {state.design_revision}' if state else '未加载')
                    +'<br>'+html.escape(state.profile.version if state else 'CN · 待加载计算配置')+'</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="step-strip">01 需求与参数　→　02 工程师确认　→　03 设计与独立验算　→　04 复核与修订</div>',unsafe_allow_html=True)


def sidebar(ctl):
    with st.sidebar:
        st.markdown('<div class="brand">EngiAgent<span style="color:#8da7c5">.</span></div><div class="eyebrow">RC BEAM WORKBENCH</div>',unsafe_allow_html=True)
        st.write('')
        st.radio('工作区',PAGES,key='nav',label_visibility='collapsed')
        st.divider()
        st.radio('执行模式',['离线 · 确定性角色','DeepSeek · 真实模型'],key='execution_mode',on_change=ctl.mark_dirty)
        st.caption('离线模式运行真实工程工具，使用固定角色；自然语言解析需要真实模型。')
        st.divider()
        st.caption('规范配置')
        st.markdown('**中国规范 · 限定梁模型**')
        st.caption('GB/T 50010（2024修订）\n\nGB 55001 / GB 55008\n\nGB 50009')
        st.divider()
        st.caption('科研与教学原型\n\n当前连接内存会话；不提供跨进程恢复。\n\n完整工程审查仍需工程师完成。')


def download_buttons(ctl, key='main'):
    data=ctl.downloads()
    if not data:return
    a,b,c=st.columns(3)
    a.download_button('下载计算书 .md',data['md'],'engiagent_report.md','text/markdown',key='md_'+key,on_click='ignore',width='stretch')
    b.download_button('下载结果 .json',data['json'],'engiagent_result.json','application/json',key='json_'+key,on_click='ignore',width='stretch')
    c.download_button('下载调用审计',data['audit'],'engiagent_ui_audit.json','application/json',key='audit_'+key,on_click='ignore',width='stretch')


def load_panel(ctl):
    with st.expander('需求与案例 · 加载或解析任务',expanded=ctl.draft is None):
        source=st.selectbox('任务来源',['现有案例模板','上传任务 JSON','自然语言需求'],key='source')
        chosen=st.selectbox('案例模板',list(CASES),key='case_selector')
        if source=='现有案例模板':
            if st.button('加载案例',key='load_case',width='stretch'):
                ctl.load(load_case(chosen),chosen)
                st.rerun()
        elif source=='上传任务 JSON':
            uploaded=st.file_uploader('选择 TaskRequest JSON',type=['json'])
            if st.button('读取并校验文件',disabled=uploaded is None,width='stretch'):
                try:
                    ctl.load(TaskRequest.model_validate_json(uploaded.getvalue()),uploaded.name)
                    st.rerun()
                except ValueError as exc:st.error(str(exc))
        else:
            use_template=st.checkbox('采用上述显式参数模板',value=True)
            query=st.text_area('自然语言工程需求',placeholder='例如：按中国规范新设计一根梁，跨度6m，梁宽300mm，梁高550mm，其余采用指定模板。',height=108)
            live=st.session_state.execution_mode.startswith('DeepSeek')
            if not live:st.caption('请先在侧栏切换到DeepSeek模式；离线模式不会发起自然语言模型调用。')
            if st.button('调用 Dispatcher 提取参数',disabled=not query.strip() or not live,width='stretch'):
                try:
                    with st.spinner('正在提取结构化参数…'):
                        ctl.parse(query,load_case(chosen) if use_template else None)
                    st.rerun()
                except ValueError as exc:st.error(str(exc))
            st.caption('仅点击此按钮才调用解析；模板值和模型提取值在确认表分别标注。')
        if chosen=='梁高修改与局部重算':st.info('先运行已有梁基准，再将梁高550改为600mm，校验并重新确认。')


def parameters_panel(ctl):
    if ctl.draft is None:return
    state=ctl.draft; g=ctl.editor_generation
    with st.container(border=True,key='card_parameters'):
        st.markdown('### 参数与确认')
        mode=st.radio('任务类型',['新方案设计','已有梁验算'],index=0 if state.request.task_type=='new_design' else 1,
                      horizontal=True,key=f'task_{g}',on_change=ctl.mark_dirty)
        task_type='new_design' if mode=='新方案设计' else 'evaluate_existing'
        targets=st.multiselect('验算目标',ALL_TARGETS,default=state.request.targets,format_func=lambda t:LABELS[t],
                               disabled=task_type=='new_design',key=f'targets_{g}',on_change=ctl.mark_dirty)
        col1,col2=st.columns([1.2,1])
        auto=col1.toggle('有限自动改设',value=state.request.auto_redesign if task_type=='new_design' else False,
                         disabled=task_type!='new_design',key=f'auto_{g}',on_change=ctl.mark_dirty)
        limit=col2.number_input('最多轮次',min_value=1,max_value=10,value=state.request.max_iterations,
                               disabled=not auto,key=f'rounds_{g}',on_change=ctl.mark_dirty)
        actions=st.columns(3)
        validate_clicked=actions[0].button('校验参数',key='validate',width='stretch')
        confirm_clicked=actions[1].button('确认参数',disabled=ctl.stage!='validated',key='confirm',width='stretch')
        run_clicked=actions[2].button('运行任务',type='primary',disabled=ctl.stage!='confirmed',key='run',width='stretch')
        all_rows=[]
        for tab,group in zip(st.tabs(list(GROUPS)),GROUPS):
            with tab:
                rows=editor_rows(state,group)
                if task_type=='new_design':rows=[r for r in rows if r['字段'] not in ('bar_count','stirrup_spacing_mm','design_moment_kn_m','design_shear_kn')]
                edited=st.data_editor(rows,hide_index=True,height=310,column_order=['参数','输入值','单位'],
                    disabled=['字段','参数'],key=f'editor_{group}_{g}',on_change=ctl.mark_dirty,
                    column_config={'输入值':st.column_config.TextColumn('输入值',help='留空表示未提供；数值必须配单位。'),
                                   '单位':st.column_config.TextColumn('单位',width='small')},width='stretch')
                all_rows.extend(edited.to_dict('records') if hasattr(edited,'to_dict') else edited)
        if validate_clicked:
            try:
                ctl.apply(all_rows,task_type,targets,auto,int(limit))
                st.rerun()
            except ValueError as exc:st.error(str(exc))
        if confirm_clicked:
            try:
                ctl.confirm();st.rerun()
            except ValueError as exc:st.error(str(exc))
        notice(ctl)
        st.caption('参数、任务或改设设置变更后确认立即失效。新设计的根数与跨内箍筋间距由工程工具确定。')
        if ctl.stage=='validated':st.info('校验完成。请核对全部参数、来源及适用假定后确认。')
        if ctl.stage=='confirmed':st.success('当前参数已确认，可以运行。')
        st.caption('50年、二级、一类环境；理想铰支。端部采用充分受拉直锚保守方案；节点详图仍需复核。')
        if run_clicked:
            mode='offline' if st.session_state.execution_mode.startswith('离线') else 'DeepSeek'
            with st.status('正在执行工程任务…',expanded=True) as status:
                progress=st.progress(0)
                messages=st.empty();lines=[]
                def event(e):
                    name=LABELS.get(e.name,e.name)
                    phase='设计' if e.phase=='design' else '独立验算'
                    if e.kind=='tool':
                        progress.progress(e.step/e.total_steps)
                        check=' · 检查不通过' if e.outputs.get('pass') is False else ' · 检查通过' if e.outputs.get('pass') is True else ''
                        lines.append(f'{phase} {e.step}/{e.total_steps} · {name} · {TOOL_STATUS.get(e.status,e.status)}{check}')
                        messages.text('\n'.join(lines[-7:]))
                    else:status.update(label=phase+' · '+name+' 工具计划'+('调用中' if e.status=='running' else '已返回'))
                ctl.run(mode,callback=event)
                status.update(label='任务执行结束',state='error' if ctl.result is None or ctl.result.evaluation.status=='error' else 'complete')
            st.rerun()


def summary(state):
    verdict=state.evaluation.status
    if verdict=='pass':st.success('请求项目通过 · 完整工程审查仍未完成')
    elif verdict=='fail':st.error('请求项目不通过 · 请查看分项原因与修订记录')
    elif verdict=='error':st.error('执行错误 · 未形成有效通过结论')
    else:st.warning('检查不完整 · 未形成通过结论')
    rows=pd.DataFrame(result_rows(state))
    if not rows.empty:
        for key in ('实际/作用值','承载力/限值'):rows[key]=rows[key].astype(float)
    st.dataframe(rows.style.format(precision=3,na_rep='—'),hide_index=True,width='stretch',
                 column_config={'实际/作用值':st.column_config.NumberColumn(format='%.3f'),
                                '承载力/限值':st.column_config.NumberColumn(format='%.3f')})


def workbench(ctl):
    left,right=st.columns([1,1.65],gap='large')
    with left:
        load_panel(ctl)
        parameters_panel(ctl)
    with right:
        state=ctl.draft
        if state is None:
            with st.container(border=True,key='card_start'):
                st.markdown('### 建立当前工程任务')
                st.info('从左侧加载案例，或提交自然语言需求。参数确认之前不会执行计算。')
                st.markdown('**1** 选择设计或验算任务\n\n**2** 检查参数、单位和来源\n\n**3** 确认并运行，查看独立验算与规划轨迹')
            return
        is_current=ctl.stage=='completed' and ctl.result is not None
        p={k:parameter_python(k,v) for k,v in state.request.parameters.items()}
        c=ctl.result.candidate if is_current else {}
        actual={**p,**c}
        with st.container(border=True,key='card_model'):
            st.markdown('<div class="section-title">ENGINEERING MODEL / 工程示意</div>',unsafe_allow_html=True)
            metrics=st.columns(3)
            metrics[0].metric('计算跨度',number(actual.get('span_mm'))+' mm' if actual.get('span_mm') else '未提供')
            metrics[1].metric('矩形截面',number(actual['beam_width_mm'])+' × '+number(actual['beam_depth_mm'])+' mm' if actual.get('beam_width_mm') and actual.get('beam_depth_mm') else '待确定')
            metrics[2].metric('下部纵筋',str(actual['bar_count'])+'Φ'+number(actual['bar_diameter_mm']) if actual.get('bar_count') and actual.get('bar_diameter_mm') else '待设计/提供')
            svg=beam_svg(p,c)
            st.image(svg,width='stretch')
            st.caption('按当前已知数据生成；图形为工程示意，腰筋与节点位置不推测补画。')
            if ctl.stage=='editing':st.caption('编辑尚未校验时，示意仍使用上次校验的参数；不会把未校验输入当作新方案。')
        with st.container(border=True,key='card_results'):
            st.markdown('### 分项结果与执行状态')
            if is_current:
                summary(ctl.result)
                st.caption('工具成功返回与分项检查通过是不同状态。详细公式、依据、原始输入输出见“计算与规范复核”。')
                download_buttons(ctl)
            else:
                st.info('当前参数尚未执行。'+('上一次结果已保留为历史快照，可在复核页查看。' if ctl.result else '确认后运行，结果将显示在此处。'))
            if ctl.progress:
                with st.expander('实际执行事件'):
                    st.dataframe(ctl.progress,hide_index=True,width='stretch')
        with st.expander('完整参数确认表 · 原值、采用值与来源',expanded=False):
            st.dataframe(audit_rows(state),hide_index=True,width='stretch',height=390)
        if ctl.errors:
            for error in ctl.errors:st.error(error)


def require_result(ctl):
    if ctl.result is None:
        st.info('尚无工程结果。请先在设计工作台确认参数并运行。')
        return None
    if ctl.stage!='completed':st.warning(f'当前草稿尚未重新运行；以下为上次执行的修订 {ctl.result.design_revision} 快照，不是当前草稿结论。')
    return ctl.result


def tool_details(name, result):
    a,b=st.columns(2)
    a.markdown('**工具执行：** '+TOOL_STATUS[result.status])
    checked=result.outputs.get('pass') if result.status=='success' else None
    b.markdown('**分项结论：** '+('通过' if checked is True else '不通过' if checked is False else '未获得有效结论'))
    for error in result.errors+result.outputs.get('reasons',[]):st.error(error)
    if result.status=='success':
        st.markdown('#### 计算值与采用条件')
        st.dataframe(output_rows(result),hide_index=True,width='stretch',column_config={'数值':st.column_config.NumberColumn(format='%.5g')})
    st.markdown('#### 实现公式 · LaTeX')
    st.caption('只读转写现有工具公式。截面计算使用mm、N、MPa；内力输出kN、kN·m。梁均布荷载分析采用相应一致单位。显示不参与重新判定。')
    st.latex(r'M_{\mathrm{N\cdot mm}}=10^6M_{\mathrm{kN\cdot m}},\quad V_{\mathrm N}=10^3V_{\mathrm{kN}},\quad q_{\mathrm{N/mm}}=q_{\mathrm{kN/m}}')
    for latex in FORMULAS.get(name,[]):st.latex(latex)
    if result.status!='success':st.caption('以上为该工具实现模型，当前工具未成功时不表示这些公式已被有效求值。')
    if name in NOTES:st.info(NOTES[name])
    for assumption in result.outputs.get('assumptions',[]):st.caption('采用假定：'+assumption)
    st.markdown('#### 规范依据与版本')
    for ref in result.code_refs:st.write('· '+ref)
    st.caption('公式版本：'+result.formula_version)
    st.markdown('#### 实际输入参数')
    st.dataframe(input_rows(result),hide_index=True,width='stretch',column_config={'数值':st.column_config.NumberColumn(format='%.5g')})
    with st.expander('实际工具输入 · 包括上游材料与几何'):
        st.json(result.inputs)
    with st.expander('原始工具结果、哈希与诊断'):
        st.json(result.model_dump())


def review(ctl):
    state=require_result(ctl)
    if state is None:return
    with st.container(border=True,key='card_review'):
        summary(state)
        st.caption('请求状态：'+state.evaluation.status+' ｜ 规范检查：'+state.evaluation.code_status+' ｜ 完整工程审查：'+state.evaluation.overall_status)
        for item in state.evaluation.unimplemented:st.caption('未覆盖：'+item)
        download_buttons(ctl,'review')
    targets=[t for t in state.request.targets if t in TARGET_TOOLS]
    for tab,target in zip(st.tabs([LABELS[t] for t in targets]),targets):
        with tab:
            name=TARGET_TOOLS[target]; result=state.tool_results.get('evaluation.'+name)
            if result:tool_details(name,result)
            else:st.warning('该项未得到工具结果，不能判定通过。')
    with st.expander('其余实际计算步骤 · 材料、荷载、内力与设计'):
        names=[k for k in state.tool_results if k not in {'evaluation.'+TARGET_TOOLS[t] for t in targets}]
        if names:
            selected=st.selectbox('计算步骤',names,format_func=lambda k:('设计 · ' if k.startswith('design.') else '验算 · ')+LABELS.get(k.split('.')[1],k))
            tool_details(selected.split('.')[1],state.tool_results[selected])


def planning(ctl):
    state=ctl.result or ctl.draft
    if state is None:
        st.info('加载案例后可查看待执行计划；运行后显示实际调用和工具轨迹。');return
    if ctl.result and ctl.stage!='completed':st.warning('当前显示上一次执行的记录；新草稿尚未重新运行。')
    agent_tab,dag_tab,revision_tab=st.tabs(['Agent 执行图','工程依赖 DAG','方案修订比较'])
    with agent_tab:
        calls=[vars(c) for c in ctl.calls]
        if not calls and state.role_events:
            calls=[{**e,'mode':e.get('mode','历史记录 · 模式未保存')} for e in state.role_events]
        st.caption('角色调用与工程依赖是两种图。这里只展示真实调用或历史角色事件；离线角色不会被标成真实大模型。')
        if calls:
            with st.container(border=True,key='card_agents'):st.graphviz_chart(agent_dot(calls,state),width='stretch')
            index=st.selectbox('选择实际角色事件',range(len(calls)),format_func=lambda i:f'{i+1:02d} · {calls[i]["role"]} · {calls[i].get("mode","未记录")}')
            call=calls[index]
            st.write('**调用状态：** '+str(call['status']))
            if call.get('elapsed_seconds') is not None:st.caption(f'适配层记录调用耗时：{call["elapsed_seconds"]:.3f} s；开始时间（UTC）：{call["started_at"]}')
            st.caption('未记录模型内部思维、token或费用；工具逐项耗时也未由内核记录。')
            a,b=st.columns(2)
            with a:
                st.markdown('#### 实际结构化输入')
                if 'inputs' in call:st.json(call['inputs'])
                else:st.info('该历史事件未保存调用输入。')
            with b:
                st.markdown('#### 实际结构化输出')
                if call.get('outputs') is not None:st.json(call['outputs'])
                elif call.get('diagnostic'):st.error(call['diagnostic'])
                else:st.info('该历史事件未保存完整调用输出。')
        else:st.info('尚无实际角色调用；待执行计划不作为执行事件。')
    with dag_tab:
        cols=st.columns(2)
        count=len(state.revisions)
        index=cols[0].selectbox('方案轮次',range(count),index=count-1,format_func=lambda i:f'修订 {state.revisions[i]["revision"]} · {VERDICTS[state.revisions[i]["evaluation"]["status"]]}') if count else None
        phase=cols[1].radio('执行阶段',['evaluation','design'],format_func=lambda x:'Evaluation · 独立验算' if x=='evaluation' else 'Design · 配筋设计',horizontal=True)
        nodes=dag_nodes(state,phase,index)
        st.caption('绿色：已执行　蓝色：缓存复用　灰色：待执行计划　琥珀：阻断　红色：工具/模型失败。执行完成但检查不通过会另行标注。')
        if not nodes:st.info('本轮没有执行该阶段，不生成虚构节点。')
        else:
            selected=st.selectbox('选择节点查看详情',[n['name'] for n in nodes],format_func=lambda n:LABELS.get(n,n)+' · '+n,key=f'node_{phase}_{index}')
            graph,inspector=st.columns([1.65,1])
            with graph:
                with st.container(border=True,key='card_dag'):st.graphviz_chart(dag_dot(nodes,selected),width='stretch')
                skipped=[LABELS.get(n,n) for n in SPECS if n not in {x['name'] for x in nodes}]
                with st.expander('本阶段未纳入子图的工具 · 未计划'):
                    st.write('、'.join(skipped) or '无')
            with inspector:
                node=next(n for n in nodes if n['name']==selected)
                with st.container(border=True,key='card_node'):
                    st.markdown('### '+node['label'])
                    st.code(node['name'],language=None)
                    st.write('**处理：** '+node['action'])
                    st.write('**原因：** '+node['reason'])
                    if node['result']:
                        result=node['result']
                        st.write('**执行：** '+TOOL_STATUS[result.status])
                        st.caption(result.formula_version)
                        st.caption('分项：'+('通过' if result.outputs.get('pass') is True else '不通过' if result.outputs.get('pass') is False else '无独立判定'))
                        with st.expander('输入',expanded=True):st.json(result.inputs,expanded=1)
                        with st.expander('输出'):st.json(result.outputs)
                        for e in result.errors:st.error(e)
                    else:st.caption('尚无实际输入输出。')
    with revision_tab:
        if not state.revisions:st.info('尚无执行修订。');return
        st.dataframe([{'修订':r['revision'],'本次轮次':r['iteration'],'原因':r.get('reason','未记录'),
                       '请求结论':VERDICTS[r['evaluation']['status']]} for r in state.revisions],hide_index=True,width='stretch')
        if len(state.revisions)<2:st.info('目前只有一轮。修改参数后重新确认运行，或开启有限改设，可比较真实修订。');return
        a,b=st.columns(2)
        before=a.selectbox('修改前',range(len(state.revisions)),index=len(state.revisions)-2,format_func=lambda i:f'修订 {state.revisions[i]["revision"]}')
        after=b.selectbox('修改后',range(len(state.revisions)),index=len(state.revisions)-1,format_func=lambda i:f'修订 {state.revisions[i]["revision"]}')
        changes=revision_comparison(state,before,after)
        st.dataframe(changes,hide_index=True,width='stretch') if changes else st.info('两轮已记录输入与方案没有数值变化。')
        r=state.revisions[after]
        st.markdown('#### 修改后实际工具处理')
        st.dataframe([{'阶段':t['phase'],'工具':LABELS.get(t['tool'],t['tool']),'处理':ACTIONS.get(t['action'],t['action']),'原因':t['reason']} for t in r.get('trace',[])],hide_index=True,width='stretch')
        a,b=st.columns(2)
        for col,idx in ((a,before),(b,after)):
            with col:
                st.markdown('#### 修订 '+str(state.revisions[idx]['revision'])+' 分项结论')
                st.json(state.revisions[idx]['evaluation'])


def experiments():
    with st.container(border=True,key='card_experiment'):
        st.markdown('### 统一案例对照 · 后续扩展')
        st.info('正式对照实验未执行')
        st.dataframe([{'执行组':label,'状态':'未执行','结果证据':'尚未提供'} for label in ('人工设计','通用 LLM','固定 Python 流程','EngiAgent 对照组')],hide_index=True,width='stretch')
        st.caption('已有工程演示不冒充标准化对照实验；不生成准确率、耗时或token统计。')
        with st.expander('预留数据接口 · ExperimentRecord'):
            st.code('case_id, group, code_version, evidence, status\nelapsed_seconds: float | None\ntokens: int | None\ncost: float | None',language='python')
        st.markdown((ROOT/'docs/cn_experiment_protocol.md').read_text(encoding='utf-8'))


def main():
    st.set_page_config(page_title='EngiAgent · RC 梁工程工作台',page_icon='▰',layout='wide')
    st.markdown(CSS,unsafe_allow_html=True)
    ctl=current()
    sidebar(ctl);header(ctl)
    page=st.session_state.nav
    if page==PAGES[0]:workbench(ctl)
    elif page==PAGES[1]:review(ctl)
    elif page==PAGES[2]:planning(ctl)
    else:experiments()
