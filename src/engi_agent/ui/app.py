"""Streamlit workbench. All computation is dispatched through service.py."""
from __future__ import annotations
import html
from typing import get_args
import streamlit as st

from engi_agent.engineering.cn_schema import TaskRequest, EngineeringState, parameter_python, CNParameters, REBAR_DIAMETERS
from engi_agent.engineering.cn_workflow import ALL_TARGETS
from engi_agent.engineering.dependency_graph import TARGET_TOOLS, SPECS
from engi_agent.engineering.cn_presentation import OUTPUTS
from engi_agent.engineering.cn_presentation import number, SOURCES, ENUMS
from .service import WorkbenchSession, CASES, ROOT, load_case, ENUM_FIELDS
from .projections import (STAGES, VERDICTS, ACTIONS, TOOL_STATUS, GROUPS, LABELS,
                          editor_rows, audit_rows, result_rows, dag_nodes, revision_comparison, output_rows,input_rows)
from .diagrams import beam_svg, dag_dot, agent_dot
from .formulas import FORMULAS, NOTES
from .styles import CSS

PAGES=['设计工作台','计算与规范复核','Agent 与动态规划','专家咨询']



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
        st.markdown('<div class="eyebrow">中国规范 RC 梁 · 工程工作台</div>',unsafe_allow_html=True)
        title=st.session_state.get('nav',PAGES[0])
        if title==PAGES[0]:st.header(title)
        else:st.title(title)
    with right:
        state=ctl.draft
        status=VERDICTS[ctl.result.evaluation.status] if ctl.stage=='completed' and ctl.result else STAGES[ctl.stage]
        css='pass' if ctl.stage=='completed' and ctl.result.evaluation.status=='pass' else 'fail' if ctl.stage=='error' or ctl.stage=='completed' and ctl.result.evaluation.status in ('fail','error') else 'warn' if ctl.stage in ('editing','validated') else ''
        st.markdown(f'<div class="task-status"><span class="pill {css}">{html.escape(status)}</span><div class="meta">'
                    +html.escape(ctl.case_name)+' · '+(f'修订 {state.design_revision}' if state else '未加载')
                    +'</div></div>',unsafe_allow_html=True)
    active = {'empty':0, 'editing':0, 'parsing':0, 'validated':1,
              'confirmed':2, 'running':2, 'completed':3}.get(ctl.stage, 0)
    steps = ['需求与参数', '核对与确认', '设计与独立验算', '结果复核与修订']
    items = ''.join(f'<li aria-current="{"step" if i == active else "false"}" class="{"done" if i < active else ""}">{i+1:02d}　{title}</li>'
                    for i, title in enumerate(steps))
    st.markdown('<ol class="workflow-steps" aria-label="工程任务进度">'+items+'</ol>', unsafe_allow_html=True)
    if ctl.result and ctl.stage != 'completed':
        st.warning(f'参数已修改，待重新验算。上次结果：修订 {ctl.result.design_revision}。')


def sidebar(ctl):
    with st.sidebar:
        st.markdown('<div class="brand">EngiAgent<span class="brand-dot">.</span></div><div class="eyebrow">RC BEAM WORKBENCH</div>',unsafe_allow_html=True)
        st.write('')
        st.radio('工作区',PAGES,key='nav',label_visibility='collapsed')
        st.divider()
        with st.expander('运行设置', expanded=False):
            st.radio('执行模式',['离线 · 确定性角色','DeepSeek · 真实模型','DeepSeek · 仅需求与咨询'],key='execution_mode',on_change=ctl.mark_dirty)
        st.caption('当前模式：'+st.session_state.execution_mode)
        st.divider()
        with st.expander('规范与适用范围'):
            st.caption('GB/T 50010（2024修订） · GB 55001 · GB 55008 · GB 50009')
            st.caption('简支矩形梁、全跨均布恒活载、单层受拉筋。')



