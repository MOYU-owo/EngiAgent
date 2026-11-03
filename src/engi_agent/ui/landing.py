"""Native HTML/SVG landing with browser-local, decorative pointer interactions."""
from functools import lru_cache
import json
from pathlib import Path
import re
import streamlit as st


ASSETS=Path(__file__).with_name('landing_assets')


def plan_svg():
    """Illustrative reinforcement plan, not analysis data or selectable members."""
    xs=[110,270,430,590,750];ys=[125,245,365,485]
    parts=['''<svg class="ea-plan-svg" viewBox="0 0 860 560" role="img" aria-labelledby="ea-plan-title">
<title id="ea-plan-title">一层梁配筋平面示意，五条纵向轴线与四条横向轴线</title>
<defs><marker id="ea-dim-arrow" markerWidth="7" markerHeight="7" refX="3" refY="3" orient="auto-start-reverse"><path d="M 6 0 L 0 3 L 6 6" fill="none" stroke="currentColor" stroke-width=".8"/></marker></defs>
<g class="ea-axis-grid">''']
    for x in xs:
        parts.append(f'<line x1="{x}" y1="78" x2="{x}" y2="515"/>')
    for y in ys:
        parts.append(f'<line x1="75" y1="{y}" x2="797" y2="{y}"/>')
    parts.append('</g><g class="ea-axis-labels">')
    for i,x in enumerate(xs,1):
        parts.append(f'<circle cx="{x}" cy="32" r="13"/><text x="{x}" y="37">{i}</text>')
    for label,y in zip('DCBA',ys):
        parts.append(f'<circle cx="32" cy="{y}" r="13"/><text x="32" y="{y+5}">{label}</text>')
    parts.append('</g><g class="ea-plan-dimensions">')
    for i in range(4):
        a,b=xs[i:i+2]
        parts.append(f'<path d="M {a} 50 V 116 M {b} 50 V 116"/><line class="ea-dim" x1="{a}" y1="91" x2="{b}" y2="91"/><text x="{(a+b)/2}" y="84">6000</text>')
    parts.append('<line class="ea-dim" x1="110" y1="62" x2="750" y2="62"/><text x="430" y="55">24000</text>')
    for a,b in zip(ys,ys[1:]):
        parts.append(f'<line class="ea-dim" x1="65" y1="{a}" x2="65" y2="{b}"/><text transform="translate(56 {(a+b)/2}) rotate(-90)">6000</text>')
    parts.append('</g><g class="ea-plan-members">')
    for y in ys:
        parts.append(f'<rect x="110" y="{y-4}" width="640" height="8"/>')
    for x in xs:
        parts.append(f'<rect x="{x-4}" y="125" width="8" height="360"/>')
    parts.append('</g><g class="ea-plan-detail">')
    for row,y in enumerate(ys[:3]):
        for col in range(4):
            x=(xs[col]+xs[col+1])/2
            parts.append(f'<text x="{x}" y="{y+25}">L{row*4+col+1}　300×550<tspan x="{x}" dy="16">4Φ20; 2Φ16</tspan></text>')
    for col,x in enumerate(xs[:4]):
        for row in range(3):
            y=(ys[row]+ys[row+1])/2
            parts.append(f'<text transform="translate({x+21} {y}) rotate(-90)">KL{col*3+row+1} 250×500</text>')
    parts.append('</g><g class="ea-plan-columns">')
    for x in xs:
        for y in ys:parts.append(f'<rect x="{x-9}" y="{y-9}" width="18" height="18"/>')
    parts.append('''</g><g class="ea-plan-guides" aria-hidden="true">
<line class="ea-guide-column" x1="430" y1="79" x2="430" y2="515"/>
<line class="ea-guide-row" x1="75" y1="365" x2="797" y2="365"/>
<line class="ea-crosshair-horizontal" x1="75" y1="300" x2="797" y2="300"/>
<line class="ea-crosshair-vertical" x1="400" y1="79" x2="400" y2="515"/>
<rect class="ea-crosshair-center" x="396" y="296" width="8" height="8"/>
</g></svg>''')
    return ''.join(parts)


