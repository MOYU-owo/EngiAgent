"""Small extension of the existing workbench; all plotted results are verified."""
from itertools import combinations
import json
import streamlit as st
from engi_agent.engineering.preferences import PreferenceStore,pool,score,nondominated,NAMES


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
        'layer':[{'mark':{'type':'point','filled':True,'size':90},'encoding':{
            'x':{'field':'height','type':'quantitative','title':'梁高 / mm','scale':{'zero':False}},
            'y':{'field':'steel','type':'quantitative','title':'受拉纵筋面积 / mm²','scale':{'zero':False}},
            'color':{'field':'group','type':'nominal','title':'搜索组'},
            'shape':{'field':'front','type':'nominal','title':'三维非支配集'},
            'tooltip':[{'field':k,'type':'quantitative'} for k in ('revision','height','steel','utilization','score')]}}]},width='stretch')
    st.caption('点来自已通过候选；非支配判定同时使用梁高、纵筋面积和控制利用率。二维投影不一定保留三维支配关系。')


def preference_panel(ctl):
    state=ctl.result
    if not state or state.request.task_type!='new_design':return
    with st.expander('工程师偏好学习 · 成对评价与引导搜索',expanded=False):
        source=st.radio('评价来源',['real','simulated'],format_func=lambda x:'真实工程师' if x=='real' else '模拟工程师 · 合成数据',horizontal=True,key='pref_source')
        store=PreferenceStore(source)
        try:snapshot,records=store.load()
        except (ValueError,OSError) as exc:
            st.error('偏好文件不可用：'+str(exc));return
        st.caption(f'独立来源：{source} · 版本 {snapshot.version} · 固定归一化：1000mm / 1000mm² / 1；评分越低越符合偏好。')
        if snapshot.version==0:st.caption('尚无评价，当前为等权初值，尚未学习。')
        st.dataframe([{'维度':n,'权重':w} for n,w in zip(NAMES,snapshot.weights)],hide_index=True,width='stretch')
        st.caption('JSON仅支持本地单写入者。部署云端/多用户时须改进并发存储、身份隔离和备份。')
        enabled=st.checkbox('下一次设计开启偏好引导',value=ctl.draft.request.preference_guidance,key='pref_enabled')
        if st.button('将偏好设置写入待确认任务',key='pref_apply'):
            ctl.configure_preference(enabled,source);st.rerun()
        items=pool(state);mapping={i['id']:i for i in items}
        label=lambda key:f"修订 {mapping[key]['revision']} · {mapping[key]['raw'][0]:g}mm · As {mapping[key]['raw'][1]:.1f} · 利用率 {mapping[key]['raw'][2]:.3f}"
        if len(items)>=2 and source=='real':
            left=st.selectbox('方案 A',list(mapping),format_func=label,key='pref_left')
            right=st.selectbox('方案 B',[k for k in mapping if k!=left],format_func=label,key='pref_right')
            a,b=st.columns(2)
            choice=None
            if a.button('更喜欢 A',key='pref_choose_a',disabled=ctl.stage!='completed'):choice=left
            if b.button('更喜欢 B',key='pref_choose_b',disabled=ctl.stage!='completed'):choice=right
            if choice:
                try:store.evaluate(state,left,right,choice,snapshot.version);st.rerun()
                except ValueError as exc:st.error(str(exc))
        elif source=='simulated':
            st.info('模拟判断仅使用隔离的预设规则；学习器只接收选择，不接收隐藏规则或分数。模拟记录不会写入真实偏好。')
            if st.button('模拟20次成对评价',key='pref_simulate',disabled=len(items)<2 or ctl.stage!='completed'):
                try:simulate_evaluations(state);st.rerun()
                except ValueError as exc:st.error(str(exc))
        else:st.info('至少需要两个已通过且特征不同的候选。')
        if records:
            st.dataframe([{'版本':r['version'],'来源':r['source'],'A修订':r['left']['revision'],'B修订':r['right']['revision'],
                           '选择': 'A' if r['chosen_id']==r['left']['id'] else 'B','更新后权重':str(tuple(round(w,4) for w in r['after']))} for r in records[-30:]],hide_index=True,width='stretch')
        if st.button('同预算比较：关闭 / 开启偏好引导',key='pref_compare',disabled=ctl.stage!='completed'):
            with st.spinner('使用原工程工具计算两个独立搜索，默认不调用云端模型…'):ctl.compare_preferences(source)
        comparison=ctl.preference_comparison
        if comparison:
            from engi_agent.engineering.cn_schema import EngineeringState
            from engi_agent.engineering.preferences import PreferenceSnapshot
            frozen=PreferenceSnapshot.model_validate(comparison['snapshot'])
            st.caption(f"该对照使用 {comparison['source']} 版本 {frozen.version}；更新评价后需重新运行对照。")
            st.dataframe([{'组别':'关闭' if name=='off' else '开启','候选验算次数':r['metrics']['tested'],
                           '通过次数':r['metrics']['passed'],'不同通过方案':r['metrics']['unique_passed'],
                           '最低偏好评分':r['metrics']['best_score']} for name,r in comparison['results'].items()],hide_index=True,width='stretch')
            plotted=[]
            for name,r in comparison['results'].items():plotted.extend(chart_rows(EngineeringState.model_validate(r['state']),frozen,name))
            scatter(plotted)
            st.download_button('下载偏好搜索对照 JSON',json.dumps(comparison,ensure_ascii=False,indent=2),'preference_comparison.json','application/json',key='pref_download',on_click='ignore')
        else:scatter(chart_rows(state,snapshot,'当前已验算候选'))
