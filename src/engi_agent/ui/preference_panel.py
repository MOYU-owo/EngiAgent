"""Small extension of the existing workbench; all plotted results are verified."""
from itertools import combinations
import json
import streamlit as st
from engi_agent.engineering.preferences import PreferenceStore,pool,score,nondominated


def simulate_evaluations(state,rounds=20):
    """Private synthetic judge. Its score/weights are never inputs to the learner."""
    items=pool(state)
    pairs=[(a,b) for a,b in combinations(items,2) if a['features']!=b['features']]
    if not pairs:raise ValueError('至少需要两个特征不同的已通过候选；可增加规则搜索轮次')
    store=PreferenceStore('simulated')
    for index in range(rounds):
        a,b=pairs[index%len(pairs)]
        def oracle(item):
            h,area,u=item['features']
            return .05*h+.05*area+.9*u
        chosen=min((a,b),key=oracle)
        snapshot,_=store.load()
        store.evaluate(state,a['id'],b['id'],chosen['id'],snapshot.version)
    return store.load()[0]


def chart_rows(state,snapshot,group):
    items=pool(state);front={i['id'] for i in nondominated(items)}
    return [dict(group=group,revision=i['revision'],height=i['raw'][0],steel=i['raw'][1],
                 utilization=i['raw'][2],score=score(i,snapshot),front=i['id'] in front) for i in items]


def scatter(rows):
    if not rows:return
    st.vega_lite_chart(rows,{
        'transform':[{'calculate':"datum.front ? '取舍方案' : '其他合格方案'",'as':'front_label'}],
        'layer':[{'mark':{'type':'point','filled':True,'size':90},'encoding':{
            'x':{'field':'height','type':'quantitative','title':'梁高 / mm','scale':{'zero':False}},
            'y':{'field':'steel','type':'quantitative','title':'受拉纵筋面积 / mm²','scale':{'zero':False}},
            'color':{'field':'group','type':'nominal','title':'设计方式'},
            'shape':{'field':'front_label','type':'nominal','title':'方案类型'},
            'tooltip':[{'field':k,'type':'quantitative','title':label} for k,label in (
                ('revision','方案编号'),('height','梁高 / mm'),('steel','受拉纵筋面积 / mm²'),
                ('utilization','验算利用率'),('score','偏好成本（越低越好）'))]}}]},width='stretch')
    st.caption('每个点都是通过检查的方案。取舍方案指梁高、纵筋面积和验算利用率不能被其他已搜索方案同时改善的方案；这里只画出其中两个维度。')


def _next_pair():
    st.session_state['pref_pair_offset']=st.session_state.get('pref_pair_offset',0)+1
    for key in ('pref_left','pref_right'):
        st.session_state.pop(key,None)


def _scheme_label(item):
    c=item['candidate']
    return (f"方案 {item['revision']} · {c['beam_width_mm']:g} × {c['beam_depth_mm']:g} mm"
            f" · {c['bar_count']}Φ{c['bar_diameter_mm']:g}")


def _pair_vote(ctl,state,store,snapshot,items):
    # Only offer pairs that can teach the three-feature learner something.
    if len({tuple(i['features']) for i in items})<2:
        st.info('还需要两份有不同取舍的合格方案。可加载“截面与配筋联合设计”模板，确认后运行。')
        return
    mapping={i['id']:i for i in items}
    keys=list(mapping)
    a,b=st.columns(2)
    with a:
        left=st.selectbox('左侧方案',keys,index=st.session_state.get('pref_pair_offset',0)%len(keys),
                          format_func=lambda k:_scheme_label(mapping[k]),key='pref_left')
    right_keys=[k for k in keys if mapping[k]['features']!=mapping[left]['features']]
    if st.session_state.get('pref_right') not in right_keys:
        st.session_state.pop('pref_right',None)
    with b:
        right=st.selectbox('右侧方案',right_keys,format_func=lambda k:_scheme_label(mapping[k]),key='pref_right')
    choice=None
    for col,key,side,button_key in ((a,left,'左侧','pref_choose_a'),(b,right,'右侧','pref_choose_b')):
        with col:
            item=mapping[key];c=item['candidate']
            st.markdown(f"**{c['beam_width_mm']:g} × {c['beam_depth_mm']:g} mm　·　{c['bar_count']}Φ{c['bar_diameter_mm']:g}**")
            st.write(f"受拉纵筋面积：{item['raw'][1]:,.0f} mm²")
            st.write(f"验算利用率：{item['raw'][2]:.1%}")
            if st.button('更喜欢'+side,key=button_key,disabled=ctl.stage!='completed',width='stretch'):
                choice=key
    st.caption('两份方案均通过本次检查。利用率越低，表示所列验算的裕量越大；按你的综合取舍选择即可。')
    st.button('换一组方案',key='pref_next_pair',on_click=_next_pair,disabled=ctl.stage!='completed')
    if choice:
        try:
            store.evaluate(state,left,right,choice,snapshot.version)
            st.session_state['pref_notice']='已记住这次选择。你可以继续比较，也可以将偏好用于本次设计。'
            st.rerun()
        except (ValueError,OSError) as exc:st.error('选择未能保存：'+str(exc))