@lru_cache(maxsize=1)
def cover_html():
    markup='''<section id="engiagent-home" class="ea-native-home" data-ea-home aria-labelledby="ea-hero-title">
<header class="ea-hero-nav">
<a class="ea-hero-brand" href="#engiagent-home" target="_self" aria-label="EngiAgent 首页"><svg viewBox="0 0 76 82" aria-hidden="true"><path d="M65 17 38 3 10 18v43l28 17 28-16M65 17 29 36v13l36-17M29 49l20 10"/></svg><span>EngiAgent</span></a>
<nav aria-label="首页导航"><a href="#engineering-workbench" target="_self" aria-label="进入计算工作台">工作台</a><a href="#about-engiagent" target="_self">关于</a></nav></header>
<div class="ea-hero-visual">
<figure class="ea-plan-region"><div class="ea-plan-drawing">PLAN_SVG</div></figure>
<figure class="ea-beam-region" tabindex="0" aria-label="梁剖切示意图，悬停或聚焦可放大">
<div class="ea-beam-picture"><div class="ea-beam-photo"><img src="app/static/engiagent-cover.png" alt="钢筋混凝土梁剖切示意，展示纵筋及封闭箍筋" width="1586" height="992" fetchpriority="high" draggable="false"/></div></div>
</figure></div>
<footer class="ea-hero-footer"><h1 id="ea-hero-title">钢筋混凝土梁<br>智能设计与验算</h1>
<div class="ea-hero-description"><h2>融合规范约束的结构设计助手</h2><p>从需求输入、方案生成到独立复核，<br>让计算过程与规范依据清晰可查。</p>
<a class="ea-enter-workbench" href="#engineering-workbench" target="_self" aria-label="向下进入计算工作台"><span class="ea-enter-label">进入工作台</span><svg viewBox="0 0 30 38" aria-hidden="true"><path d="M15 2v30M3 21l12 12 12-12"/></svg></a></div></footer>
<div class="ea-hero-cursor" aria-hidden="true"><span></span></div></section>'''.replace('PLAN_SVG',plan_svg())
    # st.html's HTML-only sanitizer removes inline SVG even with JavaScript
    # enabled. Mount only these repository-owned vectors after sanitization.
    vectors=[]
    def mount(match):
        vectors.append(match.group(0).replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" ', 1))
        return f'<span data-ea-vector="{len(vectors)-1}"></span>'
    markup=re.sub(r'<svg\b.*?</svg>',mount,markup,flags=re.DOTALL)
    vector_json=json.dumps(vectors,ensure_ascii=False).replace('<',r'\u003c')
    script=(ASSETS/'landing.js').read_text(encoding='utf-8').replace('__EA_VECTORS__',vector_json)
    return '<style>'+ (ASSETS/'landing.css').read_text(encoding='utf-8')+'</style>'+markup+'<script>'+script+'</script>'


def cover():
    # Only repository-owned code is executed. Task text and model outputs never
    # enter this HTML/JavaScript. Pointer effects have no Python event bridge.
    st.html(cover_html(),unsafe_allow_javascript=True)


def about():
    st.markdown('''<section id="about-engiagent" class="ea-about" aria-labelledby="ea-about-title">
<h2 id="ea-about-title">关于 EngiAgent</h2>
<p>面向中国规范的钢筋混凝土梁设计与验算工作台。从需求输入、方案生成到独立复核，保留计算过程、规范依据与方案修订记录。</p>
<p>当前支持简支矩形梁、全跨均布恒活载和单层受拉配筋，检查抗弯、抗剪、适用构造、裂缝与长期挠度。实际支承、节点及施工图仍需工程师复核。</p>
<a href="#engineering-workbench" target="_self">返回计算工作台 ↑</a></section>''',unsafe_allow_html=True)
