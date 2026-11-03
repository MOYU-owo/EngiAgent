"""Math presentation preserves values; suggestions depend on recorded outcomes."""
import pytest
from engi_agent.ui.expert_content import answer_blocks,suggested_questions
from engi_agent.ui.service import WorkbenchSession,load_case


def state(case='已有梁独立验算'):
    s=WorkbenchSession();s.load(load_case(case),case);s.confirm();s.run('program');return s.result


def test_standard_latex_delimiters_are_rendered_without_exposing_commands():
    source=r'应变系数 \(\psi\) 用于刚度。'+ '\n'+r'\[B_s=\frac{E_s A_s h_0^2}{1.15\psi+0.2}\]'
    blocks=answer_blocks(source)
    assert any(kind=='markdown' and r'$\psi$' in value for kind,value in blocks)
    assert ('latex',r'B_s=\frac{E_s A_s h_0^2}{1.15\psi+0.2}') in blocks


def test_dollar_math_keeps_nested_brackets_and_parentheses_unchanged():
    expression=r'B=\operatorname{clamp}(\psi,0.2,1)\left[1+\frac{a}{b}\right]'
    assert ('latex',expression) in answer_blocks('$$'+expression+'$$')
    assert '$'+expression+'$' in ''.join(value for _,value in answer_blocks('$'+expression+'$'))


def test_legacy_math_is_repaired_but_markdown_links_and_literal_code_are_preserved():
    source=r'系数(\theta)。[B_s=\frac{a}{b}] [规范](https://example.com) `\(literal\)`'
    blocks=answer_blocks(source)
    assert ('latex',r'B_s=\frac{a}{b}') in blocks
    text=''.join(value for kind,value in blocks if kind=='markdown')
    assert r'$\theta$' in text and '[规范](https://example.com)' in text
    assert r'`\(literal\)`' in text
    assert answer_blocks('```text\n\\[literal\\]\n```')==[('markdown','```text\n\\[literal\\]\n```')]


def test_list_spacing_and_escaped_currency_are_retained():
    text=''.join(value for _,value in answer_blocks('1.**刚度**\n2、组合\n费用\\$100'))
    assert '1. **刚度**' in text and '2. 组合' in text and r'\$100' in text


def test_suggestions_prioritize_failed_checks_and_change_with_follow_up():
    failed=state('改设达到上限停止')
    questions=suggested_questions(failed)
    assert '裂缝' in questions[0] and '不通过' in questions[0]
    passing=state()
    assert '不通过' not in suggested_questions(passing)[0]
    assert suggested_questions(passing,[{'query':'什么是准永久组合'}])[-1].startswith('准永久组合')
    assert '锚固' in suggested_questions(passing,[{'query':'用钢量多少'}])[-1]
    assert len(questions)==len(set(questions))==3
