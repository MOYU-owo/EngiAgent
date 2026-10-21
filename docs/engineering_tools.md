# 首轮工程工具计算说明（teaching-rc-1）

本实现为教学试算，不是中国规范或完整 ACI 实现。中国规范核验始终为未完成。
先冻结本说明，再编写计算程序。工具不执行 LLM 生成的代码。

## 来源及版本

- 用户提供的 Chen / Bao (2025) 论文第 3、4 节：参考任务参数和五步设计顺序。
- StructurePoint，2021-04-08，*Simply Supported Reinforced Concrete Beam Analysis and
  Design (ACI 318-14)*，第 2–13 页：参考截面、荷载、矩形应力块、钢筋布置、剪力公式。
  https://structurepoint.org/publication/pdf/Simply%20Supported%20Reinforced%20Concrete%20Beam%20Analysis%20and%20Design%20(ACI%20318-14).pdf
- 论文标称 ACI 318-19，原算例为 ACI 318-14；二者不混称同一规范。
- 挠度采用均布荷载简支梁 Euler–Bernoulli 弹性解，不实现原算例的开裂/长期计算。

## 单位与模型边界

外部字段按 mm、MPa、kN/m、kN·m、kN；内部截面公式用 N、mm、MPa，
弯矩乘 10^6、剪力乘 1000。kN/m 在挠度公式中数值等于 N/mm。
仅简支、矩形、正向全跨均布恒活载、单层受拉筋、竖向双肢或多肢箍筋。
fc_mpa 是参考模型混凝土圆柱抗压强度，不是中国规范轴心抗压设计值。
纵筋/箍筋分别给屈服强度；钢筋公称面积优先于由直径推导的面积。
profile 中的所有系数、材料参数、荷载及限值须显示并人工确认。

## 工具契约

所有工具返回 status（success/failed/blocked）、输入、输出、依据、警告、
错误、公式版本及输入哈希。success 只表示执行成功，判定另存 pass。
工具输入必须来自已校验且确认的工程参数或上游工具。异常阻断依赖工具。

|工具|输入|公式 / 输出|阻断或失败|
|---|---|---|---|
|section_sizing|跨度、已有/约束宽高|未给 h 时 L/16 向上取 25mm；未给 b 时 0.6h 向上取 25mm；已有尺寸保留|尺寸超过约束；不自动增大已有尺寸|
|section_geometry|b,h,保护层,箍筋与纵筋直径|d=h-cover-d_st-d_bar/2；Ig=bh³/12|d≤0；非单层|
|load_combination|截面、容重、D,L、自重约定、组合系数|excluded: Dtot=D+γbh；included: Dtot=D；ignore: 明示忽略；wu=max(γD_only Dtot,γD Dtot+γL L)，ws=Dtot+L|自重约定缺失、负荷载|
|beam_analysis|L、wu、ws、位置x|R=Vmax=wL/2，Mmax=wL²/8，V(x)=w(L/2-x)|x不在[0,L]|
|flexural_design|Mu,b,d,材料、钢筋目录|由 φAs fy(d−As fy/(2αfc b))=Mu 求较小正根；不小于最小钢筋；向上取整数根；验算实配|根不存在、单层放不下、非受拉控制|
|shear_design|V(d)、b,d,材料、箍筋面积/肢数|Vc=k_c√fc bd；Vs_req=max(V/φ−Vc,0)；Av/s同时满足承载力和最小量；s≤d/2或d/4及绝对限值；向下取5mm|超过模型最大Vs；无正可行间距|
|flexural_check|实配As、几何、Mu|a=As fy/(αfc b)，c=a/β1，εt=εcu(d−c)/c；φMn=φAs fy(d−a/2)|非受拉控制、超截面、承载力不足|
|detailing_check|实配根数、直径、面积、保护层、骨料|中心距=(b−2cover−2dst−db)/(n−1)；净距=中心距−db；净距≥max(db,25.4,4agg/3)|根数<2或间距不足；最大中心距另按参考模型检查|
|shear_check|实配箍筋、V(d)、几何|φVn=φ(Vc+Av fy d/s)，同时复核最小量、最大Vs和间距|任一控制条件失败|
|elastic_deflection|Ec,Ig,ws,L,限值分母r|δ=5ws L⁴/(384Ec Ig)，限值=L/r|Ec或限值缺失；仅弹性比较|

## 教学系数定义

teaching-rc-1：α=0.85，φ弯=0.9，φ剪=0.75，εcu=0.003，εt下限=0.005。
β1=clip(0.85−0.05(fc[psi]−4000)/1000,0.65,0.85)。仅支持 fc=17–55MPa。
为避免混用英制经验公式，令 P=145.03773773 psi/MPa，则：

- As_min=max((3/√P)√fc/fy, (200/P)/fy)bd。
- k_c=2/√P；Vs_max=(8/√P)√fc bd。
- (Av/s)_min=max((0.75/√P)√fc b/fyt, (50/P)b/fyt)。
- Vs≤(4/√P)√fc bd 时最大间距 min(d/2,609.6mm)，否则 min(d/4,304.8mm)。
- 纵筋最大中心距 min(380×280/fs−2.5cover,300×280/fs)，fs=2fy/3（教学公制近似，明确不要求与英制参考完全相同）。

仅截面承载力与有限布置检查；不含锚固、搭接、耐久性、抗震、裂缝或全套构造。
首轮箍筋全跨均布，不复现论文分区截断点及箍筋总数。

## 参考案例与独立验收

保留论文原始单位及精确换算公制数值：25ft、4.35ksi、60ksi、0.82/1.00kip/ft、
150pcf、#9(1in²,1.128in)、#3(0.11in²,0.375in)、保护层1.5in、骨料0.75in。
参考对照固定12×20in；正常示例计入自重，另一个明确 ignore 的对照不计。
0.82kip/ft 不含自重，但论文计算与忽略自重一致。正常试算不追逐该数值。
独立力学手算、精确单位换算及边界测试作为真值；表格错位和附录疑值不作为真值。
强度试算通过、弹性挠度通过仍仅能得出所实现项目通过；完整工程结论为 incomplete。