def download_buttons(ctl, key='main'):
    data=ctl.downloads()
    if not data:return
    a,b,c=st.columns(3)
    a.download_button('下载计算书 .md',data['md'],'engiagent_report.md','text/markdown',key='md_'+key,on_click='ignore',width='stretch')
    b.download_button('下载结果 .json',data['json'],'engiagent_result.json','application/json',key='json_'+key,on_click='ignore',width='stretch')
    c.download_button('下载调用审计',data['audit'],'engiagent_ui_audit.json','application/json',key='audit_'+key,on_click='ignore',width='stretch')


def load_panel(ctl):
    with st.expander('需求与案例 · 加载或解析任务',expanded=ctl.draft is None):
        source=st.selectbox('任务来源',['现有案例模板','上传任务 JSON','自然语言需求','图片识别 OCR'],key='source')
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
        elif source=='图片识别 OCR':
            image_task_panel(ctl, chosen)
        else:
            use_template=st.checkbox('采用上述显式参数模板',value=False)
            st.caption('勾选后使用模板补充未说明的参数。')
            query=st.text_area('自然语言工程需求',placeholder='例如：按中国规范新设计一根梁，跨度6m，梁宽300mm，梁高550mm，其余采用指定模板。',height=108)
            live=st.session_state.execution_mode.startswith('DeepSeek')
            if not live:st.caption('自然语言解析需在侧栏选择 DeepSeek 模式。')
            if st.button('调用 Dispatcher 提取参数',disabled=not query.strip() or not live,width='stretch'):
                try:
                    with st.spinner('正在提取结构化参数…'):
                        ctl.parse(query,load_case(chosen) if use_template else None)
                    st.rerun()
                except ValueError as exc:st.error(str(exc))
        if chosen=='梁高修改与局部重算':st.info('先运行已有梁基准，再将梁高550改为600mm，校验并重新确认。')


def image_task_panel(ctl, chosen):
    from hashlib import sha256
    from .ocr import recognize_image

    uploaded=st.file_uploader('上传工程需求图片',type=['png','jpg','jpeg','webp','bmp'],key='ocr_upload',max_upload_size=10)
    data=uploaded.getvalue() if uploaded is not None else None
    digest=sha256(data).hexdigest() if data else None
    if st.session_state.get('ocr_upload_digest') != digest:
        st.session_state.ocr_upload_digest=digest
        st.session_state.pop('ocr_result',None)
        st.session_state.pop('ocr_text',None)
    if st.button('识别图片文字',disabled=data is None,key='ocr_recognize',width='stretch'):
        try:
            with st.spinner('正在调用 DeepSeek 视觉模型识别图片…'):
                result=recognize_image(data)
            st.session_state.ocr_result=result.evidence()
            st.session_state.ocr_text=result.text
        except (ValueError, RuntimeError) as exc:
            st.session_state.pop('ocr_result',None)
            st.session_state.pop('ocr_text',None)
            st.error(str(exc))
    result=st.session_state.get('ocr_result')
    if not result:return
    with st.expander('查看原图'):
        st.image(data,width='stretch')
    if result.get('model') is None:
        st.info('识别方式已更新，请重新调用 DeepSeek 识别图片。')
        return
    st.success('DeepSeek 已生成任务描述。')
    for item in result.get('uncertainties',[]):st.warning('待核对：'+item)
    query=st.text_area('识别后的任务描述 · 可修改',key='ocr_text',height=220)
    extra=st.text_area('补充任务要求',placeholder='例如：请新设计这根梁；或仅复核已有配筋。',key='ocr_extra',height=80)
    st.caption('请核对尺寸、单位、钢筋牌号与直径，以及模型标出的待核对项。')
    use_template=st.checkbox('使用案例模板补充未说明参数',value=False,key='ocr_template')
    live=st.session_state.execution_mode.startswith('DeepSeek')
    if not live:st.info('图片识别通过 DeepSeek 云端调用；任务分派需在运行设置中选择 DeepSeek 模式。')
    if st.button('将识别文本交给 Dispatcher',key='ocr_dispatch',disabled=not query.strip() or not live,width='stretch'):
        try:
            with st.spinner('正在解析图片任务并提取参数…'):
                ctl.parse(query+('\n补充要求：'+extra if extra.strip() else ''),
                          load_case(chosen) if use_template else None,image_evidence=result)
            st.rerun()
        except ValueError as exc:st.error(str(exc))


