"""Presentation-only answer formatting and state-driven question suggestions."""
import re
from engi_agent.engineering.cn_presentation import LABELS

# Keep literal code untouched; normalize only prose/math, without executing it.
CODE = re.compile(r'(```[\s\S]*?```|~~~[\s\S]*?~~~|`[^`\n]*`)')
MATH_COMMAND = re.compile(r'\\(?:frac|sqrt|psi|rho|theta|sigma|alpha|beta|gamma|delta|varepsilon|epsilon|quad|text|mathrm|sum|times|leq?|geq?)\b')


def _prose_math(text):
    text = re.sub(r'\\\[([\s\S]*?)\\\]', lambda m:'\n\n$$\n'+m[1].strip()+'\n$$\n\n', text)
    text = re.sub(r'\\\(([^\n]*?)\\\)', lambda m:'$'+m[1].strip()+'$', text)
    def repair(part):
        if part.startswith('$'):return part
        # Repair legacy answers without changing already-delimited math.
        part = re.sub(r'(?<![\\$])\[([^\[\]]*?)\](?!\()',
            lambda m:'\n\n$$\n'+m[1].strip()+'\n$$\n\n' if MATH_COMMAND.search(m[1]) else m[0],part)
        part = re.sub(r'(?<![\\$])\(([^()\n]*?)\)',
            lambda m:'$'+m[1].strip()+'$' if MATH_COMMAND.search(m[1]) else m[0],part)
        return re.sub(r'(?m)^(\s*\d+)[.、](?=\S)', r'\1. ', part)
    parts=re.split(r'(\$\$[\s\S]*?\$\$|(?<!\\)\$(?!\$)[^\n$]*?(?<!\\)\$)',text)
    return ''.join(repair(part) for part in parts)


def answer_blocks(answer):
    """Return Markdown and display-math blocks; math content remains verbatim."""
    blocks=[]
    def append(kind,value):
        if value and (value.strip() or kind=='markdown'):
            if kind=='markdown' and blocks and blocks[-1][0]=='markdown':
                blocks[-1]=('markdown',blocks[-1][1]+value)
            else:blocks.append((kind,value))
    for part in CODE.split(answer):
        if not part:continue
        if CODE.fullmatch(part):
            append('markdown',part)
            continue
        part=_prose_math(part)
        cursor=0
        for match in re.finditer(r'(?<!\\)\$\$([\s\S]*?)(?<!\\)\$\$',part):
            append('markdown',part[cursor:match.start()])
            append('latex',match[1].strip())
            cursor=match.end()
        append('markdown',part[cursor:])
    return blocks


def suggested_questions(state, consultations=()):
    """Select prompts from actual verdicts, requested scope and recent questions.

    No model calls, numerical predictions, edits, or automatic submissions.
    """
    questions=[]
    for target,passed in state.evaluation.checks.items():
        if not passed:
            questions.append('当前'+LABELS.get(target,target)+'为什么不通过，可以从哪些方面改进？')
    if state.evaluation.status=='error':questions.append('当前计算为什么没有完成，哪些结果不能使用？')
    if not questions:
        questions.append('为什么抗弯通过仍可能挠度超限？' if 'deflection' in state.request.targets
                         else '本次只做了哪些检查，还缺哪些正常使用检查？')
    questions.append('当前实配参数和用钢量是多少？')
    recent=consultations[-1].get('query','') if consultations else ''
    if '准永久' in recent:
        follow='准永久组合如何影响当前梁的裂缝与挠度？'
    elif any(word in recent for word in ('用钢','钢量','重量')):
        follow='上述用钢量包含锚固、箍筋和上部钢筋吗？'
    elif any(word in recent for word in ('裂缝','挠度')):
        follow='哪些参数会影响当前裂缝和挠度，两者可能有什么取舍？'
    elif any(t.get('action')=='reuse' for t in state.plan_trace):
        follow='这次修改后，哪些结果得到了复用，为什么？'
    else:follow='什么是准永久组合，它在当前计算中有什么作用？'
    # Keep one slot for a contextual follow-up even when several checks failed.
    return list(dict.fromkeys(questions[:2]+[follow]))
