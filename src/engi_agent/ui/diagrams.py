"""Data-driven SVG/DOT drawings. Geometry conversion only, no engineering checks."""
import html
import json
from .projections import LABELS


def fmt(value):
    return f'{value:,.3f}'.rstrip('0').rstrip('.') if isinstance(value,(float,int)) else str(value)


def beam_svg(parameters, candidate=None):
    p={**parameters,**(candidate or {})}
    esc=lambda text:html.escape(str(text))
    parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 350" role="img" aria-label="由实际参数生成的简支梁与截面示意">',
           '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="none" stroke="#547395"/></marker></defs>',
           '<rect width="960" height="350" fill="#fff"/>',
           '<g font-family="Microsoft YaHei,Arial,sans-serif" fill="#253d57" font-size="18">',
           '<text x="38" y="30" font-size="12" fill="#708095">立面 / ELEVATION</text>',
           '<text x="758" y="30" font-size="12" fill="#708095">截面 / SECTION</text>']
    span,b,h=p.get('span_mm'),p.get('beam_width_mm'),p.get('beam_depth_mm')
    if span and span>0:
        start,end,y=56,675,143
        height=min(95,max(8,h/span*(end-start))) if h else None
        if height:
            parts.append(f'<rect x="{start}" y="{y}" width="{end-start}" height="{height}" fill="#eaf0f7" stroke="#173e73" stroke-width="2"/>')
        else:
            parts.append(f'<line x1="{start}" y1="{y}" x2="{end}" y2="{y}" stroke="#173e73" stroke-width="2"/>')
            parts.append('<text x="230" y="180">梁高未提供，未绘制实体厚度</text>')
        sy=y+(height or 0)
        for x in (start,end):
            parts.append(f'<path d="M{x},{sy} l-15,24 h30 Z" fill="#e3eaf2" stroke="#547395"/><line x1="{x-22}" y1="{sy+30}" x2="{x+22}" y2="{sy+30}" stroke="#8d9fb1"/>')
        parts.append(f'<line x1="{start}" y1="263" x2="{end}" y2="263" stroke="#708095"/>')
        for x in (start,end):parts.append(f'<line x1="{x}" y1="255" x2="{x}" y2="271" stroke="#708095"/>')
        parts.append(f'<text x="290" y="286">L = {esc(fmt(span))} mm</text>')
        if 'dead_load_kn_m' in p and 'live_load_kn_m' in p:
            parts.append(f'<line x1="{start}" y1="91" x2="{end}" y2="91" stroke="#547395"/>')
            for i in range(15):
                x=start+(end-start)*i/14
                parts.append(f'<line x1="{x}" y1="91" x2="{x}" y2="{y-10}" stroke="#547395" marker-end="url(#arrow)"/>')
            mode={'excluded':'恒载另计梁自重','included':'恒载已含自重'}.get(p.get('self_weight_mode'),'自重约定未提供')
            parts.append(f'<text x="58" y="66">Gk = {esc(fmt(p["dead_load_kn_m"]))} kN/m · Qk = {esc(fmt(p["live_load_kn_m"]))} kN/m</text>')
            parts.append(f'<text x="58" y="318" font-size="12" fill="#708095">{mode}；支座为约束符号，图形不作为节点详图。</text>')
        else:
            parts.append('<text x="58" y="90" fill="#708095">未提供线荷载，不绘制荷载箭头</text>')
        if p.get('support_width_mm'):
            parts.append(f'<text x="58" y="237" font-size="12">支座宽 {esc(fmt(p["support_width_mm"]))} mm</text>')
    else:parts.append('<text x="90" y="165" fill="#708095">待提供实际跨度，未绘制梁立面</text>')
    if b and h and b>0 and h>0:
        scale=min(155/b,212/h); width,height=b*scale,h*scale
        x=810-width/2;y=58
        parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="#f5f7fa" stroke="#173e73" stroke-width="2"/>')
        cover,stirrup=p.get('cover_mm'),p.get('stirrup_diameter_mm')
        if cover is not None and stirrup is not None and 2*(cover+stirrup)<min(b,h):
            offset=(cover+stirrup/2)*scale
            parts.append(f'<rect x="{x+offset}" y="{y+offset}" width="{width-2*offset}" height="{height-2*offset}" rx="3" fill="none" stroke="#8b9fb5" stroke-width="{max(1,stirrup*scale)}"/>')
            for count_key,dia_key,top,color in [('bar_count','bar_diameter_mm',False,'#173e73'),('top_bar_count','top_bar_diameter_mm',True,'#6a829e')]:
                count,diam=p.get(count_key),p.get(dia_key)
                if count and diam and 2<=count<=100:
                    edge=(cover+stirrup+diam/2)*scale
                    cy=y+edge if top else y+height-edge
                    for n in range(int(count)):
                        cx=x+edge+(width-2*edge)*n/(count-1)
                        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{max(.8,diam*scale/2)}" fill="{color}"/>')
        parts.append(f'<text x="{x}" y="{y+height+25}">{esc(fmt(b))} × {esc(fmt(h))} mm</text>')
        if p.get('bar_count') and p.get('bar_diameter_mm'):
            parts.append(f'<text x="{x}" y="{y+height+49}">下部 {esc(fmt(p["bar_count"]))}Φ{esc(fmt(p["bar_diameter_mm"]))}</text>')
        else:parts.append(f'<text x="{x}" y="{y+height+49}" fill="#708095">下部配筋待确定</text>')
        parts.append('<text x="744" y="333" font-size="11" fill="#708095">腰筋未定位绘制；以参数和构造结果为准</text>')
    else:parts.append('<text x="738" y="160" fill="#708095">截面尺寸不全，暂不绘制</text>')
    return ''.join(parts+['</g></svg>'])


