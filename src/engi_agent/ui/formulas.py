"""Read-only LaTeX transcriptions of existing cn_tools and its documented assumptions.

No evaluation of these expressions occurs in the UI. Values come from ToolResult.
"""
FORMULAS={
 'materials': [r'f_c,\ f_t,\ f_{tk},\ E_c,\ f_y,\ f_{yv},\ E_s\quad\text{按确认牌号查表}',
               r'\xi_b=\frac{\beta_1}{1+f_y/(E_s\varepsilon_{cu})},\quad\alpha_1=1,\ \beta_1=0.8'],
 'section_sizing':[r'h_{\mathrm{trial}}=25\left\lceil\frac{L}{12\times25}\right\rceil,\quad b_{\mathrm{trial}}=25\left\lceil\frac{0.5h}{25}\right\rceil\quad\text{（缺尺寸时的经验初选）}'],
 'section_geometry':[r'h_0=h-c-d_{sv}-\frac{d}{2},\qquad A_{s1}=\frac{\pi d^2}{4},\qquad I_g=\frac{bh^3}{12}'],
 'load_combination':[r'g_{\mathrm{add}}=\gamma_c\frac{bh}{10^6}\quad\text{仅输入恒载未含自重时另计}',
                     r'q_d=1.3G_k+1.5Q_k,\quad q_k=G_k+Q_k,\quad q_q=G_k+\psi_qQ_k',
                     r'q_f=G_k+\psi_fQ_k,\quad q_c=G_k+\psi_cQ_k'],
 'beam_analysis':[r'M_{\max}=\frac{qL^2}{8},\quad R_A=R_B=\frac{qL}{2},\quad V(x)=q\left(\frac L2-x\right)',
                  r'V_{\mathrm{edge}}=\frac{q(L-b_s)}2\quad\text{（已给支座宽度时）}'],
 'demand':[r'M_d=M_{\mathrm{user}}\ \text{或}\ M_{\mathrm{analysis}},\qquad V_d=V_{\mathrm{user}}\ \text{或}\ V_{\mathrm{analysis}}'],
 'flexural_design':[r'x=h_0-\sqrt{h_0^2-\frac{2M_d}{\alpha_1 f_cb}},\quad A_{s,\mathrm{req}}=\max\left(\frac{\alpha_1f_cbx}{f_y},A_{s,\min}\right)',
                    r'A_{s,\min}=\max\left(0.002,\frac{0.45f_t}{f_y}\right)bh,\quad n=\max\left(2,n_{\mathrm{trial}},\left\lceil\frac{A_{s,\mathrm{req}}}{A_{s1}}\right\rceil\right)'],
 'flexural_check':[r'A_s=nA_{s1},\quad x=\frac{f_yA_s}{\alpha_1 f_cb},\quad M_u=\alpha_1 f_cbx\left(h_0-\frac x2\right)',
                   r'M_d\le M_u,\quad x\le\xi_bh_0,\quad A_s\ge\max\left(0.002,\frac{0.45f_t}{f_y}\right)bh'],
 'shear_design':[r'V_c=0.7f_tbh_0,\quad V_{cs}=V_c+f_{yv}\frac{A_{sv}}s h_0,\quad A_{sv}=n_{sv}\frac{\pi d_{sv}^2}{4}',
                 r'\left(\frac{A_{sv}}s\right)_{\min}=\begin{cases}0.24f_tb/f_{yv}&V_d>V_c\\0&V_d\le V_c\end{cases}',
                 r's=10\left\lfloor\frac{\min(s_{\max},A_{sv}/(A_{sv}/s)_{\mathrm{req}})}{10}\right\rfloor\quad\text{需求为0时采用间距上限}'],
 'shear_check':[r'V_d\le V_{cs}=0.7f_tbh_0+f_{yv}\frac{A_{sv}}s h_0,\quad V_d\le k\beta_c f_cbh_0',
                r'k=\begin{cases}0.25&r\le4\\0.25-0.025(r-4)&4<r\le6\end{cases},\quad r=h_0/b,\quad \beta_c=1'],
 'detailing_check':[r'a_{\mathrm{clear}}=\frac{b-2(c+d_{sv})-nd}{n-1}\ge\max\left(25,d,\frac{4D_{\mathrm{agg}}}{3}\right)',
                    r'l_a=\max\left(0.14\frac{f_y}{f_t}d\,\zeta_a,200\right),\quad\zeta_a=\begin{cases}1.1&d>25\\1&d\le25\end{cases}',
                    r'h_w=h_0\ge450\ \Longrightarrow\ A_{s,\mathrm{side,each}}\ge0.001bh_w,\quad s_{\mathrm{side}}\le200'],
 'crack_check':[r'M_q=\frac{q_qL^2}{8},\quad\sigma_s=\frac{M_q}{0.87h_0A_s},\quad A_{te}=0.5bh',
                r'\rho_{te}=\max\left(\frac{A_s}{A_{te}},0.01\right),\quad\psi=\operatorname{clamp}\left(1.1-\frac{0.65f_{tk}}{\rho_{te}\sigma_s},0.2,1\right)',
                r'w_{\max}=1.9\psi\frac{\sigma_s}{E_s}\left(1.9c_s+\frac{0.08d_{eq}}{\rho_{te}}\right)\le w_{\lim}',
                r'c_s=\operatorname{clamp}(c+d_{sv},20,65),\qquad d_{eq}=d'],
 'deflection_check':[r'\rho=\frac{A_s}{bh_0},\quad\alpha_E=\frac{E_s}{E_c},\quad B_s=\frac{E_sA_sh_0^2}{1.15\psi+0.2+6\alpha_E\rho}',
                     r'B=\frac{B_s}{\theta},\quad\theta=2,\quad f=\frac{5q_qL^4}{384B}\le\frac L{r_{\lim}}',
                     r'\rho_{te}=\frac{A_s}{0.5bh}\quad\text{刚度中的}\ \psi\ \text{采用原始配筋率，不套裂缝专用0.01下限}'],
}
NOTES={
 'shear_check':'受剪截面比值大于6是当前工具边界；最大间距按实际梁高及剪力分档，结果中列出。',
 'shear_design':'跨内同间距；支座锚固区另按确认间距。最小候选间距50mm。',
 'detailing_check':'一般充分受拉直锚的保守方案；上筋净距、保护层、架立筋、锚固区箍筋等其余条件见实际输出和假定。不宜类条文按项目接受准则检查。',
 'crack_check':'采用准永久组合；零荷载显式返回零裂缝。钢筋应力超过模型范围时工具失败。',
 'deflection_check':'准永久组合，矩形等截面采用跨中控制刚度；不计上部架立筋有利作用。限值取表3.4.3及用户要求中较严格者。',
 'demand':'用户输入必须是已经确认的设计内力，不再次乘荷载分项系数；该工具输出标明实际来源。',
}