def parameters_panel(ctl):
    if ctl.draft is None:return
    state=ctl.draft; g=ctl.editor_generation
    with st.container(border=True,key='card_parameters'):
        st.markdown('### 参数与确认')
        with st.expander('任务与验算设置', expanded=False):
            mode=st.radio('任务类型',['新方案设计','已有梁验算'],index=0 if state.request.task_type=='new_design' else 1,
                          horizontal=True,key=f'task_{g}',on_change=ctl.mark_dirty)
            task_type='new_design' if mode=='新方案设计' else 'evaluate_existing'
            targets=st.multiselect('验算目标',ALL_TARGETS,default=state.request.targets,format_func=lambda t:LABELS[t],
                                   disabled=task_type=='new_design',key=f'targets_{g}',on_change=ctl.mark_dirty)
            col1,col2=st.columns([1.2,1])
            auto=col1.toggle('有限自动改设',value=state.request.auto_redesign if task_type=='new_design' else False,
                             disabled=task_type!='new_design',key=f'auto_{g}',on_change=ctl.mark_dirty)
            limit=col2.number_input('最多轮次',min_value=1,max_value=40,value=state.request.max_iterations,
                                   disabled=not auto,key=f'rounds_{g}',on_change=ctl.mark_dirty)
        st.caption(('新方案设计' if task_type=='new_design' else '已有梁验算')+' · '+'、'.join(LABELS[t] for t in (ALL_TARGETS if task_type=='new_design' else targets)))
        search_diameters=st.multiselect('允许搜索的纵筋直径 / mm',REBAR_DIAMETERS,default=state.request.search_diameters_mm,
            disabled=task_type!='new_design' or not auto,key=f'search_diameters_{g}',on_change=ctl.mark_dirty,
            help='留空时固定使用输入直径。')
        solutions=st.number_input('最多展示方案数',min_value=1,max_value=3,value=state.request.solution_count,
            disabled=task_type!='new_design' or not auto,key=f'solutions_{g}',on_change=ctl.mark_dirty,
            help='最多展示此数量；先去重和剔除明显劣势方案，再保留材料用量、梁高及验算裕量有取舍的方案。')
        st.caption('梁宽、梁高填值即固定；留空则由程序初选并调整。可在几何参数中填写最大梁宽、最大梁高。变更后请校验并查看确认范围。')
        if task_type=='new_design' and not auto:
            st.caption('自动改设已关闭，仅尝试一个候选方案。')
        with st.expander('参数来源与支持规格'):
            inherited=[row for row in audit_rows(state) if row.get('来源')=='显式案例模板']
            st.caption(f'{len(inherited)} 项参数来自案例模板。')
            st.dataframe(inherited,hide_index=True,width='stretch') if inherited else None
            st.write('程序支持公称直径 / mm：'+ '、'.join(map(str,REBAR_DIAMETERS)))
            st.caption('HPB300 箍筋支持目录内 6–25 mm 规格。')
        all_rows=[]
        notice(ctl)
        group_titles=[group + (f' · 缺{sum(k in state.missing_parameters for k in keys)}项' if any(k in state.missing_parameters for k in keys) else '') for group,keys in GROUPS.items()]
        for tab,group in zip(st.tabs(group_titles),GROUPS):
            with tab:
                rows=editor_rows(state,group)
                if task_type=='new_design':rows=[r for r in rows if r['字段'] not in ('bar_count','stirrup_spacing_mm','design_moment_kn_m','design_shear_kn')]
                missing=[r['参数'] for r in rows if r['字段'] in state.missing_parameters]
                if missing:st.warning('本组必填缺项：'+'、'.join(missing))
                enum_rows=[row for row in rows if row['字段'] in ENUM_FIELDS]
                if enum_rows:
                    with st.expander(group+'选项 · 结构条件与材料等级',expanded=group=='材料' or any(row['字段'] in state.missing_parameters for row in enum_rows)):
                        for row in enum_rows:
                            key=row['字段']
                            choices=[None,*get_args(CNParameters.model_fields[key].annotation)]
                            current=state.request.parameters.get(key)
                            value=current.value if current else None
                            chosen=st.selectbox(row['参数'],choices,index=choices.index(value) if value in choices else 0,
                                format_func=lambda value:'请选择' if value is None else ENUMS.get(value, '一类环境' if value=='I' else str(value)),
                                key=f'enum_{key}_{g}',on_change=ctl.mark_dirty)
                            all_rows.append({**row,'输入值':'' if chosen is None else str(chosen),'单位':''})
                rows=[row for row in rows if row['字段'] not in ENUM_FIELDS]
                for row in rows:
                    item=state.request.parameters.get(row['字段'])
                    row['来源']=SOURCES.get(item.source,item.source) if item else '待提供'
                edited=st.data_editor(rows,hide_index=True,height=350,column_order=['参数','输入值','单位'],
                    disabled=['字段','参数','来源'],key=f'editor_{group}_{g}',on_change=ctl.mark_dirty,
                    column_config={'输入值':st.column_config.TextColumn('输入值',help='留空表示未提供；数值必须配单位。'),
                                   '参数':st.column_config.TextColumn('参数'),
                                   '单位':st.column_config.TextColumn('单位',width='small'),
                                   '来源':st.column_config.TextColumn('来源',width='small')},width='stretch')
                all_rows.extend(edited.to_dict('records') if hasattr(edited,'to_dict') else edited)
        if ctl.stage == 'validated':
            with st.expander('确认前核对 · 全部采用值、来源与假定', expanded=True):
                st.dataframe(audit_rows(state), hide_index=True, width='stretch', height=260)
                if state.request.task_type=='new_design':
                    from engi_agent.engineering.design_search import search_domain, domain_text
                    params={k:parameter_python(k,v) for k,v in state.request.parameters.items()}
                    if 'span_mm' in params:st.info('截面设计范围：'+domain_text(search_domain(params)))
                st.caption('设计假定：50年、二级、一类环境、理想铰支、充分受拉直锚。')
        hints = {'editing':'下一步：填写并校验参数。', 'validated':'下一步：核对采用值后，点击确认参数。',
                 'confirmed':'下一步：运行任务。', 'completed':'计算已完成。修改参数后可创建下一轮修订。'}
        st.caption(hints.get(ctl.stage, '先校验参数，再确认并运行。'))
        actions=st.columns(3)
        validate_clicked=actions[0].button('校验参数',key='validate',width='stretch')
        confirm_clicked=actions[1].button('确认参数',disabled=ctl.stage!='validated',key='confirm',width='stretch')
        run_clicked=actions[2].button('运行任务',type='primary',disabled=ctl.stage!='confirmed',key='run',width='stretch')
        if validate_clicked:
            try:
                ctl.apply(all_rows,task_type,targets,auto,int(limit),search_diameters=search_diameters,solution_count=int(solutions))
                st.rerun()
            except ValueError as exc:st.error(str(exc))
        if confirm_clicked:
            try:
                ctl.confirm();st.rerun()
            except ValueError as exc:st.error(str(exc))
        if run_clicked:
            mode='offline' if st.session_state.execution_mode.startswith('离线') else 'program' if '仅需求与咨询' in st.session_state.execution_mode else 'DeepSeek'
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
    if verdict=='pass':st.success('请求项目通过')
    elif verdict=='fail':st.error('请求项目不通过 · 请查看分项原因与修订记录')
    elif verdict=='error':st.error('执行错误 · 未形成有效通过结论')
    else:st.warning('检查不完整 · 未形成通过结论')
    if state.search_stop_reason:st.caption('设计搜索：'+state.search_stop_reason)
    if state.design_alternatives:
        st.markdown('**筛选后的已通过候选**')
        st.dataframe([{'方案':'修订 '+str(r['revision'])+(' · 当前' if r['revision']==state.design_revision else ''),
            '截面/mm · 纵筋':number(r['candidate']['beam_width_mm'])+'×'+number(r['candidate']['beam_depth_mm'])+' · '+str(r['candidate']['bar_count'])+'Φ'+number(r['candidate']['bar_diameter_mm']),
            '受拉纵筋/mm²':number(r['candidate']['As_mm2']),
            '混凝土/m³':number(r.get('metrics',{}).get('concrete_m3'),3),
            '控制利用率':number(r.get('metrics',{}).get('governing_utilization'),3)}
            for r in state.design_alternatives],hide_index=True,width='stretch')
    filtering=state.design_search.get('filter')
    if filtering:
        st.caption(f"尝试 {filtering['tested']} 轮 · 通过 {filtering['passed']} 轮 · 去重 {filtering['duplicates']} 项 · 剔除支配方案 {filtering['dominated']} 项 · 展示 {filtering['displayed']} 项")
        with st.expander('方案初筛与推荐依据'):
            st.write(filtering['rule'])
            for option in state.design_alternatives:
                st.write('修订 '+str(option['revision'])+'：'+option.get('selection_reason','已通过候选'))
            st.caption('推荐采用混凝土体积与受拉纵筋面积的等权相对指标；控制利用率越低，所列验算裕量越大。')
            st.caption(filtering['limitation'])
    rows=result_rows(state)
    tiles=[]
    for row in rows:
        passed=row['分项结论']=='通过'
        tone='pass' if passed else 'fail' if row['分项结论']=='不通过' else 'warn'
        detail='多项构造条件' if row['单位']=='多项条件' else number(row['实际/作用值'],3)+' / '+number(row['承载力/限值'],3)+' '+row['单位']
        tiles.append('<div class="result-tile"><strong>'+html.escape(row['检查项目'])+'</strong><span class="pill '+tone+'">'
                     +html.escape(row['分项结论'])+'</span><p>'+html.escape(detail)+'</p></div>')
    st.markdown('<div class="result-grid" aria-label="请求项目验算摘要">'+''.join(tiles)+'</div>',unsafe_allow_html=True)
    with st.expander('查看结果明细 · 作用值、限值与工具状态'):
        display=[]
        for row in rows:
            display.append({**row, '实际/作用值':number(row['实际/作用值'],3),
                            '承载力/限值':number(row['承载力/限值'],3)})
        st.dataframe(display,hide_index=True,width='stretch')