COLORS={'executed':('#e8f2ec','#498260'),'reuse':('#e7effa','#406b9d'),
        'pending':('#f2f4f7','#a1aab5'),'blocked':('#f5eee0','#a88440'),
        'error':('#f9e8e7','#b55b56'),'failed':('#f9e8e7','#b55b56')}
STATE_LABEL={'executed':'已执行','reuse':'缓存复用','pending':'待执行','blocked':'阻断','error':'工具错误','failed':'模型/工程失败'}


def dag_dot(nodes, selected=None):
    lines=['digraph G {','rankdir=LR; bgcolor="transparent"; pad="0.25"; nodesep="0.3"; ranksep="0.5";',
           'node [shape=box, style="rounded,filled", fontname="Microsoft YaHei", fontsize=12, margin="0.14,0.10"];',
           'edge [color="#a1afc0", arrowsize=0.65];']
    names={n['name'] for n in nodes}
    for node in nodes:
        bg,stroke=COLORS[node['state']]
        result=node.get('result')
        if result and result.outputs.get('pass') is False:bg,stroke=COLORS['failed']
        check=' · 检查不通过' if result and result.outputs.get('pass') is False else ''
        text=node['label']+'\n'+STATE_LABEL[node['state']]+check
        lines.append(f'{json.dumps(node["name"])} [label={json.dumps(text,ensure_ascii=False)}, fillcolor="{bg}", color="{stroke}", penwidth={2.8 if node["name"]==selected else 1.2}];')
        for parent in node['parents']:
            if parent in names:lines.append(f'{json.dumps(parent)} -> {json.dumps(node["name"])};')
    return '\n'.join(lines+['}'])


def agent_dot(calls, state=None):
    lines=['digraph G { rankdir=LR; bgcolor="transparent"; nodesep=0.3;',
           'node [shape=box, style="rounded,filled", fontname="Microsoft YaHei", fontsize=12, margin="0.18,0.12"];',
           'edge [color="#9aabc0", arrowsize=0.7];']
    previous=None
    for i,call in enumerate(calls):
        role=call['role']; status=call['status']; mode=call.get('mode','未记录')
        color='#f9e8e7' if status=='error' else '#e7effa'
        caption=role+'\n'+('文件读取' if mode=='structured_file' else '离线角色' if mode=='offline' else mode)+' · '+('调用完成' if status=='success' else '失败' if status=='error' else '执行中')
        lines.append(f'n{i} [label={json.dumps(caption,ensure_ascii=False)}, fillcolor="{color}", color="#9aabc0"];')
        if previous is not None:
            feedback=(' [label="工程师确认后新请求"]' if call.get('run_id')!=calls[previous].get('run_id') and calls[previous].get('run_id',0)!=0
                      else ' [label="失败反馈 / 下一轮", color="#a76b37"]' if role=='Design' and calls[previous]['role']=='Evaluation' else '')
            lines.append(f'n{previous} -> n{i}{feedback};')
        previous=i
    return '\n'.join(lines+['}'])