def preference_panel(ctl):
    state=ctl.result
    if not state or state.request.task_type!='new_design':return
    with st.container(border=True,key='design_preferences'):
        st.markdown('### 设计偏好')
        st.caption('选出你更喜欢的方案，系统会记住你的取舍，用于后续设计搜索。')
        source=st.session_state.get('pref_source','real')
        store=PreferenceStore(source)
        try:snapshot,records=store.load()
        except (ValueError,OSError) as exc:
            st.error('暂时无法读取已保存的偏好：'+str(exc));return
        notice=st.session_state.pop('pref_notice',None)
        if notice:st.success(notice)
        if source=='simulated':
            st.info(f'当前为模拟体验，已有 {len(records)} 次模拟选择；与你的真实偏好分开保存。')
        else:
            st.caption(f'已保存 {len(records)} 次选择。' if records else '还没有偏好记录，先从下面两份方案中选一份。')
        items=pool(state)
        if source=='real':_pair_vote(ctl,state,store,snapshot,items)
        active=ctl.draft.request.preference_guidance
        if ctl.stage=='running':st.caption('设计正在运行，完成后可继续评价。')
        elif ctl.stage=='confirmed':st.info('参数已确认，请点击上方“运行任务”。')
        elif ctl.stage=='validated':st.info('设计草稿待确认，请回到上方“确认参数”，再点击“运行任务”。')
        elif ctl.stage!='completed':st.info('设计草稿有修改，请先在上方校验并确认参数。')
        elif active:
            frozen=ctl.draft.request.preference_snapshot
            current=bool(frozen and frozen.source==source and frozen.version==snapshot.version)
            st.caption('本次设计已使用当前偏好。' if current else '已有新的偏好或切换了评价来源，点击下方按钮可更新设计草稿。')
        if st.button('本次设计使用'+('模拟偏好' if source=='simulated' else '我的偏好'),key='pref_apply',
                     disabled=not records or ctl.stage!='completed',type='primary'):
            ctl.configure_preference(True,source)
            st.session_state['pref_notice']='偏好已用于设计草稿。请回到上方“确认参数”，再点击“运行任务”。'
            st.rerun()
        if not records:st.caption('保存一次选择后，即可使用偏好。')
        if active and st.button('本次设计不使用偏好',key='pref_disable',disabled=ctl.stage!='completed'):
            ctl.configure_preference(False,source)
            st.session_state['pref_notice']='已关闭本次设计的偏好引导，请回到上方重新确认参数。'
            st.rerun()
        with st.expander('查看已记住的偏好'):
            st.caption('当前对三类取舍的重视程度；来自已有选择的初步估计。')
            st.dataframe([{'取舍':n,'重视程度':f'{w:.0%}'} for n,w in zip(
                ('减小梁高','减少受拉纵筋','保留验算裕量'),snapshot.weights)],hide_index=True,width='stretch')
            if records:
                st.dataframe([{'第几次':r['version'],'比较方案':f"{r['left']['revision']} / {r['right']['revision']}",
                    '更喜欢':r['left']['revision'] if r['chosen_id']==r['left']['id'] else r['right']['revision']}
                    for r in records[-10:]],hide_index=True,width='stretch')
            st.caption('记录已保存在本机，重启后仍保留。')
        with st.expander('模拟体验与效果对比'):
            st.radio('使用哪组偏好',['real','simulated'],format_func=lambda x:'我的选择' if x=='real' else '模拟选择（仅演示）',
                     horizontal=True,key='pref_source')
            if source=='simulated':
                st.caption('自动比较当前这批合格方案20次，演示如何学习偏好；不会新增20个设计任务。')
                if st.button('自动体验20次选择',key='pref_simulate',disabled=len({tuple(i['features']) for i in items})<2 or ctl.stage!='completed'):
                    try:
                        simulate_evaluations(state)
                        st.session_state['pref_notice']='已完成20次模拟选择。可以查看偏好，或比较设计效果。'
                        st.rerun()
                    except (ValueError,OSError) as exc:st.error('模拟未完成：'+str(exc))
            st.caption('用相同工程条件和尝试次数，比较原搜索与偏好引导搜索。对比不替换当前设计方案。')
            if st.button('比较使用偏好前后',key='pref_compare',disabled=ctl.stage!='completed' or not records):
                try:
                    with st.spinner('正在计算两组方案，请稍候…'):ctl.compare_preferences(source)
                except (ValueError,OSError) as exc:st.error('对比未完成：'+str(exc))
            comparison=ctl.preference_comparison
            if comparison:
                from engi_agent.engineering.cn_schema import EngineeringState
                from engi_agent.engineering.preferences import PreferenceSnapshot
                frozen=PreferenceSnapshot.model_validate(comparison['snapshot'])
                origin='我的选择' if comparison['source']=='real' else '模拟选择'
                st.caption(f'以下结果依据“{origin}”的前 {frozen.version} 次评价。')
                if frozen!=snapshot:st.info('偏好已变化，重新点击“比较使用偏好前后”可更新结果。')
                names={'off':'原搜索','on':'使用偏好'}
                st.dataframe([{'设计方式':names[name],'尝试次数':r['metrics']['tested'],
                    '不同合格方案':r['metrics']['unique_passed'],
                    '最佳偏好成本':round(r['metrics']['best_score'],3) if r['metrics']['best_score'] is not None else None}
                    for name,r in comparison['results'].items()],hide_index=True,width='stretch')
                st.caption('偏好成本越低，越符合这组评价反映的取舍；不能作为不同工程任务之间的优劣排名。')
                plotted=[]
                for name,r in comparison['results'].items():
                    plotted.extend(chart_rows(EngineeringState.model_validate(r['state']),frozen,names[name]))
                scatter(plotted)
                st.download_button('下载对比记录',json.dumps(comparison,ensure_ascii=False,indent=2),
                    'preference_comparison.json','application/json',key='pref_download',on_click='ignore')