def workbench(ctl):
    left,right=st.columns([1.05,1.25],gap='large')
    with left:
        load_panel(ctl)
        parameters_panel(ctl)
    with right:
        state=ctl.draft
        if state is None:
            with st.container(border=True,key='card_start'):
                st.markdown('### 建立当前工程任务')
                st.info('从左侧加载案例，或提交自然语言需求。')
                st.markdown('**1** 选择设计或验算任务\n\n**2** 检查参数、单位和来源\n\n**3** 确认并运行，查看独立验算与规划轨迹')
            return
        is_current=ctl.stage=='completed' and ctl.result is not None
        p={k:parameter_python(k,v) for k,v in state.request.parameters.items()}
        c=ctl.result.candidate if is_current else {}
        actual={**p,**c}
        with st.container(border=True,key='card_model'):
            st.markdown('<div class="section-title">工程模型 · 当前已校验参数</div>',unsafe_allow_html=True)
            metrics=st.columns(3)
            metrics[0].metric('计算跨度',number(actual.get('span_mm'))+' mm' if actual.get('span_mm') else '未提供')
            metrics[1].metric('矩形截面',number(actual['beam_width_mm'])+' × '+number(actual['beam_depth_mm'])+' mm' if actual.get('beam_width_mm') and actual.get('beam_depth_mm') else '待确定')
            metrics[2].metric('下部纵筋',str(actual['bar_count'])+'Φ'+number(actual['bar_diameter_mm']) if actual.get('bar_count') and actual.get('bar_diameter_mm') else '待设计/提供')
            st.image(beam_svg(p,c),width='stretch',caption='简支梁立面与矩形截面示意')
            if ctl.stage=='editing':st.caption('示意图使用上次校验的参数。')
        with st.container(border=True,key='card_results'):
            st.markdown('### 分项结果与执行状态')
            if is_current:
                summary(ctl.result)
                if len(ctl.result.design_alternatives)>1:
                    labels={r['revision']:f"修订 {r['revision']} · {number(r['candidate']['beam_width_mm'])}×{number(r['candidate']['beam_depth_mm'])} · {r['candidate']['bar_count']}Φ{number(r['candidate']['bar_diameter_mm'])}"
                            for r in ctl.result.design_alternatives}
                    selected=st.selectbox('工程师选择已验证候选',list(labels),
                        format_func=lambda r:labels[r],key='verified_alternative')
                    if st.button('选用此已验证方案',key='select_alternative'):
                        ctl.select_design_alternative(selected);st.rerun()
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
    if ctl.stage!='completed':st.warning(f'以下为修订 {ctl.result.design_revision} 的历史结果，当前修改待重新验算。')
    return ctl.result


