"""Render numeric substitutions as LaTeX via an AST whitelist, without evaluation."""
import ast
import math
import re

FORMULAS={
 '实配钢筋面积':r'A_s=n A_1',
 '有效高度':r'h_0=h-c-d_{sv}-d/2',
 '单根纵筋面积':r'A_1=\pi d^2/4',
 '单肢箍筋面积':r'A_{sv,1}=\pi d_{sv}^2/4',
 '毛截面惯性矩':r'I=bh^3/12',
 '界限相对受压区高度':r'\xi_b=\frac{\beta_1}{1+f_y/(E_s\varepsilon_{cu})}',
 '受压区高度':r'x=\frac{f_yA_s}{\alpha_1f_cb}',
 '受压区上限':r'x_b=\xi_b h_0',
 '最小配筋面积':r'A_{s,\min}=\max(0.002,0.45f_t/f_y)bh',
 '抗弯承载力':r'M_u=f_y A_s(h_0-x/2)/10^6',
 '受弯比较':r'M\le M_u,\quad A_s\ge A_{s,\min},\quad x\le x_b',
 '钢筋应力':r'\sigma_s=\frac{M_q\times10^6}{0.87h_0 A_s}',
 '有效受拉区配筋率':r'\rho_{te,0}=\frac{A_s}{0.5bh},\quad\rho_{te,\mathrm{crack}}=\max(\rho_{te,0},0.01)',
 '应变不均匀系数':r'\psi=\operatorname{clamp}\!\left(1.1-\frac{0.65 f_{tk}}{\rho_{te}\sigma_s},0.2,1\right)',
 '保护层距离':r'c_s=\operatorname{clamp}(c+d_{sv},20,65)',
 '裂缝宽度':r'w_{\max}=1.9\psi\frac{\sigma_s}{E_s}\!\left(1.9c_s+\frac{0.08d_{eq}}{\rho_{te}}\right)',
 '裂缝比较':r'w_{\max}\le w_{\lim}',
 '截面配筋率':r'\rho=\frac{A_s}{bh_0}',
 '短期刚度':r'B_s=\frac{E_sA_sh_0^2}{1.15\psi+0.2+6(E_s/E_c)\rho}',
 '长期刚度':r'B=B_s/\theta',
 '长期挠度':r'f=\frac{5q_qL^4}{384B}',
 '挠度限值':r'f_{\lim}=L/r_{\lim}',
 '挠度比较':r'f\le f_{\lim}',
 '设计弯矩':r'M=qL^2/8', '标准弯矩':r'M_k=q_kL^2/8', '准永久弯矩':r'M_q=q_qL^2/8',
 '支座中心剪力':r'V=qL/2', '支座边缘剪力':r'V=q(L-b_{\mathrm{support}})/2',
 '恒载合计':r'G_k=G_{\mathrm{input}}+g_{\mathrm{self}}',
 '另计自重':r'g_{\mathrm{self}}=\gamma_c bh/10^6',
 '承载力组合':r'q_u=1.3G_k+1.5Q_k', '准永久组合':r'q_q=G_k+\psi_qQ_k',
 '标准组合':r'q_k=G_k+Q_k', '频遇组合':r'q_f=G_k+\psi_fQ_k', '组合值':r'q_c=G_k+\psi_cQ_k',
 '混凝土抗剪贡献':r'V_c=0.7f_tbh_0/1000',
 '受剪截面上限':r'V_{\max}=\beta f_cbh_0/1000',
 '箍筋肢面积合计':r'A_{sv}=n_{\mathrm{legs}}A_{sv,1}',
 '受剪承载力':r'V_u=V_c+f_{yv}(A_{sv}/s)h_0/1000',
 '需求配箍':r'A_{sv}/s\ge\max\left((A_{sv}/s)_{\min},\frac{\max(0,V-V_c)10^3}{f_{yv}h_0}\right)',
 '下部净距':r's_{\mathrm{net}}=\frac{b-2(c+d_{sv})-nd}{n-1}',
 '上部纵筋净距':r's_{\mathrm{net,top}}=\frac{b-2(c+d_{sv})-n_{\mathrm{top}}d_{\mathrm{top}}}{n_{\mathrm{top}}-1}',
 '最小净距':r's_{\min}=\max(25,d,4D_{\mathrm{agg}}/3)',
 '直锚需求':r'l_a=\max(200,0.14(f_y/f_t)d\zeta_a)',
 '每侧腰筋面积':r'A_{s,\mathrm{side}}=n_{\mathrm{side}}\pi d_{\mathrm{side}}^2/4',
 '每侧腰筋需求':r'h_0\ge450\Rightarrow A_{s,\mathrm{side}}\ge0.001bh_0',
}


def numeric_latex(expression):
    """None for prose or unsupported syntax; never execute the input expression."""
    if len(expression)>2000:return None
    comparison=re.fullmatch(r'\s*([-+0-9.eE]+)\s*([≤≥])\s*([-+0-9.eE]+)\s*',expression)
    if comparison:
        try:
            left=float(comparison[1]);right=float(comparison[3])
            if not math.isfinite(left) or not math.isfinite(right):return None
            return f'{left:.8g}'+(r'\le ' if comparison[2]=='≤' else r'\ge ')+f'{right:.8g}'
        except ValueError:return None
    expression=expression.replace('×','*').replace('²','**2').replace('³','**3').replace('⁴','**4').replace('⁶','**6').replace('π','pi').replace('⁻','-')
    def render(node,depth=0):
        if depth>40:raise ValueError('too deep')
        child=lambda n:render(n,depth+1)
        if isinstance(node,ast.Constant) and type(node.value) in (int,float) and math.isfinite(node.value):
            text=f'{node.value:.8g}'
            if 'e' in text:
                a,b=text.split('e');return a+r'\times10^{'+str(int(b))+'}'
            return text
        if isinstance(node,ast.Name) and node.id=='pi':return r'\pi'
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):
            return ('-' if isinstance(node.op,ast.USub) else '+')+child(node.operand)
        if isinstance(node,ast.BinOp):
            l,r=child(node.left),child(node.right)
            if isinstance(node.op,ast.Div):return r'\frac{'+l+'}{'+r+'}'
            if isinstance(node.op,ast.Pow):return (r'\left('+l+r'\right)' if isinstance(node.left,ast.BinOp) else l)+'^{'+r+'}'
            op={ast.Add:'+',ast.Sub:'-',ast.Mult:r'\times'}.get(type(node.op))
            if op:
                if isinstance(node.op,ast.Mult):
                    if isinstance(node.left,ast.BinOp) and isinstance(node.left.op,(ast.Add,ast.Sub)):l=r'\left('+l+r'\right)'
                    if isinstance(node.right,ast.BinOp) and isinstance(node.right.op,(ast.Add,ast.Sub)):r=r'\left('+r+r'\right)'
                elif isinstance(node.right,ast.BinOp) and isinstance(node.op,ast.Sub):r=r'\left('+r+r'\right)'
                return l+op+r
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in ('max','min','clamp') and not node.keywords:
            return r'\operatorname{'+node.func.id+r'}\!\left('+','.join(child(a) for a in node.args)+r'\right)'
        raise ValueError('unsupported syntax')
    try:return render(ast.parse(expression.strip(),mode='eval').body)
    except (ValueError,SyntaxError,RecursionError,OverflowError):return None


def step_formula(row):
    return FORMULAS.get(row['title'])