def tool_details(name, result):
    from engi_agent.engineering.calculation_trace import calculation_steps
    from engi_agent.engineering.references import professional_references
    from .latex_steps import step_formula, numeric_latex
    checked=result.outputs.get('pass') if result.status=='success' else None
    if checked is not None:
        (st.success if checked else st.error)('本项验算'+('通过' if checked else '不通过'))
    elif result.status!='success':st.warning('本项未完成有效计算，不能判定通过。')
    for reason in result.errors+result.outputs.get('reasons',[]):st.write('· '+reason)
    st.markdown('#### 分步计算 · 公式、代入与判定')
    st.caption('代入值取自本轮实际计算记录；显示取舍不改变验算结论。')
    steps=result.calculation_steps or calculation_steps(result)
    for row in steps:
        if row['title']=='工具总判定':continue
        st.markdown('**'+str(row['step'])+'. '+row['title']+'**')
        formula=step_formula(row)
        if formula:st.latex(formula)
        elif not row['substitution'].startswith('{'):st.caption(row['formula'])
        substituted=numeric_latex(row['substitution'])
        value=row['result']
        if substituted:
            rendered=numeric_latex(str(value)) if isinstance(value,(int,float)) and not isinstance(value,bool) else None
            st.markdown('**代入：**')
            st.latex(substituted+(r' = '+rendered if rendered else ''))
        elif not row['substitution'].startswith('{'):
            st.write('代入：'+row['substitution'])
        if not substituted or not isinstance(value,(int,float)):
            st.write('结果：'+(number(value,6) if isinstance(value,(float,int)) else str(value))+' '+row['unit'])
        elif row['unit']:st.caption('单位：'+row['unit'])
    with st.expander('采用参数与条件'):
        from .projections import label
        rows=[]
        for key,value in result.inputs.get('parameters',{}).items():
            if value is not None and label(key)!=key:
                rows.append({'参数':label(key),'采用值':ENUMS.get(value,str(value)) if isinstance(value,str) else number(value,6)})
        if rows:st.dataframe(rows,hide_index=True,width='stretch')
        for assumption in result.outputs.get('assumptions',[]):st.write('· '+assumption)
        if name in NOTES:st.caption(NOTES[name])
    refs=professional_references(result.code_refs)
    if refs:
        with st.expander('规范依据'):
            for ref in refs:st.write('· '+ref)


def review(ctl):
    state=require_result(ctl)
    if state is None:return
    with st.container(border=True,key='card_review'):
        summary(state)
        with st.expander('适用范围与未覆盖项目'):
            st.caption('规范检查：'+state.evaluation.code_status+' ｜ 完整工程审查：'+VERDICTS[state.evaluation.overall_status])
            for item in state.evaluation.unimplemented:st.caption('未覆盖：'+item)
        download_buttons(ctl,'review')
    targets=[t for t in state.request.targets if t in TARGET_TOOLS]
    for tab,target in zip(st.tabs([LABELS[t] for t in targets]),targets):
        with tab:
            name=TARGET_TOOLS[target]; result=state.tool_results.get('evaluation.'+name)
            if result:tool_details(name,result)
            else:st.warning('该项暂无验算结果。')
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
        if calls:
            run_ids=sorted({c.get('run_id',0) for c in calls})
            batch=st.selectbox('运行批次', ['all', *run_ids], index=len(run_ids),
                               format_func=lambda value:'全部历史' if value=='all' else '需求解析 / 初始记录' if value==0 else f'第 {value} 次运行',
                               key='agent_batch')
            visible=[c for c in calls if batch=='all' or c.get('run_id',0)==batch]
            st.caption(f'本批次 {len(visible)} 条记录 · 全部历史 {len(calls)} 条')
            statuses={'success':'完成','error':'失败','running':'执行中'}
            modes={'offline':'离线角色','program':'程序执行','structured_file':'任务文件','DeepSeek':'DeepSeek'}
            st.dataframe([{'顺序':i+1,'角色':c['role'],'执行方式':modes.get(c.get('mode'),c.get('mode','未记录')),
                           '状态':statuses.get(c['status'],c['status']),
                           '耗时/s':round(c['elapsed_seconds'],3) if c.get('elapsed_seconds') is not None else None}
                          for i,c in enumerate(visible)],hide_index=True,width='stretch')
            with st.expander('调用关系图'):
                st.graphviz_chart(agent_dot(visible,state),width='stretch')
            index=st.selectbox('选择实际角色事件',range(len(visible)),format_func=lambda i:f'{i+1:02d} · {visible[i]["role"]} · {visible[i].get("mode","未记录")}',key=f'agent_event_{batch}')
            call=visible[index]
            st.write('**调用状态：** '+statuses.get(call['status'],call['status']))
            if call.get('elapsed_seconds') is not None:st.caption(f'调用耗时：{call["elapsed_seconds"]:.3f} s')
            if call.get('diagnostic'):st.error(call['diagnostic'])
            with st.expander('结构化输入与输出 · 调用证据'):
                st.markdown('#### 实际输入')
                if 'inputs' in call:st.json(call['inputs'])
                else:st.info('该历史事件未保存调用输入。')
                st.markdown('#### 实际输出')
                if call.get('outputs') is not None:st.json(call['outputs'])
                else:st.info('该历史事件未保存完整调用输出。')
                if call.get('started_at'):st.caption('开始时间（UTC）：'+call['started_at'])
        else:st.info('尚无角色调用记录。')
    with dag_tab:
        cols=st.columns(2)
        count=len(state.revisions)
        index=cols[0].selectbox('方案轮次',range(count),index=count-1,format_func=lambda i:f'修订 {state.revisions[i]["revision"]} · {VERDICTS[state.revisions[i]["evaluation"]["status"]]}') if count else None
        phase=cols[1].radio('执行阶段',['evaluation','design'],format_func=lambda x:'Evaluation · 独立验算' if x=='evaluation' else 'Design · 配筋设计',horizontal=True)
        nodes=dag_nodes(state,phase,index)
        st.caption('绿色：已执行　蓝色：缓存复用　灰色：待执行　琥珀：阻断　红色：执行失败')
        if not nodes:st.info('本轮未执行该阶段。')
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
        if len(state.revisions)<2:st.info('运行两轮后可比较修订。');return
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


def fill_expert_question(question):
    st.session_state['expert_query']=question


def expert(ctl):
    from engi_agent.engineering.consultation import ConsultationReply, basis_hash
    state=require_result(ctl)
    if state is None:return
    from .expert_content import answer_blocks, suggested_questions
    suggestions=suggested_questions(state,ctl.consultations)
    columns=st.columns(len(suggestions))
    for index,(column,question) in enumerate(zip(columns,suggestions)):
        column.button(question,key=f'expert_suggestion_{index}',width='stretch',
                      on_click=fill_expert_question,args=(question,))
    query=st.text_area('向工程专家提问',key='expert_query',height=100,
                       placeholder='输入问题，或选择上方建议')
    live=st.session_state.execution_mode.startswith('DeepSeek')
    if st.button('提交咨询',key='ask_expert',disabled=ctl.stage!='completed' or not query.strip(),type='primary'):
        try:
            with st.spinner('正在核对当前结果与问题…'):ctl.ask_expert(query,'DeepSeek' if live else 'offline')
            st.rerun()
        except ValueError as exc:st.error(str(exc))
    for position,record in enumerate(reversed(ctl.consultations)):
        reply=ConsultationReply.model_validate(record)
        with st.expander('咨询 · '+reply.query, expanded=position==0):
            st.markdown('**问题：** '+reply.query)
            stale=reply.basis_hash!=basis_hash(state) or ctl.stage!='completed'
            st.caption(f'依据：修订 {reply.revision}'+(' · 历史依据，不能采用' if stale else ' · 当前结果'))
            if reply.decision.intent=='unsupported':st.warning('该问题超出当前工程模型，请由工程师另行分析。')
            for question in reply.decision.questions:st.info(question)
            if reply.preview:
                st.markdown('**参数建议 · 待验算**')
                st.caption('采用后保留现有配筋，转为已有梁验算。重新选筋请回设计工作台。')
                st.dataframe([{k:v for k,v in row.items() if k!='field'} for row in reply.preview],hide_index=True,width='stretch')
                if st.button('将建议写入待确认草稿',key='adopt_'+reply.id,disabled=stale or reply.applied):
                    try:ctl.adopt_expert_proposal(reply.id);st.rerun()
                    except ValueError as exc:st.error(str(exc))
                if reply.applied:st.success('建议已写入草稿，请回到设计工作台确认后运行。')
            answer=reply.answer or '\n\n'.join(item.text for item in reply.evidence)
            if answer:
                for kind,content in answer_blocks(answer):
                    if kind=='latex':st.latex(content)
                    else:st.markdown(content)
            for item in reply.evidence:
                with st.expander('查看依据 · '+item.title):
                    if item.tool:
                        shown=[{'项目':OUTPUTS.get(k,k),'记录值':number(v,5) if isinstance(v,(int,float)) and not isinstance(v,bool) else str(v)}
                               for k,v in item.outputs.items() if k in OUTPUTS and not isinstance(v,(dict,list))]
                        if shown:st.dataframe(shown,hide_index=True,width='stretch')
                    else:
                        st.write(item.text)
                    from engi_agent.engineering.references import professional_references
                    for ref in professional_references(item.references):st.caption(ref)



def main():
    st.set_page_config(page_title='EngiAgent · RC 梁工程工作台',page_icon='▰',layout='wide',initial_sidebar_state='collapsed')
    st.markdown(CSS,unsafe_allow_html=True)
    ctl=current()
    if st.session_state.get('nav') not in PAGES:st.session_state.nav=PAGES[0]
    sidebar(ctl)
    page=st.session_state.nav
    if page==PAGES[0]:
        from .landing import cover,about
        cover()
        with st.container(key='calculation_workspace'):
            st.markdown('<div id="engineering-workbench" class="ea-workbench-anchor"></div>',unsafe_allow_html=True)
            header(ctl)
            workbench(ctl)
            from .preference_panel import preference_panel
            preference_panel(ctl)
            about()
    else:
        header(ctl)
        if page==PAGES[1]:review(ctl)
        elif page==PAGES[2]:planning(ctl)
        elif page=='专家咨询':expert(ctl)
