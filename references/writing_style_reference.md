# 生成模型的前世今生：从 GAN 到 Diffusion、DiT/MMDiT 与跨领域生成

基于论文深度笔记整理

2026 年 5 月 19 日

## ㅅ⿆

0.1 如何阅读这本讲义 8
第1章 生成模型前史：为什么 diffusion 会赢到今天 9
1.1 本章要解决的问题 9
1.2 技术背景 9
1.3 核心方法 10
1.3.1 1. VAE: 把隐变量推断变成可微下界 10
1.3.2 2. GAN/WGAN: 把真实感交给可学习评价器 11
1.3.3 3. 自回归图像模型：把图片当成序列 11
1.3.4 4. Flow: 用可逆变换换 exact likelihood 12
1.4 关键公式或伪代码 12
1.5 关键架构图 / 方法图拆解 13
1.6 该方向的痛点 15
1.7 核心 insight 15
1.8 实验结论 16
1.9 局限与未来工作 16
1.10 读完这一章应该掌握什么 16
1.11 复习问题 17
第2章 扩散模型基础：从 DDPM 到 Score SDE、EDM 与 Flow Matching 18
2.1 本章要解决的问题 18
2.2 技术背景 18
2.3 核心方法 19
2.3.1 1. DDPM: 预测噪声 19
2.3.2 2. Classifier guidance 与 CFG: 采样阶段施加条件 19
2.3.3 3. Score SDE: 连续时间统一 20
2.3.4 4. EDM: 把扩散设计空间坐标化 20

## 目录

2.3.5 5. Flow Matching / Rectified Flow: 学习速度场 ..... 21
2.4 关键公式或伪代码 ..... 21
2.5 关键架构图 / 方法图拆解 ..... 23
2.6 该方向的痛点 ..... 25
2.7 核心 insight ..... 25
2.8 实验结论 ..... 26
2.9 局限与未来工作 ..... 26
2.10 读完这一章应该掌握什么 ..... 26
2.11 复习问题 ..... 27

第3章 文生图系统：从 GLIDE、DALL-E 2、Imagen 到 Stable Diffusion 与 SD3 ..... 28
3.1 本章要解决的问题 ..... 28
3.2 技术背景 ..... 28
3.3 核心方法 ..... 29
3.3.1 1. GLIDE: 文本条件 diffusion 与 guidance 选择 ..... 29
3.3.2 2. DALL-E 2 / unCLIP: 先生成 CLIP 图像语义，再解码成图 ..... 29
3.3.3 3. Imagen: 语言编码器比想象中更重要 ..... 29
3.3.4 4. Latent Diffusion: 把计算搬到 perceptual latent ..... 30
3.3.5 5. SDXL: 把 LDM 做成工程化大系统 ..... 30
3.3.6 6. SD3: rectified flow + MMDiT 的转向 ..... 30
3.4 关键公式或伪代码 ..... 31
3.5 关键架构图 / 方法图拆解 ..... 31
3.6 该方向的痛点 ..... 34
3.7 核心 insight ..... 34
3.8 实验结论 ..... 34
3.9 局限与未来工作 ..... 35
3.10 读完这一章应该掌握什么 ..... 35
3.11 复习问题 ..... 35

第4章 DiT、MMDiT 与 Transformer 化 diffusion ..... 36
4.1 本章要解决的问题 ..... 36
4.2 技术背景 ..... 36

4.3 核心方法 37
4.3.1 1. DiT: latent patches + Transformer blocks 37
4.3.2 2. U-ViT 与 MDT: 把 U-Net 经验带回 Transformer 37
4.3.3 3. PixArt: 训练成本工程化 37
4.3.4 4. Hunyuan-DiT、Lumina、Sana: 高效化和多语言系统 37
4.3.5 5. MMDiT 与 E-MMDiT: 文本图像 token 的深交互和高效化 38
4.4 关键公式或伪代码 38
4.5 关键架构图 / 方法图拆解 39
4.6 该方向的痛点 43
4.7 核心 insight 43
4.8 实验结论 44
4.9 局限与未来工作 44
4.10 读完这一章应该掌握什么 44
4.11 复习问题 44

第5章 采样、蒸馏与对齐：如何让 diffusion 更快、更符合偏好 46
5.1 本章要解决的问题 46
5.2 技术背景 46
5.3 核心方法 47
5.3.1 1. Training-free sampler: 不改权重，改路径离散化 47
5.3.2 2. Progressive Distillation / Consistency / LCM: 把多步老师压进少步学生 47
5.3.3 3. ADD: 用 adversarial loss 补少步细节 47
5.3.4 4. DDPO / Diffusion-DPO / SPIN: 从好看图到偏好对齐 47
5.4 关键公式或伪代码 48
5.5 关键架构图 / 方法图拆解 49
5.6 该方向的痛点 51
5.7 核心 insight 52
5.8 实验结论 52
5.9 局限与未来工作 52
5.10 读完这一章应该掌握什么 52

目录

5.11 复习问题 ..... 52

第6章 控制、编辑与个性化：从 SDEdit 到 ControlNet、IP-Adapter
6.1 本章要解决的问题 ..... 54
6.2 技术背景 ..... 54
6.3 核心方法 ..... 55
6.3.1 1. SDEdit: 加噪再生成，平衡保真和真实感 ..... 55
6.3.2 2. Textual Inversion / DreamBooth: 把新主体放进模型词汇 ..... 55
6.3.3 3. Prompt-to-Prompt: 编辑 cross-attention ..... 55
6.3.4 4. GLIGEN / ControlNet / T2I-Adapter: 把空间条件接进模型 ..... 55
6.3.5 5. IP-Adapter: 把 image prompt 作为独立条件通道 ..... 55
6.4 关键公式或伪代码 ..... 56
6.5 关键架构图 / 方法图拆解 ..... 56
6.6 该方向的痛点 ..... 59
6.7 核心 insight ..... 59
6.8 实验结论 ..... 59
6.9 局限与未来工作 ..... 59
6.10 读完这一章应该掌握什么 ..... 60
6.11 复习问题 ..... 60

第7章 跨媒体生成：音频、视频、3D 与多媒体 foundation models
7.1 本章要解决的问题 ..... 61
7.2 技术背景 ..... 61
7.3 核心方法 ..... 62
7.3.1 1. 音频：从波形去噪到音频 latent diffusion ..... 62
7.3.2 2. 视频：时间层、级联与 latent 化 ..... 62
7.3.3 3. 3D: 用二维先验约束三维对象 ..... 63
7.4 关键公式或伪代码 ..... 63
7.5 关键架构图 / 方法图拆解 ..... 65
7.6 该方向的痛点 ..... 70
7.7 核心 insight ..... 71
7.8 实验结论 ..... 71

7.9 局限与未来工作 ..... 71
7.10 读完这一章应该掌握什么 ..... 72
7.11 复习问题 ..... 72

第8章 具身与决策：diffusion 如何生成轨迹、动作和 VLA ..... 73
8.1 本章要解决的问题 ..... 73
8.2 技术背景 ..... 73
8.3 核心方法 ..... 74
8.3.1 1. Diffuser：把轨迹当作图像一样去噪 ..... 74
8.3.2 2. Decision Diffuser：把奖励、目标和技能作为条件 ..... 74
8.3.3 3. Diffusion Policy：从轨迹规划转为动作 chunk 控制 ..... 74
8.3.4 4. DP3：让 diffusion policy 直接看 3D 点云 ..... 75
8.3.5 5. RDT-1B：大规模 robot diffusion transformer ..... 75
8.3.6 6. pi0：VLM + flow action expert ..... 75
8.4 关键公式或伪代码 ..... 75
8.5 关键架构图 / 方法图拆解 ..... 76
8.6 该方向的痛点 ..... 79
8.7 核心 insight ..... 79
8.8 实验结论 ..... 79
8.9 局限与未来工作 ..... 80
8.10 读完这一章应该掌握什么 ..... 80
8.11 复习问题 ..... 80

第9章 AI4Science：分子、蛋白、材料与天气中的结构生成 ..... 81
9.1 本章要解决的问题 ..... 81
9.2 技术背景 ..... 81
9.3 核心方法 ..... 82
9.3.1 1. 晶体材料：CDVAE 与 MatterGen ..... 82
9.3.2 2. 分子构象：GeoDiff 与 Equivariant Diffusion ..... 82
9.3.3 3. Docking：DiffDock 的姿态分布 ..... 83
9.3.4 4. 蛋白生成：从角度到 frame，再到 RFdiffusion ..... 83
9.3.5 5. 天气与时空场：GenCast ..... 83

## 目录

9.4 关键公式或伪代码 ..... 84
9.5 关键架构图 / 方法图拆解 ..... 85
9.6 该方向的痛点 ..... 89
9.7 核心 insight ..... 90
9.8 实验结论 ..... 90
9.9 局限与未来工作 ..... 91
9.10 读完这一章应该掌握什么 ..... 91
9.11 复习问题 ..... 91

第 10 章 评测、安全、高效化与未来路线 ..... 92
10.1 本章要解决的问题 ..... 92
10.2 技术背景 ..... 92
10.3 核心方法 ..... 93
10.3.1 1. 组合评测：从“像不像”到“有没有按话做” ..... 93
10.3.2 2. 视频评测：要看时间维度 ..... 93
10.3.3 3. 数据记忆与隐私：模型可能复现训练样本 ..... 93
10.3.4 4. 高效化：从少步采样到系统部署 ..... 94
10.3.5 5. 未来路线：从生成模型到可控世界模拟器 ..... 94
10.4 关键公式或伪代码 ..... 94
10.5 关键架构图 / 方法图拆解 ..... 95
10.6 该方向的痛点 ..... 98
10.7 核心 insight ..... 99
10.8 实验结论 ..... 99
10.9 局限与未来工作 ..... 99
10.10 读完这一章应该掌握什么 ..... 100
10.11 复习问题 ..... 100

附录 A 全书质量检查清单 ..... 101本讲义基于 /Users/qingle/Code/Paper/projects/generative_models_diffusion/paper_bank/中104篇论文、MinerU全文解析结果与逐篇深度阅读笔记综合整理。插图均来自对应论文的MinerU提取图片，仅用于个人学习笔记和内部研究综述；每张图都标注来源论文、年份和可识别的Figure/Page信息。若无法可靠判断图号，统一写作“论文中的方法图/实验图”。

## 0.1 㑥⧨㴪⛣㸆〉Ⰶ㯏

这本讲义不按论文逐篇排队。生成模型的发展更像几条问题线同时推进：怎样定义概率，怎样采样，怎样控制条件，怎样把模型做大，怎样把多步过程变快，怎样把生成能力迁移到视频、音频、3D、机器人和科学问题。你会在每章看到同一个结构：先问这章要解决什么，再讲背景和方法，接着给公式、伪代码、图像拆解、痛点、insight、实验结论、局限和复习问题。

建议的阅读顺序是：

1. 第1-2 章先建立生成模型和diffusion的统一语言。

2. 第3-5章理解现代图像生成系统为什么从U-Net/LDM走向DiT/MMDiT、flowmatch-ing 和少步蒸馏。

3. 第6-7 章看控制、编辑、个性化和跨媒体生成如何把基础模型变成产品级系统。

4. 第8-9章把diffusion放进具身智能和AI4Science，理解它为什么适合生成轨迹、结构、构象、材料和天气集合预报。

5. 第10章回到评测、安全和效率，建立做新研究时必须检查的清单。

# ☾1㷦 㔶⒱ㄩ㨻㍰㖱ᱶ㢜㖬ぼdiffusion ⪹㱖☡ⱅ㝢

## 1.1 〉㷦㮔ⰶⴈ☨㢼㝘

今天讲 diffusion，很容易从 DDPM 开始。但如果只看 DDPM，就会误以为 diffusion的成功只是“加噪再去噪”这个公式突然出现。真正的问题链更长：生成模型一直在尝试回答四个基本问题。

第一，怎样给数据分布写概率？VAE给出隐变量模型和可优化下界[VAE,2013]，Pix-elRNN/PixelCNN 给出逐像素自回归精确似然 [PixelRNN, 2016]，Glow 给出可逆变换与精确 likelihood [Glow, 2018]。

第二，怎样生成看起来真实的样本？GAN用生成器和判别器的对抗博弈把“真实感”变成可学习损失[GAN,2014]，WGAN又指出距离度量会决定梯度是否有用[WGAN,2017]。

第三，怎样把图像变成可被序列模型处理的 token？VQ-VAE 把图像压成离散码本索引 [VQ-VAE, 2017]，Taming Transformers 用 VQGAN + Transformer 生成高分辨率图像[Taming Transformers, 2020]，DALL-E 第一代把文本 token 和图像 token 拼成一个长序列[DALL-E, 2021]。

第四，怎样同时得到稳定训练、高质量样本、可控条件和相对好的分布覆盖？这正是diffusion后来被推上主线的原因。它没有像GAN那样依赖脆弱博弈，也没有像逐像素自回归那样逐点慢采样；它用大量局部监督把复杂生成拆成许多去噪小题。

本章的目标，是让你在进入DDPM前先理解diffusion解决了哪些旧问题，也继承了哪些旧思想。

## 1.2 ⭒㗯⌟Ⳃ

生成模型可以先粗略分成五类。

<table><tr><td>范式</td><td>代表论文</td><td>训练目标</td><td>采样特点</td><td>核心困难</td></tr><tr><td>VAE / latent variable model</td><td>VAE</td><td>ELBO</td><td>快</td><td>样本容易模糊,posterior collapse</td></tr><tr><td>GAN</td><td>GAN, WGAN</td><td>对抗损失</td><td>很快</td><td>训练不稳定,mode collapse,无显式似然</td></tr><tr><td>Autoregressive</td><td>PixelRNN,DALL-E</td><td>精确 next-token likelihood</td><td>逐 token 慢</td><td>长序列高成本,全局结构难</td></tr><tr><td>Flow</td><td>Glow</td><td>精确 likelihood</td><td>快且可逆</td><td>架构受可逆性约束</td></tr><tr><td>Diffusion / score / flow matching</td><td>DDPM, Score SDE, EDM, Rectified Flow</td><td>去噪/score/velocity</td><td>多步,可加速</td><td>采样成本、条件对齐、效率</td></tr></table>

这张表不要背成静态分类。更重要的是看每个范式在和什么矛盾搏斗。VAE 用下界换稳定训练；GAN用判别器换视觉锐度；autoregressive用链式法则换精确似然；flow用可逆结构换 exact density；diffusion 用多步去噪换稳定性和覆盖。

## 1.3 ⧥㨲➝➈

## 1.3.1 1. VAEᱶ≿㯨⍐⼋㟺⛱⍐⒱⶙㢔㥲ⰻ

VAE假设数据由潜变量z 生成：

$$
p _ {\theta} (x, z) = p (z) p _ {\theta} (x | z).
$$

边缘似然需要积分：

$$
p _ {\theta} (x) = \int p (z) p _ {\theta} (x | z) d z,
$$

通常不可直接求。VAE引入近似后验 $q _ { \phi } ( z | x )$ ，得到 ELBO：

$$
\log p _ {\theta} (x) \geq \mathbb {E} _ {q _ {\phi} (z | x)} [ \log p _ {\theta} (x | z) ] - D _ {K L} (q _ {\phi} (z | x) \| p (z)).
$$

这两个项的直觉很清楚：第一项要求 z 能重构 x，第二项要求 z 的分布接近简单先验，方便从先验采样。重参数化技巧：

$$
z = \mu_ {\phi} (x) + \sigma_ {\phi} (x) \odot \epsilon , \quad \epsilon \sim \mathcal {N} (0, I)
$$

让随机采样节点可以反向传播。VAE对后来的latentdiffusion极其重要，因为StableDiffusion 的第一阶段本质上也是学习一个把像素压到 latent、再从 latent 解码回像素的

autoencoder [Latent Diffusion, 2021]。 

## 1.3.2 2. GAN/WGANᱶ≿㸊㖯⡮Ⰿ⢖⶙㫓㥠㋂⭱㋹

GAN 的 minimax 目标是：

$$
\min _ {G} \max _ {D} \mathbb {E} _ {x \sim p _ {\text { data }}} [ \log D (x) ] + \mathbb {E} _ {z \sim p (z)} [ \log (1 - D (G (z))) ].
$$

生成器 G 想骗过判别器 D，判别器想区分真实样本和生成样本。理想状态下 $p _ { g } =$ $p _ { \mathrm { d a t a } } , \ D ( x ) = 1 / 2 [ \mathrm { G A N } , 2 0 1 4 ]$ 。GAN的贡献在于可学习损失，而非显式概率：判别器会随着生成器进步不断更新“真实感标准”。

WGAN 指出原始 GAN 的 JS divergence 在高维流形支撑不重叠时会给生成器带来坏梯度，于是改用 Wasserstein-1 距离：

$$
W (P _ {r}, P _ {g}) = \sup _ {\| f \| _ {L} \leq 1} \mathbb {E} _ {x \sim P _ {r}} [ f (x) ] - \mathbb {E} _ {\tilde {x} \sim P _ {g}} [ f (\tilde {x}) ].
$$

判别器变成 critic，输出实数评分，不输出概率 [WGAN, 2017]。这条线后来没有消失：ADD 把 adversarial loss 引回少步 diffusion 蒸馏，用于补足 one-step 生成的细节锐度[ADD, 2023]。

## 1.3.3 3. 㽴⪰⥅㟰㦡ㄩ㨻ᱶ≿㟰㊮☕⒱㩠⼜

PixelRNN/PixelCNN 从链式法则出发：

$$
p (x) = \prod_ {i = 1} ^ {N} p (x _ {i} | x _ {<   i}).
$$

这给了精确 likelihood，但生成必须按顺序逐像素采样。DALL-E 和 Taming Transform-ers 的关键改造是：先用离散视觉 tokenizer 把图像压成较短 token 序列，再用 Transformer做 autoregressive modeling [VQ-VAE, 2017][Taming Transformers, 2020][DALL-E, 2021]。

VQ-VAE的量化步骤是：

$$
z _ {q} (x) = e _ {k}, \quad k = \arg \min _ {j} \| z _ {e} (x) - e _ {j} \| _ {2}.
$$

图像从连续像素变成离散code，Transformer才能像处理语言一样处理图像。这个想法后来在多模态大模型中继续存在，只是 diffusion 主线选择了连续 latent 而非离散 code作为高分辨率生成接口。

## 1.3.4 4. Flowᱶ㱫⶙ㅬ⍐⪓⪓ exact likelihood

Flow 模型使用可逆函数f 将数据映射到简单分布：

$$
z = f (x), \quad \log p _ {X} (x) = \log p _ {Z} (z) + \log \left| \det \frac {\partial f (x)}{\partial x} \right|.
$$

Glow 通过 actnorm、invertible 1 1 convolution 和 affine coupling layer 构建可逆网络[Glow,2018]。Flow的优点是概率精确、采样快、可逆；难点是网络必须可逆，架构自由度受限。后来的 flow matching 和 rectified flow 继承了“连续运输”的思想，放宽了严格可逆网络约束，把重点转向学习速度场 [Rectified Flow, 2022][Flow Matching, 2022]。

## 1.4 ⤴⮒⤇㖷⫊㢣■⿵

把几条前史路线压成统一伪代码：

```txt
VAE:
    encode x -> qφ(z|x)
    sample z with reparameterization
    decode z -> x_hat
    optimize reconstruction + KL

GAN:
    train D to separate real x and fake G(z)
    train G to fool D

Autoregressive image model:
    tokenize image into pixels/codes
    train p(token_i | token_<i)
    sample one token at a time

Flow:
    learn invertible f: x <-> z
    compute log likelihood with Jacobian determinant
    sample z ~ N(0,I), invert f

Diffusion preview:
    corrupt x0 gradually to xT
    learn reverse denoising steps
    sample by iterative denoising 
```

这一段伪代码也提示了diffusion的优势位置：它不像VAE那样必须把所有信息压进一个简单 posterior；不像 GAN 那样依赖对抗平衡；不像 autoregressive 像素模型那样逐像素采样；不像flow 那样要求每层严格可逆。它付出的代价是多步采样。

## 1.5 ⤴⮒⭲⤕㟰/➝➈㟰␚ⰶ

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/b981e16f87ea55c5913fec7b557b2b94ce4c349f15dbdba3502823081ad651c7.jpg)



㟰 1.1: 图 1-1：VAE 图模型示意，来源：Kingma and Welling, 2013, Fig. 1。


这张图要看实线和虚线。实线表示生成方向：从z 到x。虚线表示推断方向：从x到z。VAE的意义是把这两条方向放进同一个训练目标。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/bdb58ed7cbce7a75deb24682f910c9f690654ead25f3d4a68fd80bae3472a49b.jpg)



㟰 1.2: 图 1-2：GAN 对抗训练动态，来源：Goodfellow et al., 2014, Fig. 1。


图中黑色是真实分布，绿色是生成分布，蓝色是判别器。GAN的全部故事就在这里：判别器指出差异，生成器沿梯度移动，直到两者无法区分。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/a66e2d1669f7c2ab8b05785dec1c648eace7eaf566d31aa550365bd00293d711.jpg)



㟰 1.3: 图 1-3：VQ-VAE 离散码本，来源：van den Oord et al., 2017, Fig. 1。


VQ-VAE 的图解释了图像 token 化的关键接口：encoder 输出连续向量，最近邻量化到码本向量，decoder 从码本向量重构。DALL-E、Taming Transformers 依赖这类接口把图像变成序列。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/346958b0d2e4d011e692be89149bb774f9a62d5134c6ab716ad742239443296e.jpg)



㟰 1.4: 图 1-4：VQGAN + Transformer 高分辨率生成框架，来源：Esser et al., 2020, Fig. 2。


这张图是 diffusion 前夜的重要图。左边学视觉 codebook，右边用 Transformer 学 token组合。LatentDiffusion后来保留“先压缩再生成”的思路，替换了第二阶段生成器。

## 1.6 ⡡➝㦢☨㟨♇

第一，视觉质量、似然和覆盖很难三者兼得。GAN样本锐利但覆盖和稳定性差；au-toregressive likelihood 清楚但采样慢；flow 概率精确但架构受限；VAE 稳定但视觉质量弱。

第二，高维图像不适合直接建模。无论是像素自回归还是可逆 flow，在高分辨率下都会遇到成本、内存或架构限制。VQ-VAE、VQGAN、LDM都是在寻找更好的中间表示。

第三，条件控制越来越重要。早期无条件生成只要样本像真图即可；文生图时代要求物体、属性、关系、风格和编辑指令都能被控制。旧范式在开放文本条件下暴露出新的短板。

第四，评测不可靠。GAN 的好样本可能掩盖 mode collapse，likelihood 好不代表视觉真实，CLIP score 高不代表组合关系正确。这会在第 10 章展开。

## 1.7 ⧥㨲 insight

本章的核心 insight 是：diffusion 的胜利来自对多条旧路线矛盾的折中，而非单点公式胜利。它接受多步采样成本，换来稳定监督、较好覆盖、强条件接口和可扩展训练。更准确地说，diffusion 把“生成一张图”拆成“在不同噪声水平上做许多去噪判断”，于是复杂分布学习变成大量局部回归问题。

第二个 insight 是：旧范式仍在现代系统中活着。Stable Diffusion 用 VAE latent；SD3使用 rectified flow；ADD 使用 adversarial loss；DALL-E 2 使用 CLIP latent；DiT/MDT 继承 Transformer token 化思想。学习生成模型不能把历史看成淘汰赛，更应该看成工具箱不断重组。

## 1.8 㖯㬕ⰵ⿥

VAE证明隐变量模型可用神经网络和SGD训练，但样本锐度有限[VAE,2013]。GAN证明可学习判别器能驱动高保真生成，但训练不稳定 [GAN, 2014]。PixelRNN/PixelCNN证明图像自回归能得到强 likelihood，但采样慢 [PixelRNN, 2016]。WGAN 证明分布距离的几何性质会影响梯度质量 [WGAN, 2017]。VQ-VAE、Taming Transformers、DALL-E 证明图像 token 化和 Transformer prior 可行，但离散 token 自回归在高分辨率、细节和速度上压力明显 [VQ-VAE, 2017][Taming Transformers, 2020][DALL-E, 2021]。

这些结论合在一起，给diffusion留出了位置：它不要求精确逐像素likelihood，不依赖对抗平衡，不要求严格可逆，并且可以在连续latent中处理高分辨率视觉生成。

## 1.9 ⳨㦎㲓㢦⹂⤀㾗

前史模型的局限也变成了 diffusion 的未来问题。VAE 提醒我们 latent tokenizer 会限制细节；GAN提醒我们感知质量需要专门监督；autoregressive模型提醒我们序列建模和多模态统一很强；flow提醒我们路径几何和可逆性/ODE思想有长期价值。未来生成模型很可能继续融合：用 diffusion/flow 做主体，用 Transformer 做主干，用 VAE/RAE 做表示，用偏好/RL/对抗损失做后训练。

## 1.10 ⛣㠞㸆㮥㷦㱎⡡㷪㣇㖬ぼ

读完这一章，你应该能解释：

1. VAE的ELBO为什么同时包含重构和KL。

2. GAN 的判别器为什么是可学习损失，WGAN 为什么换距离。

3. PixelRNN 和 DALL-E 为什么把图像变成序列。

4. VQ-VAE/VQGAN 为什么是图像 token 化的关键。

5. Glow 的 exact likelihood 来自变量替换公式。

6. diffusion为什么在稳定性、覆盖和条件控制上占到优势。

## 1.11 ⡒㥠㢼㝘

1. 为什么 VAE 会出现模糊样本？这和解码似然有什么关系？

2. 原始 GAN 的 JS divergence 为什么会导致梯度问题？

3. PixelRNN的训练为什么可并行，采样为什么慢？

4. VQ-VAE 的 stop-gradient 在两个 loss 项中分别阻断谁的梯度？

5. Flow 模型的可逆性带来什么好处和代价？

6. 如果让你设计一个新生成系统，你会把 VAE、GAN、Transformer、diffusion 的哪些组件组合起来？

# ☾2 㷦 ⸷㓞ㄩ㨻⫑╇ᱶ╹ DDPM ☡ Score SDEᮢEDM 㲓 Flow Matching

## 2.1 〉㷦㮔ⰶⴈ☨㢼㝘

本章回答 diffusion 的核心问题：为什么“加噪再去噪”可以变成强生成模型？更具体地说，我们要讲清楚五件事。

第一，forward process 怎样把数据变成噪声，reverse process 怎样从噪声生成数据[Nonequilibrium Thermodynamics, 2015][DDPM, 2020]。

第二，DDPM 为什么可以把复杂的变分下界简化成噪声预测 MSE [DDPM, 2020]。

第三，score-based model 和 DDPM 如何在连续时间 SDE 视角下统一 [NCSN, 2019][ScoreSDE, 2020]。

第四，DDIM、EDM、DPM-Solver、DPM-Solver++ 等工作为什么把采样看成数值求解问题 [DDIM, 2020][EDM, 2022][DPM-Solver, 2022][DPM-Solver++, 2022]。

第五，Rectified Flow、Flow Matching、Stochastic Interpolants 为什么把现代 diffusion 推向“学习速度场/传输路径”的新语言 [Rectified Flow, 2022][Flow Matching, 2022][StochasticInterpolants, 2023]。

如果第 1 章讲的是生成模型的旧矛盾，本章讲的就是 diffusion 怎样把这些矛盾重新组织。

## 2.2 ⭒㗯⌟Ⳃ

扩散模型的基本直觉很像图像修复课。给你一张完全清晰的图，逐渐往上加高斯噪声，最后它会变成几乎纯噪声。这个方向很容易，因为我们自己定义加噪过程。真正难的是反方向：给你一团噪声，你怎样一步步去掉噪声，让它落回真实图像分布？

用 $x _ { 0 }$ 表示真实数据， $x _ { t }$ 表示第t 步noisydata。正向加噪定义为：

$$
q (x _ {t} | x _ {t - 1}) = \mathcal {N} (x _ {t}; \sqrt {1 - \beta_ {t}} x _ {t - 1}, \beta_ {t} I).
$$

由于高斯加噪的可组合性，可以直接从 $x _ { 0 }$ 采样任意时间步：

$$
q (x _ {t} | x _ {0}) = \mathcal {N} (x _ {t}; \sqrt {\bar {\alpha} _ {t}} x _ {0}, (1 - \bar {\alpha} _ {t}) I),
$$

其中

$$
\alpha_ {t} = 1 - \beta_ {t}, \quad \bar {\alpha} _ {t} = \prod_ {s = 1} ^ {t} \alpha_ {s}.
$$

因此可以写成：

$$
x _ {t} = \sqrt {\bar {\alpha} _ {t}} x _ {0} + \sqrt {1 - \bar {\alpha} _ {t}} \epsilon , \quad \epsilon \sim \mathcal {N} (0, I).
$$

这就是 DDPM 最常用的训练入口。

## 2.3 ⧥㨲➝➈

## 2.3.1 1. DDPMᱶ㴊␌㵑㔵

反向过程由神经网络参数化：

$$
p _ {\theta} (x _ {t - 1} | x _ {t}) = \mathcal {N} (x _ {t - 1}; \mu_ {\theta} (x _ {t}, t), \Sigma_ {\theta} (x _ {t}, t)).
$$

DDPM 的关键简化是训练网络预测加到 $x _ { 0 }$ 上的噪声ϵ：

$$
L _ {\text { simple }} = \mathbb {E} _ {t, x _ {0}, \epsilon} \left[ \| \epsilon - \epsilon_ {\theta} (x _ {t}, t) \| ^ {2} \right].
$$

直觉非常朴素：如果模型知道当前图像里哪些成分是噪声，就能把它们减掉。重复很多次，就能从纯噪声还原到数据样本[DDPM,2020]。

Improved DDPM 后来补上几个工程关键点：学习 reverse variance、使用 cosine sched-ule、混合simpleloss与VLB、降低梯度噪声，并证明扩大模型规模能持续提升质量[Im-proved DDPM, 2021]。

## 2.3.2 2. Classifier guidance 㲓 CFGᱶ⏳㬥Ⱛ⛰㖣⭩㝫⮔

Diffusion Models Beat GANs 用 classifier guidance 把类别条件写成 score 修正：

$$
\nabla_ {x _ {t}} \log p (x _ {t} | y) = \nabla_ {x _ {t}} \log p (x _ {t}) + \nabla_ {x _ {t}} \log p (y | x _ {t}).
$$

采样时用 noisy classifier 的梯度把样本推向目标类别 [Diffusion Beats GANs, 2021]。Classifier-free guidance 进一步省掉外部分类器：同一个 denoiser 同时学习条件和无条件预测，推理时线性外推：

$$
\epsilon_ {\mathrm{cfg}} = \epsilon_ {\theta} (x _ {t}, \varnothing , t) + w \left[ \epsilon_ {\theta} (x _ {t}, c, t) - \epsilon_ {\theta} (x _ {t}, \varnothing , t) \right].
$$

w 是guidancescale。它越大，条件遵从越强，多样性和自然度可能下降[CFG,2022]。

## 2.3.3 3. Score SDEᱶ⻸㩦㖫⭺㟧㮥

Score SDE 把正向加噪写成：

$$
d x = f (x, t) d t + g (t) d w.
$$

反向时间 SDE 为：

$$
d x = [ f (x, t) - g (t) ^ {2} \nabla_ {x} \log p _ {t} (x) ] d t + g (t) d \bar {w}.
$$

因此只要学到 score：

$$
s _ {\theta} (x, t) \approx \nabla_ {x} \log p _ {t} (x),
$$

就能反向生成。对应的 probability flow ODE 是：

$$
d x = \left[ f (x, t) - \frac {1}{2} g (t) ^ {2} s _ {\theta} (x, t) \right] d t.
$$

这一步意义很大：采样不再只是“DDPM 链”，也可以是 ODE/SDE 数值求解 [ScoreSDE, 2020]。

## 2.3.4 4. EDMᱶ≿⸷㓞㔤⭜ⶥ⭺㾘⍖⪇

EDM 重新组织扩散模型。它直接用噪声强度σ 表示扰动：

$$
x _ {\sigma} = x _ {0} + \sigma \epsilon .
$$

训练 denoiser：

$$
D _ {\theta} (x _ {\sigma}, \sigma) \approx x _ {0}.
$$

score 可由 denoiser 得到：

$$
\nabla_ {x} \log p (x; \sigma) \approx \frac {D _ {\theta} (x ; \sigma) - x}{\sigma^ {2}}.
$$

EDM 的重点是 preconditioning：

$$
D _ {\theta} (x; \sigma) = c _ {\mathrm{skip}} (\sigma) x + c _ {\mathrm{out}} (\sigma) F _ {\theta} (c _ {\mathrm{in}} (\sigma) x, c _ {\mathrm{noise}} (\sigma)).
$$

这让不同噪声尺度的输入输出数值更稳定。EDM 还系统研究 Karras noise schedule、Heun sampler、stochastic churn 等采样设计 [EDM, 2022]。

## 2.3.5 5. Flow Matching / Rectified Flowᱶ㫓㥠㚑⛪⒉

Rectified Flow 把路径写成线性插值：

$$
X _ {t} = (1 - t) X _ {0} + t X _ {1},
$$

目标速度是：

$$
\dot {X} _ {t} = X _ {1} - X _ {0}.
$$

训练向量场：

$$
\min _ {\theta} \mathbb {E} \| v _ {\theta} (X _ {t}, t) - (X _ {1} - X _ {0}) \| ^ {2}.
$$

FlowMatching进一步把目标写成条件向量场回归：

$$
L _ {\mathrm{CFM}} = \mathbb {E} _ {t, x _ {1}, p _ {t} (x | x _ {1})} \| v _ {\theta} (x, t) - u _ {t} (x | x _ {1}) \| ^ {2}.
$$

这套语言把生成模型从“预测噪声”推向“学习从噪声到数据的运输速度”。StableDiffu-sion 3、SiT、π0 等后续系统都和这条线有紧密关系 [Stable Diffusion 3, 2024][SiT, 2024][pi0,2024]。

## 2.4 ⤴⮒⤇㖷⫊㢣■⿵

DDPM 训练：

```python
repeat:
    sample x0 from data
    sample t uniformly
    sample ε ~ N(0, I)
    xt = sqrt(alpha_bar_t) * x0 + sqrt(1-alpha_bar_t) * ε
    loss = ||ε - εθ(xt, t, condition)||^2
    update θ

DDPM 采样:
```

```python
xT ~ N(0, I)
for t = T ... 1:
    predict εθ(xt, t, condition)
    compute mean μθ(xt, t)
    sample xt-1 from N(μθ, Σθ)
return x0 
```

Flow matching 训练：

```txt
sample data x1
sample base x0 ~ N(0, I)
sample t ~ Uniform(0, 1)
xt = (1 - t) * x0 + t * x1
target_velocity = x1 - x0
loss = ||vθ(xt, t) - target_velocity||^2 
```

这三段伪代码给出两种思维方式。DDPM 关注“噪声是什么”；flow matching 关注“速度往哪走”。现代模型常在这两种语言之间切换。

## 2.5 ⤴⮒⭲⤕㟰/➝➈㟰␚ⰶ

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/00c82c170d9c52361d83d942541445b6e05d34987e2f8922d1145268882f2294.jpg)



㟰 2.1: 图 2-1：非平衡热力学 diffusion 原型图，来源：Sohl-Dickstein et al., 2015, MinerU 提取图。


这张图代表最早的扩散链：正向从数据走向噪声，反向从噪声走向数据。正向过程由人定义，反向过程由模型学习。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/f47e3caf2792f48ddaf0203edb8ca5cde9b4b75211bf970eaf14fc3f7af67294.jpg)



㟰 2.2: 图 2-2：Score SDE 连续时间方法图，来源：Song et al., 2020, MinerU 提取图。


Score SDE 的图要从连续时间读：不同噪声水平形成一族边际分布，score field 指出回到高密度区域的方向。DDPM 的离散链可以嵌入这个连续视角。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/025b080d30688fc350a0ea206415b25f078839829346107199ae6c1edfe9d029.jpg)



㟰 2.3: 图 2-3：EDM 设计空间实验图，来源：Karras et al., 2022, MinerU 提取图。


EDM的图通常展示采样步数、噪声范围、求解器和FID的关系，模型框图并不是这里的重点。它提醒我们：diffusion的质量不只由网络决定，也由采样设计决定。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/bdc8b75350d422191bbccbf419998624b440c42447191d7988e2d452e5622f52.jpg)



㟰 2.4: 图 2-4：Rectified Flow 路径变直示意，来源：Liu et al., 2022, MinerU 提取图。


RectifiedFlow的图适合用来讲“路径几何”。路径越直，少步ODE求解越容易。现代rectifiedflow文生图系统正是在追求更可采样的生成路径。

## 2.6 ⡡➝㦢☨㟨♇

第一，采样慢。DDPM的稳定训练来自多步去噪，代价也是多步去噪。DDIM、PNDM、DPM-Solver、EDM、LCM、ADD 等几乎都围绕这点展开。

第二，噪声日程和参数化敏感。线性 beta、cosine schedule、ϵ-prediction、x<sub>0</sub>-prediction、v-prediction、EDM preconditioning 都会改变训练稳定性和采样质量。

第三，guidance 有双刃剑效应。CFG 让条件更强，也会降低多样性，甚至造成过饱和、结构崩坏或提示词过拟合。

第四，连续时间理论漂亮，工程上仍需调参。SDE/ODE、solver阶数、步长、stochasticity、thresholding 都不是免费午餐。

第五，flow matching 让路径更直，但路径设计和复杂条件对齐仍是难题。直线插值在低维直观，高维语义空间中是否总是好路径，需要实验验证。

## 2.7 ⧥㨲 insight

本章的第一条 insight：扩散模型强在监督密度。每张训练图可以被加到任意噪声水平，每个噪声水平都给出明确的预测目标。这让模型获得大量局部训练信号。

第二条 insight：采样器就是模型的一部分。即使权重不变，DDIM、PNDM、DPM-Solver++、EDM sampler 会给出不同速度和质量。读 diffusion 论文时，只看 backbone 会漏掉一半系统。

第三条 insight：score、denoiser、velocity 是同一个生成过程的不同坐标。DDPM 预测噪声，EDM 预测 denoised data，Score SDE 预测 score，Flow Matching 预测 velocity。它们并非完全孤立的世界，可以相互转换和比较。

## 2.8 㖯㬕ⰵ⿥

DDPM 证明噪声预测能生成高质量图像 [DDPM, 2020]。Improved DDPM 证明 learnedvariance、cosine schedule、hybrid loss 和 scaling 能显著改善 likelihood、质量和采样速度[Improved DDPM, 2021]。Diffusion Models Beat GANs 证明在强 U-Net 和 classifier guidance下，diffusion 可在 ImageNet 质量上超过 GAN [Diffusion Beats GANs, 2021]。Score SDE证明连续时间框架可以统一 NCSN/DDPM，并支持 PC sampler 与 probability flow ODE[Score SDE, 2020]。EDM 证明设计空间整理本身能带来强性能 [EDM, 2022]。RectifiedFlow 与 Flow Matching 证明直接学习速度场可成为扩散之外的强生成路径 [Rectified Flow,2022][Flow Matching, 2022]。

## 2.9 ⳨㦎㲓㢦⹂⤀㾗

基础 diffusion 的局限集中在三处：慢、贵、难控。慢来自多步采样；贵来自大 U-Net/Transformer和高分辨率数据；难控来自条件、布局、文字、数量关系和人类偏好。未来的基础模型会继续向三个方向走：一是更直的路径和更少步的蒸馏；二是更强的Trans-former/DiT/MMDiT主干；三是更好的对齐和评测，让模型生成的不只是漂亮图，还能严格遵守条件。

## 2.10 ⛣㠞㸆㮥㷦㱎⡡㷪㣇㖬ぼ

读完这一章，你应该能从头写出：

1. 正向加噪公式 $q ( x _ { t } | x _ { 0 } )$ 

2. DDPM 的噪声预测损失。

3. CFG 的线性外推公式。

4. Score SDE 的正向和反向 SDE。

5. EDM 中 denoiser 与 score 的关系。

6. Rectified Flow / Flow Matching 的 velocity regression 目标。

## 2.11 ⡒㥠㢼㝘

1. 为什么 DDPM 可以直接从 $x _ { 0 }$ 采样任意 $\boldsymbol { x } _ { t } \boldsymbol { ? }$ 

2. ϵ-prediction、x -prediction、v-prediction 各有什么直觉差异？

3. CFG scale 太大会出现什么问题？

4. Score SDE 中 probability flow ODE 有什么用？

5. EDM 为什么强调 preconditioning？

6. Rectified Flow 为什么可能减少采样步数？

7. Flow Matching 和 DDPM 在训练目标上最核心的差别是什么？

## ☾ 3 㷦 㢶㔶㟰㥥㟧ᱶ╹ GLIDE DALL-E 2ᮢImagen ☡ Stable Diffusion 㲓 SD3

## 3.1 〉㷦㮔ⰶⴈ☨㢼㝘

有了 DDPM 还不等于有了现代文生图系统。真正的文生图模型要同时解决四个系统问题：文字如何进入模型，图像在哪个空间生成，分辨率如何放大，用户偏好如何评估。GLIDE 证明文本条件 diffusion 可行，并比较 CLIP guidance 与 classifier-free guidance[GLIDE, 2021]。DALL-E 2 用 CLIP image latent 组织 text-to-image 生成，把图像语义先验和 diffusion decoder 拆开 [DALL-E 2, 2022]。Imagen 强调大语言编码器和级联超分辨率diffusion，说明语言理解能力对图像生成至关重要 [Imagen, 2022]。Latent Diffusion 把生成搬进 autoencoder latent，直接改变了成本结构，也成为 Stable Diffusion 的基础 [LatentDiffusion, 2021]。SDXL 进一步把 LDM 做成更大、更工程化的两阶段系统 [SDXL, 2023]。Stable Diffusion 3 则把主干切换到 rectified flow + MMDiT，标志着现代文生图从 U-NetLDM 走向 Transformer/flow 时代 [Stable Diffusion 3, 2024]。

本章的核心问题是：为什么现代文生图系统不是“一个文本编码器+一个diffusionU-Net”这么简单？答案是它至少包含 tokenizer/autoencoder、文本编码器、denoiser/flow back-bone、conditioning 机制、采样器、refiner、reranker/人评、数据过滤等一整套系统。

## 3.2 ⭒㗯⌟Ⳃ

文生图模型必须把自然语言条件c注入生成过程。最早可以用类别label；开放prompt则需要文本编码器。注入方式大致有三类：

1. 把文本向量作为全局条件，例如通过 AdaGN、FiLM、time embedding 相加。

2. 用 cross-attention，让图像 latent token 在 denoising 时读取文本 token [Latent Diffusion,2021]。

3. 在 Transformer diffusion 中把文本 token 和图像 token 放进统一 attention 或双流 at-tention [Stable Diffusion 3, 2024]。

分辨率也带来系统选择。像素空间diffusion直观，但高分辨率成本高。Imagen使用级联：先生成低分辨率，再用 super-resolution diffusion 放大 [Imagen, 2022]。LDM 使用 latentspace：先用 VAE 压缩图像，在低维 latent 中 diffusion，再解码回像素 [Latent Diffusion,2021]。两条路线都在减少像素空间的直接负担。

## 3.3 ⧥㨲➝➈

## 3.3.1 1. GLIDEᱶ㢶〉㝫⮔ diffusion 㲓 guidance 㫍㵗

GLIDE 使用文本条件 diffusion，并比较两种引导方式：CLIP guidance 和 classifier-freeguidance。CLIP guidance 用外部 CLIP 模型给生成图和文本匹配打梯度；CFG 在 diffusion模型内部同时训练有条件和无条件预测。实践上，CFG 更稳定、更直接，后来成为文生图标配 [GLIDE, 2021][CFG, 2022]。

GLIDE 的另一点价值在编辑。给定一张图和 mask，模型可以根据文本 prompt 补全区域。这说明 diffusion 不只是从噪声生成图片，也可以做条件修复、局部替换和指令式编辑，后来的 SDEdit、InstructPix2Pix、ControlNet 都沿着这条线扩展。

## 3.3.2 2. DALL-E 2 / unCLIPᱶ㥸㔶⒱ CLIP 㟰㦡㲗㯏ᱨ㴿ⰶ⿵⒱㟰

DALL-E 2 把文生图拆成两层。第一层 prior 从文本生成 CLIP image embedding；第二层 diffusion decoder 根据 CLIP image embedding 生成图像：

```perl
text -> CLIP text embedding
CLIP text embedding -> diffusion/autoregressive prior -> CLIP image embedding
CLIP image embedding -> diffusion decoder -> image 
```

这套 unCLIP 框架有一个清楚的系统思想：先在语义空间决定“图应该是什么”，再在像素空间决定“图长什么样”。它让模型具备图像变体生成能力，因为同一个 CLIP imagelatent 附近可以解码出多张语义相近的图 [DALL-E 2, 2022]。

## 3.3.3 3. Imagenᱶ㲗㬀⍌⿵㋹⌴㦛㦣㺲⢚㺺㮔

Imagen 的结论非常有影响力：扩大 frozen text encoder 比扩大 image U-Net 更能提升图文对齐和人类偏好 [Imagen, 2022]。它使用 T5 作为强语言编码器，配合级联 diffusion：

```txt
prompt -> T5 text embeddings
base diffusion: text -> 64x64 image
SR diffusion 1: 64x64 -> 256x256
SR diffusion 2: 256x256 -> 1024x1024 
```

这说明文生图依赖强语言表征和生成模型共同工作，不能只指望视觉生成器自己补全文本理解。后来的SD3使用多个文本编码器，Sana支持中文和多语言能力，都延续了这条经验 [Stable Diffusion 3, 2024][Sana, 2024]。

## 3.3.4 4. Latent Diffusionᱶ≿⭜㚛⊏☡ perceptual latent

LDM 的关键公式可以写成：

$$
z = E (x), \quad \hat {x} = D (z),
$$

diffusion 在 z 空间训练：

$$
L = \mathbb {E} _ {z, \epsilon , t, c} \| \epsilon - \epsilon_ {\theta} (z _ {t}, t, c) \| ^ {2}.
$$

cross-attention 注入文本条件：

$$
\text { Attention } (Q _ {z}, K _ {c}, V _ {c}) = \text { softmax } \left(\frac {Q _ {z} K _ {c} ^ {\top}}{\sqrt {d}}\right) V _ {c}.
$$

LDM的直觉是：像素空间有很多人眼不敏感的细节，先压缩到perceptuallatent，可以大幅降低 diffusion 主体的计算量 [Latent Diffusion, 2021]。这一步直接打开 Stable Diffusion的开源生态。

## 3.3.5 5. SDXLᱶ≿ LDM 㾖⒱⤀⒴⪇▙㥥㟧

SDXL 在 Stable Diffusion 基础上扩大 U-Net、改进 conditioning，使用两阶段 pipeline：base model 生成主体图像，refiner 处理高噪声到低噪声细节或最后阶段质量 [SDXL, 2023]。它还显式处理训练分辨率和裁剪信息，把尺寸、裁剪坐标等作为conditioning，减少训练/推理分辨率不一致造成的问题。

SDXL的意义在于系统工程：更大的模型、更好的数据、更好的标注、更稳定的训练和refiner组合。它提醒我们，生成质量常来自许多工程细节的共同堆叠。

## 3.3.6 6. SD3ᱶrectified flow + MMDiT ☨㽊㦢

SD3 的基础目标从传统 DDPM 噪声预测转向 rectified flow / flow matching 风格的训练。架构上，它使用MMDiT：文本和图像各自有权重不同的路径，但在attention中相互交互 [Stable Diffusion 3, 2024]。这让文本 token 不再只是 cross-attention 中被读取的条件，而成为和图像latenttoken共同参与生成动态的一部分。

## 3.4 ⤴⮒⤇㖷⫊㢣■⿵

一个现代文生图系统可以抽象成：

```python
text_tokens = tokenizer(c)
text_features = text_encoder(text_tokens)

if latent diffusion:
    z_T ~ N(0, I)
    for t = T ... 1:
    pred_cond = denoiser(z_t, t, text_features)
    pred_uncond = denoiser(z_t, t, empty_or_negative_condition)
    pred = pred_uncond + w * (pred_cond - pred_uncond)
    z_{t-1} = sampler_step(z_t, pred, t)
    image = VAE_decoder(z_0)

if rectified flow:
    z_0_noise ~ N(0, I)
    solve dz/dt = v_theta(z_t, t, text_features)
    image = decoder(z_1) 
```

核心变量是：文本编码器给什么语义，VAE丢掉多少细节，denoiser/flowbackbone有多强，sampler 步数怎样选，CFG/negative prompt 怎样平衡条件和自然度。

## 3.5 ⤴⮒⭲⤕㟰/➝➈㟰␚ⰶ

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/f96ab10ac5cc7e288bdb2278973b4c2af1894538c4158300a449678abbee7dda.jpg)



㟰 3.1: 图 3-1：LDM latent diffusion 架构与 conditioning，来源：Rombach et al., 2021, Fig. 3。


这张图是 Stable Diffusion 生态的核心图。左边是 autoencoder 压缩，右边是 latent space中的 diffusion，条件通过 cross-attention 注入。你要记住：高分辨率生成的主要计算不在像素空间。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/18501f22076dbe555f4535b2ac20a280e5a915a5461f55647156705ffb538aca.jpg)



㟰 3.2: 图 3-2：unCLIP/DALL-E 2 架构总览，来源：Ramesh et al., 2022, Fig. 2。


unCLIP 的图要分成 prior 和 decoder 读。prior 处理 CLIP 语义空间，decoder 处理图像细节。它说明“语义生成”和“像素生成”可以拆开训练。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/c12057d8361dc19e91397cfef5b5be6621b63e3ca91fdd620bd019fd510bf566.jpg)



㟰 3.3: 图 3-3：Imagen 级联 diffusion 总览，来源：Saharia et al., 2022, Appendix Fig. A.4。


Imagen的图展示低分辨率basemodel和多个超分模型。级联设计的好处是每个模型只解决一个相对明确的问题：先构图，再补细节。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/7d03d4dac13eab47a0468ede6914cadf6fd7d4980e12cac9b233862289170810.jpg)



㟰 3.4: 图 3-4：SDXL 用户偏好与两阶段 pipeline，来源：Podell et al., 2023, Fig. 1。


SDXL 的图体现工程系统思维：base 和 refiner 分工，人类偏好成为评估主轴，训练分辨率和条件信息被纳入模型设计。

## 3.6 ⡡➝㦢☨㟨♇

第一，文本理解不稳。模型可能会漏物体、混属性、搞错数量关系和空间关系。Imagen强调大语言编码器，就是因为prompt理解本身是瓶颈。

第二，VAE/tokenizer 是隐藏上限。LDM 降低成本，但 VAE 可能丢失文字、小物体和精细纹理。后来的 RAE/DiT-RAE 正是在挑战这一瓶颈 [DiT-RAE, 2025]。

第三，CFG 有质量-多样性 trade-off。强 CFG 提升 prompt adherence，也会造成过饱和和构图僵硬。

第四，级联和 refiner 增加系统复杂度。Imagen 的 cascade、SDXL 的 refiner 都提升质量，也增加训练、推理和部署成本。

第五，评测难。FID、CLIP score、人评、GenEval、T2I-CompBench 往往关注不同能力，单一指标会误导。

## 3.7 ⧥㨲 insight

文生图系统的核心 insight 是：生成质量来自“语义、表示、生成路径、采样和偏好”的联合优化。GLIDE 解决文本条件 diffusion；DALL-E 2 解决语义 latent；Imagen 强化语言编码器；LDM 改变计算空间；SDXL 做系统扩展；SD3 改 backbone 和 flow objective。这些工作不是简单替代关系，更像一层层补上文生图系统的短板。

## 3.8 㖯㬕ⰵ⿥

GLIDE显示CFG在文本条件扩散中非常有效，人评上优于多个早期baseline[GLIDE,2021]。DALL-E 2 证明 CLIP latent prior + diffusion decoder 能生成高质量开放图像，并支持 image variation [DALL-E 2, 2022]。Imagen 的 DrawBench 和 ablation 显示大文本编码器对图文对齐影响显著 [Imagen, 2022]。LDM 证明 latent space diffusion 在质量和成本之间取得好平衡 [Latent Diffusion, 2021]。SDXL 在人类偏好上显著优于早期 Stable Diffusion，并显示 refiner 能增强细节 [SDXL, 2023]。SD3 的实验显示 MMDiT + rectified flow 有更好的 scaling 和 prompt adherence [Stable Diffusion 3, 2024]。

## 3.9 ⳨㦎㲓㢦⹂⤀㾗

文生图系统的局限正在从“能不能生成好看图”转向“能不能严格执行复杂指令”。未来重点包括更好的文本 grounding、更强 tokenizer/RAE、更少步 flow/consistency 生成、更可靠的组合评测、更透明的数据治理，以及与编辑、控制、视频、3D 的统一。

## 3.10 ⛣㠞㸆㮥㷦㱎⡡㷪㣇㖬ぼ

1. GLIDE 为什么是文本条件 diffusion 的关键节点。

2. DALL-E 2 的 prior 和 decoder 分别解决什么。

3. Imagen为什么强调T5等大文本编码器。

4. LDM 为什么能让高分辨率生成成本下降。

5. SDXL 的 base/refiner 和 conditioning 有什么意义。

6. SD3 为什么代表从 U-Net LDM 到 MMDiT/flow 的转向。

## 3.11 ⡒㥠㢼㝘

1. LDM 的 cross-attention 在图像 latent 和文本 token 之间做了什么？

2. Imagen 的 cascade 和 LDM 的 latent compression 分别怎样降低成本？

3. DALL-E 2 为什么需要 CLIP image latent prior？

4. SDXL 的refiner与简单增加采样步数有什么区别？

5. CFG scale 为什么不能无限增大？

6. SD3 的 MMDiT 相比传统 cross-attention U-Net 有什么结构差异？

# ☾ 4 㷦 DiTᮢMMDiT 㲓 Transformer ⪇ diffusion

## 4.1 〉㷦㮔ⰶⴈ☨㢼㝘

U-Net曾经是diffusion的默认主干。它有卷积归纳偏置、多尺度结构和skipconnection，非常适合图像。但当文生图数据规模、模型规模和多模态条件继续增长，Transformer的吸引力越来越大：它天然处理token，可扩展性好，和LLM/VLM的工程栈更接近。DiT首次系统证明，在 latent patch 上使用 Transformer 可以成为强 diffusion backbone，并且性能随计算量平滑 scaling [DiT, 2022]。U-ViT 把 time、condition、image patch 都当成 token，保留long skip [U-ViT, 2022]。MDT 用 mask 提升 DiT 训练效率 [MDT, 2023]。PixArt、Hunyuan-DiT、Lumina、Sana 说明 DiT 可以走向高效文生图系统 [PixArt-alpha, 2023][Hunyuan-DiT,2024][Lumina-T2X, 2024][Sana, 2024]。SD3 的 MMDiT 把文本和图像 token 交互推到核心位置 [Stable Diffusion 3, 2024]。

本章要回答：视频、图像和文本都能token化时，diffusionbackbone为什么自然走向Transformer？以及 MMDiT 后续研究在解决哪些新瓶颈？

## 4.2 ⭒㗯⌟Ⳃ

DiT 的基本做法是把 VAE latent 切成 patch：

$$
z \in \mathbb {R} ^ {C \times H \times W} \to \text { patch   tokens } x \in \mathbb {R} ^ {N \times d}.
$$

然后用 Transformer block 处理这些 token。时间步 t 和类别/文本条件通过 conditioning注入。DiT 尝试多种 conditioning 方式：in-context token、cross-attention、adaptive layernorm、adaLN-Zero 等。最后 adaLN-Zero 成为重要设计：用时间和条件产生 LayerNorm的 scale/shift/gating，并把残差分支初始化为近零，使训练更稳定 [DiT, 2022]。

Transformer 化 diffusion 的关键代价是 attention 复杂度。若 latent patch token 数为 N，全局 attention 是 O(N<sup>2</sup>)。因此后续研究一边追求 scaling，一边引入更高压缩的 latent、更高效 attention、MoE、层次结构、masking、线性 attention 和蒸馏。

## 4.3 ⧥㨲➝➈

## 4.3.1 1. DiTᱶlatent patches + Transformer blocks

DiT 的输入是 noisy latent patches，加上 position embedding。每个 block 包含 self-attention 和 MLP，并用 adaLN conditioning：

$$
\operatorname{adaLN} (x, c) = \gamma (c) \frac {x - \mu (x)}{\sigma (x)} + \beta (c).
$$

adaLN-Zero 还引入 gate，使残差分支初始近零：

$$
x _ {l + 1} = x _ {l} + g _ {\mathrm{attn}} (c) \cdot \operatorname{Attn} (\operatorname{adaLN} (x _ {l}, c)).
$$

DiT 的实验结论很清楚：Gflops 和 FID 呈现良好 scaling，说明 Transformer backbone可以通过加深、加宽、减小patchsize获得更强生成能力[DiT,2022]。

## 4.3.2 2. U-ViT 㲓 MDTᱶ≿ U-Net ⲿ㬕▞⪰ Transformer

U-ViT 的口号是 all are worth words：time、condition、image patches 都作为 token 放进序列 [U-ViT, 2022]。它保留 long skip connection，把浅层细节和深层语义连接起来，吸收 U-Net 的经验。

MDT/MDTv2 则从训练效率出发。它在 latent token 上做 masking，用 asymmetric encoder-decoder 和 side-interpolater 学习 denoising；推理时移除辅助结构 [MDT, 2023]。这说明 DiT后续研究不仅追求更大模型，也追求更快训练。

## 4.3.3 3. PixArtᱶ㫡⼃⒱〉⤀⒴⪇

PixArt-alpha 的问题是：能不能用更低成本训练高质量 T2I Transformer？它采用三阶段训练：先学习低分辨率像素依赖，再学习文本-图像对齐，再高分辨率微调[PixArt-alpha,2023]。它还使用高质量自动标注和 T5 文本编码器，说明 DiT 系统不只靠主干，数据和训练 curriculum 同样关键。

PixArt-Sigma 继续改进弱到强训练、数据质量和高分辨率生成 [PixArt-Sigma, 2024]。

## 4.3.4 4. Hunyuan-DiTᮢLuminaᮢSanaᱶ⡽㨕⪇⧧✂㲗㬀㥥㟧

Hunyuan-DiT 采用双文本编码器、DiT backbone、中文/英文 prompt 适配和数据 convoy流程，强调工业级 T2I 系统中的数据、标注、多轮生成和中文能力 [Hunyuan-DiT, 2024]。

Lumina-T2X 追求统一生成不同分辨率、宽高比和模态形式的 next-DiT 框架 [Lumina-T2X, 2024]。Sana 则专注高效：高压缩 AE、Linear DiT、Gemma/VLM 相关文本编码、多语言能力，使高分辨率生成更快[Sana,2024]。

## 4.3.5 5. MMDiT 㲓 E-MMDiTᱶ㢶〉㟰㦡 token ☨㔪Ⰿ⩽⧧⡽㨕⪇

传统 LDM U-Net 用 cross-attention：图像 latent 查询文本 token。MMDiT 更进一步，让文本和图像各自有模态特定权重，并在 attention 中联合交互 [Stable Diffusion 3, 2024]。这更接近多模态 Transformer 的思路。

E-MMDiT 关注 MMDiT 的效率瓶颈，提出 Alternating Subregion Attention 等设计，在保持 GenEval 等指标的同时提高吞吐 [E-MMDiT, 2025]。这代表 MMDiT 后续研究的一条主线：既要保留文本-图像深交互，又要控制 attention 成本。

## 4.4 ⤴⮒⤇㖷⫊㢣■⿵

DiT block 的抽象：

```python
Input: noisy latent z_t, timestep t, condition c
patches = patchify(z_t)
tokens = linear_embed(patches) + position_embed
cond = embed(t, c)

for block in DiT:
    tokens = tokens + gate_attn(cond) * SelfAttention(adaLN(tokens, cond))
    tokens = tokens + gate_mlp(cond) * MLP(adaLN(tokens, cond))

prediction = unpatchify(linear_head(tokens))

MMDiT block 的抽象:

image_tokens = patch_embed(z_t)
text_tokens = text_encoder(prompt)

for block in MMDiT:
    image_qkv = image_specific_projection(image_tokens)
    text_qkv = text_specific_projection(text_tokens)
    joint_attention over concat(image_qkv, text_qkv)
    split updated image/text tokens
    apply modality-specific MLP / normalization
```

DiT 和 MMDiT 的差别不只是“有没有文本”，关键在于文本 token 参与生成动态的深度不同。

## 4.5 ⤴⮒⭲⤕㟰/➝➈㟰␚ⰶ

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/16552e24d0de12f73de7b7bff5bd991b40d499bce3979c963def313f898f2160.jpg)



㟰 4.1: 图 4-1：DiT 架构，来源：Peebles and Xie, 2022, Fig. 3。


这张图展示 latent patchify、Transformer blocks 和 conditioning。读图时要注意 DiT 工作在 VAE latent patch 上，而非像素 patch。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/32c59a9d22bcfa55e9e51aad2e2ed632962fdbb11617a79e3ab398437e0754e9.jpg)



㟰 4.2: 图 4-2：U-ViT 架构，来源：Bao et al., 2022, Fig. 1。


U-ViT 把 time、condition 和 image patches 都作为 token，并通过 long skip 保留多尺度信息。它说明 Transformer diffusion 仍然需要借鉴 U-Net 的信息流设计。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/2717aa3d42793fbfa6ab436ff5a0a9291347ac6e649fc348f81c0f527ebc6717.jpg)



㟰 4.3: 图 4-3：PixArt-alpha 架构，来源：Chen et al., 2023, Fig. 4。


PixArt 的图应和训练策略一起读：轻量化不只是模型结构，还包括数据标注、阶段训练和分辨率 curriculum。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/049f401b70d2980c2fe224ce19cb4ff272cb05e1e0b7a3e0b3c86f9a3bd0cc8d.jpg)



㟰 4.4: 图 4-4：SD3 MMDiT 架构，来源：Esser et al., 2024, Fig. 2a。


MMDiT的图要重点看文本和图像两条token流。它们有模态特定参数，又在attention中交互。这种设计比传统cross-attention更深地融合文本和图像。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/8579d79ffa5146b3a56d28d0cd973e21ba0a7556bb5c5ceb1311e5696e75e4d1.jpg)



㟰 4.5: 图 4-5：Sana 高效 Linear DiT 架构，来源：Xie et al., 2024, Fig. 5。


Sana的图代表高效化方向：更高压缩latent、更轻的DiT、更快attention和多语言条件。它说明MMDiT/DiT后续研究不只追求更大，也追求更便宜。

## 4.6 ⡡➝㦢☨㟨♇

第一，attention 成本高。分辨率越高，latent patch 越多，O(N<sup>2</sup>) 会成为瓶颈。Sana、E-MMDiT、DiT-MoE 等工作都在解决这点 [Sana, 2024][E-MMDiT, 2025][DiT-MoE, 2024]。

第二，latent 表示瓶颈更突出。Transformer 很会建模 token，但 token 本身如果来自弱VAE，细节、文字和空间结构会受限。DiT-RAE 用更强 representation autoencoder 挑战传统 VAE latent [DiT-RAE, 2025]。

第三，文本-图像融合成本高。MMDiT 增强交互，也增加计算。如何在深交互和吞吐之间平衡，是MMDiT 后续研究核心。

第四，训练数据和 caption 质量决定上限。PixArt 和 Hunyuan-DiT 都显示高质量标注、数据过滤、多语言 prompt 对效果非常关键 [PixArt-alpha, 2023][Hunyuan-DiT, 2024]。

## 4.7 ⧥㨲 insight

Transformer 化 diffusion 的核心 insight 是：生成模型正在从“图像卷积网络”变成“多模态token计算系统”。在U-Net时代，文本多半是条件；在MMDiT时代，文本token更深地参与生成动态。这个变化会让文生图、视频生成、多模态理解和LLM工程越来越接

近。

第二个insight是：DiT的scaling让生成模型进入类似LLM的研究节奏。更大模型、更好数据、更长训练、更强 tokenization、更高效 attention、更好 post-training，将成为主旋律。

## 4.8 㖯㬕ⰵ⿥

DiT 显示 Gflops 与 FID 有稳定相关，证明 Transformer diffusion 可以 scaling [DiT,2022]。U-ViT 显示 token 统一和 long skip 有效 [U-ViT, 2022]。MDT/MDTv2 显示 masking和 asymmetric structure 能显著提高训练效率 [MDT, 2023]。PixArt-alpha 以较低训练成本获得强 T2I 结果，说明数据和 curriculum 能大幅降低资源门槛 [PixArt-alpha, 2023]。Hunyuan-DiT 和 Sana 证明 DiT 可走向工业级、多语言和高效系统 [Hunyuan-DiT, 2024][Sana, 2024]。SD3 显示 MMDiT + rectified flow 有强 scaling 与人类偏好表现 [Stable Diffusion 3, 2024]。

## 4.9 ⳨㦎㲓㢦⹂⤀㾗

DiT/MMDiT 的局限集中在成本、表示和控制。全局 attention 贵，强 VAE/RAE 训练难，复杂 prompt grounding 仍不可靠。未来方向包括：线性/局部/稀疏 attention，MoE DiT，更强 latent encoder，MMDiT 蒸馏，flow matching 与 DiT 的联合设计，以及文本、图像、视频、3D token 的统一生成 backbone。

## 4.10 ⛣㠞㸆㮥㷦㱎⡡㷪㣇㖬ぼ

1. DiT 为什么在 latent patch 上工作。

2. adaLN-Zero 如何稳定 conditioning。

3. U-ViT 和 MDT 怎样把 U-Net/MAE 思想带回 Transformer diffusion。

4. PixArt为什么强调数据和训练阶段。

5. MMDiT 与传统 U-Net cross-attention 的差别。

6. Sana、E-MMDiT 等工作在解决哪些效率瓶颈。

## 4.11 ⡒㥠㢼㝘

1. DiT 的 patch size 变小会怎样影响 token 数和计算量？

2. adaLN-Zero 中 gate 初始化近零有什么好处？

## 4.11 复习问题

3. 为什么MDT 的mask只在训练时使用？

4. PixArt的三阶段训练分别在解决什么？

5. MMDiT 为什么需要模态特定参数？

6. 你如何判断一个DiT改进是真提升，还是只增加了训练计算？

## ☾5㷦 ⏳㬥ᮢ㸘⼿㲓⛶㋭ᱶ㑥⧨㑁 diffusion ⢚ⶼᮢ⢚⟛⧩㊭⧝

## 5.1 〉㷦㮔ⰶⴈ☨㢼㝘

基础 diffusion 给了稳定训练和强生成质量，但产品化会立刻遇到两个问题：慢，以及不一定符合用户偏好。慢来自多步采样；偏好不一致来自预训练目标和真实用户目标之间的差距。本章把这两条线放在一起讲，因为它们都属于“后训练/后处理生成轨迹”：采样器改变怎么走，蒸馏改变模型能用几步走完，对齐改变模型往什么目标走。

训练-free 加速线包括 DDIM、PNDM、DPM-Solver、DPM-Solver++、EDM sampler[DDIM, 2020][PNDM, 2022][DPM-Solver, 2022][DPM-Solver++, 2022][EDM, 2022]。训练式加速线包括 Progressive Distillation、Consistency Models、LCM、ADD [Progressive Distil-lation, 2022][Consistency Models, 2023][LCM, 2023][ADD, 2023]。偏好对齐线包括 DDPO、Diffusion-DPO、SPIN-Diffusion [DDPO, 2023][Diffusion-DPO, 2023][SPIN-Diffusion, 2024]。

## 5.2 ⭒㗯⌟Ⳃ

采样器问题可以抽象成数值积分。给定预训练denoiser，我们要从 $x _ { T }$ 走到 $x _ { 0 }$ ，步数越少，每步跨度越大，局部误差越容易累积。训练-freesampler不改模型参数，只改积分公式。训练式蒸馏则让学生模型学习大跨度更新，把teacher多步能力压进少步student。

偏好对齐问题可以抽象成目标错位。预训练损失是：

$$
\mathbb {E} \| \epsilon - \epsilon_ {\theta} (x _ {t}, t, c) \| ^ {2},
$$

用户偏好却可能是“更好看、更符合prompt、更少伪影、更安全、更像某种风格”。DDPO把最终图像 reward 作为 RL 信号，Diffusion-DPO 把 winner/loser 偏好对变成 logistic loss，SPIN-Diffusion 在缺少成对偏好时用模型自生成样本构造 self-play。

## 5.3 ⧥㨲➝➈

## 5.3.1 1. Training-free samplerᱶ⏥⡢㐦㺺ᱨ⡢⿁Ⳉ⹹㓞⪇

PNDM借用数值方法，使用历史噪声预测构造更高阶方向，例如Adams-Bashforth风格组合：

$$
\hat {\epsilon} _ {t} = \frac {1}{2 4} (5 5 \epsilon_ {t} - 5 9 \epsilon_ {t - 1} + 3 7 \epsilon_ {t - 2} - 9 \epsilon_ {t - 3}).
$$

DPM-Solver 针对 probability flow ODE 推导专用高阶求解器，把可解析线性项精确处理，只近似神经网络项 [DPM-Solver, 2022]。DPM-Solver++ 进一步发现强 guidance 下高阶solver 会不稳，于是使用 data prediction 形式和 dynamic thresholding 支持 guided sampling[DPM-Solver++, 2022]。

## 5.3.2 2. Progressive Distillation / Consistency / LCMᱶ≿✂⏧⹝㖠㫥ⱌ 㔕⏧㫓㔶

Progressive Distillation 每轮把步数减半：teacher 两小步的结果由 student 一大步模仿[Progressive Distillation, 2022]。Consistency Models 学习函数：

$$
f _ {\theta} (x _ {t}, t) \approx x _ {0},
$$

要求同一 ODE 轨迹上不同 noisy 点映射到一致的干净估计 [Consistency Models, 2023]。LCM 把这套思想迁移到 Stable Diffusion latent space，并把 CFG 轨迹蒸馏进学生，使 1-4步文生图成为可能 [LCM, 2023]。

## 5.3.3 3. ADDᱶ㱫 adversarial loss ⏣㔕⏧㥨Ⱞ

少步蒸馏常有细节软的问题。ADD 同时使用 teacher distillation 和 discriminator：

$$
L _ {\mathrm{ADD}} = L _ {\mathrm{distill}} + \lambda L _ {\mathrm{adv}}.
$$

teacher 负责语义和分布约束，discriminator 负责感知真实感 [ADD, 2023]。这是一种历史回环：GAN 的对抗损失回到diffusion中，用来修复one-step生成的锐度问题。

## 5.3.4 4. DDPO / Diffusion-DPO / SPINᱶ╹⧝ⶄ㟰☡㊭⧝⛶㋭

DDPO 把 denoising step 看成 policy：

$$
\pi_ {\theta} (x _ {t - 1} | x _ {t}, c) = p _ {\theta} (x _ {t - 1} | x _ {t}, c),
$$

最大化最终 reward：

$$
J (\theta) = \mathbb {E} _ {\tau \sim \pi_ {\theta}} [ r (x _ {0}, c) ].
$$

Diffusion-DPO 使用偏好对 $( x ^ { w } , x ^ { l } , c )$ 

$$
L = - \log \sigma \left(\beta [ \log \frac {p _ {\theta} (x ^ {w} | c)}{p _ {\mathrm{ref}} (x ^ {w} | c)} - \log \frac {p _ {\theta} (x ^ {l} | c)}{p _ {\mathrm{ref}} (x ^ {l} | c)} ]\right).
$$

在 diffusion 中，log-prob 用去噪损失相关项近似 [Diffusion-DPO, 2023]。SPIN-Diffusion使用 winner 数据和当前模型自生成样本做 self-play，减少对成对偏好数据的依赖 [SPIN-Diffusion, 2024]。

## 5.4 ⤴⮒⤇㖷⫊㢣■⿵

训练-free采样器：

```python
x_T ~ N(0, I)
history = []
for each time interval:
    pred = model(x_t, t)
    pred_hat = high_order_combine(pred, history)
    x_{t-1} = solver_update(x_t, pred_hat)
    history.append(pred)

一致性蒸馏:

sample x0, t_high
make noisy x_t_high
teacher_solver moves x_t_high to x_t_low
target = ema_student(x_t_low, t_low)
prediction = student(x_t_high, t_high)
loss = distance(prediction, target)

偏好对齐:

for prompt c:
    get winner image x_w and loser image x_l
    corrupt both to random noise level
    compute diffusion training losses under 0 and reference
    update 0 so winner becomes relatively more likely
```

## 5.5 ⤴⮒⭲⤕㟰/➝➈㟰␚ⰶ

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/cab4aa3ab86d959b1cddf29ff96b7822740942bd8e6b1309045e6f73a86f52af.jpg)



㟰 5.1: 图 5-1：DPM-Solver++ 强 guidance 下的稳定性对比，来源：Lu et al., 2022, Fig. 1。


这张图说明阶数更高不天然更好。强 guidance 会放大误差，采样器必须针对 guidedsetting 设计。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/c249ffa43a90696f79b8568db2cae6fe712e5c5b52170164b1d26103ab665774.jpg)



㟰 5.2: 图 5-2：LCM 少步生成示例，来源：Luo et al., 2023, Fig. 1。


LCM图要看1、2、4步之间细节和结构的变化。少步模型追求的是交互速度和质量的平衡。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/ea19baa5038256ca8e9b8e0883cd5ee083d2d57bc222079dcf5e3f97b7860b57.jpg)



㟰 5.3: 图 5-3：ADD 方法框架，来源：Sauer et al., 2023, Fig. 2。


ADD 图中有两条监督：teacher distillation 和 discriminator。少步生成要同时保留 teacher的结构知识和真实图像的细节统计。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/a589d7cee008a2d3f0da282752c613f67123954c1687a40242f130e9e24af28c.jpg)



㟰 5.4: 图 5-4：DDPO 用 reward 微调 diffusion，来源：Black et al., 2023, Fig. 1。


DDPO 图展示reward如何改变生成分布。它也提醒我们：reward是代理信号，优化它可能产生 reward hacking。

## 5.6 ⡡➝㦢☨㟨♇

第一，低步数容易牺牲细节和多样性。LCM、ADD能加速，但和完整多步模型相比仍有差距。

第二，采样器高度依赖 prediction type、CFG scale、噪声 schedule 和 latent/pixel 空间。一个scheduler在某模型上好，不保证在另一个模型上好。

第三，偏好优化容易过拟合代理指标。DDPO 的 aesthetic reward、Diffusion-DPO 的偏好数据、SPIN 的自生成负例都可能带来偏差。

第四，安全和版权不会因偏好优化自动解决。模型可能更会取悦评价器，同时保留训练数据记忆或有害内容生成能力。

## 5.7 ⧥㨲 insight

本章最重要的 insight 是：推理速度、样本质量和偏好对齐都在重塑生成轨迹。采样器用数值方法重塑轨迹；蒸馏用学生模型压缩轨迹；DPO/RL 用偏好信号改变轨迹落点。现代diffusion研究已经不只是预训练，后训练和推理算法同样决定用户体验。

## 5.8 㖯㬕ⰵ⿥

PNDM、DPM-Solver 和 DPM-Solver++ 显示不改权重也能显著减少 NFE [PNDM, 2022][DPM-Solver, 2022][DPM-Solver++, 2022]。Progressive Distillation 和 Consistency Models 显示训练式压缩能获得 one/few-step 生成能力 [Progressive Distillation, 2022][Consistency Models,2023]。LCM 证明少步蒸馏可以进入 Stable Diffusion 生态 [LCM, 2023]。ADD 证明 ad-versarial loss 能提升单步细节 [ADD, 2023]。DDPO、Diffusion-DPO、SPIN-Diffusion 证明diffusion 可以像 LLM 一样做偏好/奖励后训练 [DDPO, 2023][Diffusion-DPO, 2023][SPIN-Diffusion, 2024]。

## 5.9 ⳨㦎㲓㢦⹂⤀㾗

未来方向包括：更可靠的少步flow/consistency模型，更低成本的蒸馏，更抗rewardhacking 的偏好优化，多目标 reward 组合，安全约束下的后训练，以及能同时报告速度、质量、多样性、对齐和安全的评测协议。

## 5.10 ⛣㠞㸆㮥㷦㱎⡡㷪㣇㖬ぼ

1. Training-free sampler 和 distillation 的区别。

2. PNDM/DPM-Solver 为什么属于数值求解路线。

3. Consistency/LCM 为什么能少步生成。

4. ADD 为什么重新引入 adversarial loss。

5. DDPO 和 Diffusion-DPO 的数据接口差异。

6. 偏好优化的 reward hacking 风险。

## 5.11 ⡒㥠㢼㝘

1. DPM-Solver++ 为什么比 DPM-Solver 更适合强 guidance？

2. Progressive Distillation 为什么逐级减半步数？

3. Consistency Model 的“一致性”指什么？

4. ADD 中 distillation loss 和 adversarial loss 分别约束什么？

5. DDPO 为什么可以把 diffusion 看成 RL policy？

6. Diffusion-DPO 如何把 winner/loser 图像对变成训练信号？

## ☾6㷦 ⶨ㺨ᮢ⍌⭃㲓⢔㩂⪇ᱶ╹ SDEdit ☡ ControlNetᮢIP-Adapter

## 6.1 〉㷦㮔ⰶⴈ☨㢼㝘

基础文生图模型的输入是文本，但用户经常想要更具体的控制：保持一张草图的结构，替换图中某个物体，学习一个特定人物，保留姿态和边缘，参考另一张图片的风格或主体。文本prompt太弱，无法稳定指定空间布局、身份和局部修改。本章把控制、编辑、个性化放在同一个框架里讲。

核心论文包括 SDEdit、Textual Inversion、Prompt-to-Prompt、DreamBooth、Null-textInversion、InstructPix2Pix、Custom Diffusion、GLIGEN、ControlNet、T2I-Adapter、Perfu-sion、DragDiffusion、IP-Adapter [SDEdit, 2021][Textual Inversion, 2022][Prompt-to-Prompt,2022][DreamBooth, 2022][ControlNet, 2023][IP-Adapter, 2023]。

## 6.2 ⭒㗯⌟Ⳃ

控制可以按“改哪里”分成四类。

<table><tr><td>类型</td><td>输入</td><td>目标</td><td>代表方法</td></tr><tr><td>图像编辑</td><td>原图、mask、prompt</td><td>修改局部或整体风格</td><td>SDEdit, Instruct-Pix2Pix, Null-text Inversion</td></tr><tr><td>文本注意力编辑</td><td>prompt 替换、attention map</td><td>保持布局改语义</td><td>Prompt-to-Prompt</td></tr><tr><td>个性化</td><td>少量主体图片</td><td>学一个新 token/主体</td><td>Textual Inversion, DreamBooth, Custom Diffusion, Perfusion</td></tr><tr><td>结构/图像条件控制</td><td>边缘、深度、pose、box、image prompt</td><td>精确控制布局和参考图</td><td>GLIGEN, Control-Net, T2I-Adapter, IP-Adapter</td></tr></table>

这些方法共享一个思想：围绕已有diffusion的条件接口、attention、adapter或少量参数做小改动，用较低成本获得可控性。

## 6.3 ⧥㨲➝➈

## 6.3.1 1. SDEditᱶ⭩㵑㴿㔶⒱ᱨ㊿⧼⌏㸊⧧㸊㖯⡮

SDEdit从用户输入图x 出发，加到某个噪声水平t：

$$
x _ {t} = \sqrt {\bar {\alpha} _ {t}} x + \sqrt {1 - \bar {\alpha} _ {t}} \epsilon .
$$

再从 $x _ { t }$ 反向去噪。噪声越小，越保留原图；噪声越大，模型越自由，真实感更强[SDEdit,2021]。这给编辑任务提供了一个非常朴素的旋钮。

## 6.3.2 2. Textual Inversion / DreamBoothᱶ≿㨰㻙㝛➥ⱌㄩ㨻╰⪻

Textual Inversion 冻结扩散模型，只学习一个新 token embedding v∗，让 prompt 中的特殊词表示某个主体或风格 [Textual Inversion, 2022]：

$$
v ^ {*} = \arg \min _ {v} \mathbb {E} \| \epsilon - \epsilon_ {\theta} (x _ {t}, t, \operatorname{prompt} (v)) \| ^ {2}.
$$

DreamBooth则微调整个模型或部分参数，用少量主体图片和raretoken绑定身份，同时用 prior preservation loss 避免模型把类别先验学坏 [DreamBooth, 2022]。

## 6.3.3 3. Prompt-to-Promptᱶ⍌⭃ cross-attention

Prompt-to-Prompt 观察到文生图中的 cross-attention map 控制文本 token 和图像区域的对应关系。若只替换 prompt 中某个词，同时注入原始 attention map，可以保留布局、改动语义 [Prompt-to-Prompt, 2022]。它不需要重新训练模型，直接操控生成过程中的 attention。

## 6.3.4 4. GLIGEN / ControlNet / T2I-Adapterᱶ≿ⶥ⭺㝫⮔Ⱗⱌㄩ㨻

GLIGEN 使用 grounding token 和 gated self-attention，把 box、phrase、keypoint 等 ground-ing 信息注入冻结 diffusion [GLIGEN, 2023]。ControlNet 复制一份 U-Net 分支，用零卷积连接到冻结主干，使边缘、深度、pose等条件能强力控制生成，同时不破坏原模型[Control-Net, 2023]。T2I-Adapter 使用更轻的 adapter，为冻结 T2I 模型提供结构条件 [T2I-Adapter,2023]。

## 6.3.5 5. IP-Adapterᱶ≿ image prompt 㾗㢜⛢⻮㝫⮔㟜☤

IP-Adapter 的关键是 decoupled cross-attention：文本 cross-attention 和图像 cross-attention分开，让模型同时读 prompt 和参考图 [IP-Adapter, 2023]。这比把图像特征简单拼进文本token 更稳定，也让 image prompt 能和 ControlNet 等结构条件组合。

## 6.4 ⤴⮒⤇㖷⫊㢣■⿵

统一控制框架：

```txt
Input:
prompt c
optional source image x_src
optional subject images S
optional spatial condition m (edge/depth/pose/box)
optional reference image r

Choose control route:
editing: add noise to x_src, denoise with c
personalization: learn token/LoRA/partial weights from S
spatial control: encode m with ControlNet/Adapter/GLIGEN
image prompt: encode r with image encoder + IP-Adapter

During denoising:
combine text condition, spatial condition, image condition
update latent with guided sampler 
```

## 6.5 ⤴⮒⭲⤕㟰/➝➈㟰␚ⰶ

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/41c673e45969ebe8f74d86a07af2ca37acc1282a230764f3bb07b77ceade8124.jpg)



㟰 6.1: 图 6-1：SDEdit 方法总览，来源：Meng et al., 2021, Fig. 1。


SDEdit 的图展示“先破坏再恢复”的编辑思想。加噪强度就是保真和真实感之间的旋钮。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/8a9e85624de64b7878091812ebd6a4df7f238c5dff978291b4d3c5f68892294a.jpg)



㟰 6.2: 图 6-2：Prompt-to-Prompt 方法总览，来源：Hertz et al., 2022, Fig. 3。


这张图要看 cross-attention injection：模型沿用原 attention 结构，在对应词语的区域上改变语义内容。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/fb1c856bb178e249ed80c07dcba2448103939423dbc6094767537262381dfd44.jpg)



㟰 6.3: 图 6-3：DreamBooth 个性化流程，来源：Ruiz et al., 2022, Fig. 3。


DreamBooth 图展示 rare token 与主体绑定。个性化的难点是既记住具体主体，又保

留类别可组合性。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/0a26c7fddc3fc7c29992602e85be69c8edd2c441a3373164b1d2c03073ab8202.jpg)



㟰 6.4: 图 6-4：ControlNet block design，来源：Zhang et al., 2023, Fig. 2。


ControlNet的零卷积连接让新增控制分支从零影响开始训练，逐步学习结构条件，避免一开始破坏冻结主干。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/3d154725c7cf3c00986a562f73b42a12929e0775610041f123676a20762acc49.jpg)



㟰 6.5: 图 6-5：IP-Adapter decoupled cross-attention，来源：Ye et al., 2023, Fig. 2。


IP-Adapter的图展示文本和图像条件分离。这个设计让参考图成为独立控制通道，而

不是伪装成一段文本。

## 6.6 ⡡➝㦢☨㟨♇

第一，控制越强，自由度越低。ControlNet 能保姿态和边缘，但也可能让图像僵硬。IP-Adapter 保主体相似，也可能压制 prompt 创造力。

第二，个性化容易过拟合。DreamBooth会记住主体，也可能把主体绑定到固定姿态、背景或风格。

第三，编辑要同时保持 identity、layout 和自然度。SDEdit 的噪声强度、Prompt-to-Prompt 的 attention 注入时间、Null-text Inversion 的优化步数都需要权衡。

第四，多控制组合容易冲突。pose、depth、reference image、text prompt 可能给出互相不一致的约束。

## 6.7 ⧥㨲 insight

控制与编辑的核心 insight 是：大型生成模型本身已经学到丰富视觉先验，研究重点转向“如何以最小代价打开合适接口”。Textual Inversion 打开 embedding 接口，Prompt-to-Prompt 打开 attention 接口，ControlNet 打开 U-Net feature 接口，IP-Adapter 打开 imageprompt接口。好的控制方法通常会在关键位置加一个可控阀门，用小接口调动大先验。

## 6.8 㖯㬕ⰵ⿥

SDEdit 显示加噪强度可以平衡保真和真实感 [SDEdit, 2021]。Textual Inversion 和DreamBooth 证明少量图片可注入新概念 [Textual Inversion, 2022][DreamBooth, 2022]。Prompt-to-Prompt 证明 cross-attention map 与布局控制紧密相关 [Prompt-to-Prompt, 2022]。GLI-GEN、ControlNet、T2I-Adapter显示冻结基础模型加轻量结构条件可实现强空间控制[GLI-GEN, 2023][ControlNet, 2023][T2I-Adapter, 2023]。IP-Adapter 证明 image prompt 可以作为独立条件与文本条件共存 [IP-Adapter, 2023]。

## 6.9 ⳨㦎㲓㢦⹂⤀㾗

未来控制系统要解决可组合性、冲突消解和跨模态一致性。用户会同时给文本、草图、参考图、深度、mask、人物身份和风格，模型需要自动判断哪些约束优先。另一个方向是把控制方法迁移到 DiT/MMDiT 和视频生成中，因为 U-Net 时代的 ControlNet 结构不能直接照搬到所有 Transformer diffusion。

## 6.10 ⛣㠞㸆㮥㷦㱎⡡㷪㣇㖬ぼ

1. SDEdit的噪声强度控制什么。

2. Textual Inversion 和 DreamBooth 的参数更新范围差异。

3. Prompt-to-Prompt 为什么操控 cross-attention。

4. ControlNet 的零卷积为什么重要。

5. T2I-Adapter 和 ControlNet 的轻重差异。

6. IP-Adapter 的 decoupled cross-attention 解决什么。

## 6.11 ⡒㥠㢼㝘

1. 如果用户想保持人物身份但换背景，应该优先考虑哪些方法？

2. 如果用户给一张边缘图和一张参考风格图，ControlNet与IP-Adapter怎样组合？

3. DreamBooth 的 prior preservation loss 防什么？

4. Prompt-to-Prompt 对大幅布局变化为什么困难？

5. ControlNet 迁移到 MMDiT 可能遇到哪些结构问题？

## ☾7 㷦 ⶷ゅ㝛㔶⒱ᱶ㯞㊷ᮢ㗍㊷ᮢ3D㲓✂ゅ㝛 foundation models

## 7.1 〉㷦㮔ⰶⴈ☨㢼㝘

前面几章主要讨论图像：一个样本可以看成二维像素网格或latent网格。真实世界的生成任务远不止图像。音频是一维时间波形或二维声谱图，视频是带时间轴的图像序列，3D是在多视角中保持几何一致的空间结构，多媒体系统还要同时生成画面、运动、声音和可编辑对象。本章要解决的问题是：diffusion为什么能从图像自然扩展到这些对象，扩展过程中最难的变量是什么。

这章会把 DiffWave、AudioLDM、Video Diffusion Models、Make-A-Video、Imagen Video、Video LDM、AnimateDiff、Stable Video Diffusion、Latte、CogVideoX、Movie Gen、HunyuanVideo、DreamFusion、Magic3D、Zero-1-to-3、ProlificDreamer 放在同一个框架里理解 [Dif-fWave, 2020][AudioLDM, 2023][VDM, 2022][Make-A-Video, 2022][Imagen Video, 2022][VideoLDM, 2023][AnimateDiff, 2023][SVD, 2023][Latte, 2024][CogVideoX, 2024][Movie Gen, 2024][Hun-yuanVideo, 2024][DreamFusion, 2022][Magic3D, 2022][Zero123, 2023][ProlificDreamer, 2023]。

## 7.2 ⭒㗯⌟Ⳃ

跨媒体 diffusion 的统一视角是：我们仍然学习一个去噪函数，只是样本空间从 $x \in$ R $H \times W \times C$ 变成更复杂的结构。

音频可以直接用波形 $x \in \mathbb { R } ^ { L }$ ，也可以先转成 mel-spectrogram 或 latent。DiffWave 直接在波形上扩散，用条件网络把mel条件注入到反向生成中[DiffWave,2020]。AudioLDM则采用latentdiffusion，把音频先编码成潜空间，再让文本通过CLAP一类音频-文本表示进入条件通道 [AudioLDM, 2023]。这与 Stable Diffusion 的图像 latent 思想相似：高维原始信号太贵，就先学一个可逆性足够好的压缩空间。

视频多了时间轴。如果视频 latent 记作 $z \in \mathbb { R } ^ { T \times H ^ { \prime } \times W ^ { \prime } \times C }$ ，模型不仅要生成每一帧的画质，还要保证帧间一致、运动自然、长时物体身份不漂移。早期VideoDiffusionModels使用空间-时间分解的 3D U-Net，把图像扩散的卷积和 attention 拓展到视频 [VDM, 2022]。Make-A-Video和ImagenVideo都走级联路线：先生成低分辨率短视频，再用时间和空间超分模型逐级提高帧率、分辨率和长度 [Make-A-Video, 2022][Imagen Video, 2022]。VideoLDM 则把 latent diffusion 带到视频领域：先有强图像 LDM，再插入 temporal layers 做视

频微调 [Video LDM, 2023]。

3D 的难点更微妙。模型可以生成多视角图像、NeRF、mesh、Gaussian 或蛋白/材料中的三维坐标，但 3D 对象必须在不同视角下说同一件事。DreamFusion 使用二维文生图 diffusion 作为“老师”，通过 Score Distillation Sampling 优化一个 NeRF，让渲染图被 2Ddiffusion 认为符合 prompt [DreamFusion, 2022]。Magic3D 把这个流程做成粗到细两阶段，提高纹理和几何质量 [Magic3D, 2022]。Zero-1-to-3 将“输入一张图 + 目标相机位姿”变成条件扩散任务，先学新视角合成，再作为 3D 重建的监督 [Zero123, 2023]。ProlificDreamer进一步指出 SDS 容易过饱和和模式塌缩，引入 Variational Score Distillation，把 3D 参数分布纳入优化 [ProlificDreamer, 2023]。

## 7.3 ⧥㨲➝➈

## 7.3.1 1. 㯞㊷ᱶ╹⏒㨼㐣㵑☡㯞㊷ latent diffusion

DiffWave的直觉很适合入门：把干净语音逐步加成高斯噪声，训练网络根据噪声语音和扩散步数预测噪声，再反向一步步恢复波形 [DiffWave, 2020]。如果有 mel-spectrogram条件，模型就生成与谱图匹配的语音；如果无条件，也可以生成自然音频片段。它的网络结构类似 WaveNet 的 dilated convolution，原因是音频有长程时间依赖，普通局部卷积看不到足够长的上下文。

AudioLDM 的进步在于把文本-音频对齐和 latent diffusion 结合起来。它先把音频压入VAElatent，再在latent上运行U-Net去噪，文本条件通过音频-文本联合表征注入[Au-dioLDM, 2023]。这样做有两个好处：第一，采样成本下降；第二，文本 prompt 可以描述“雨声、脚步声、远处汽车”这类语义事件，模型在音频latent中生成对应声纹。

音频生成要记住一个核心区别：图像的空间坐标比较稳定，音频的时间尺度差异很大。一个爆破音可能几十毫秒，一个环境声可能几十秒。模型若只优化局部声谱质量，容易失去事件级结构；若只看全局语义，容易出现细节糊掉和节奏不准。

## 7.3.2 2. 㗍㊷ᱶ㖫⭺␍ᮢ⭌⻶㲓 latent ⪇

视频diffusion的第一代主线是“把图像模型加上时间”。VDM在U-Net中引入空间-时间分解模块：空间卷积处理每帧内容，时间模块处理帧间变化[VDM,2022]。这比直接使用完整3Dconvolution省算力，也更容易从图像模型迁移。

Make-A-Video继承文本到图像模型的语义能力，再用未标注视频学习运动。这里的关键思想是：文本-图像数据多，文本-视频数据少；如果文本语义已经由图像模型学好，视频数据主要负责教模型“怎么动”[Make-A-Video, 2022]。Imagen Video 进一步使用多级视频 diffusion，从低分辨率低帧率逐级到高分辨率视频，并通过 v-prediction、progressivedistillation 等技巧提高采样质量和效率 [Imagen Video, 2022]。

Video LDM 更像 Stable Diffusion 的视频化版本：在图像 LDM 的基础上加入 temporallayers，先保持空间生成能力，再让模型学习时间一致性 [Video LDM, 2023]。AnimateDiff把这个思想做成更可插拔的motionmodule：基础文生图模型负责外观，motionmodule学会让外观动起来 [AnimateDiff, 2023]。Stable Video Diffusion 强调大规模数据清洗和 stagedtraining：先做图像预训练，再做视频预训练，最后做高质量视频微调[SVD,2023]。

进入 2024 年后，视频生成明显走向 Transformer foundation model。Latte 将视频切成时空 patch，用类似 DiT 的结构做 latent video diffusion，并比较多种空间和时间 attention 排布 [Latte, 2024]。CogVideoX 使用 3D VAE、Expert Transformer、3D RoPE 和多分辨率帧打包解决长视频、不同分辨率和大运动问题 [CogVideoX, 2024]。Movie Gen 和 HunyuanVideo则把视频、音频、个性化、编辑、I2V 等功能装进系统级工程：数据过滤、caption pipeline、3DVAE、Transformerbackbone、并行训练、上采样和多任务后训练都成为模型能力的一部分 [Movie Gen, 2024][HunyuanVideo, 2024]。

## 7.3.3 3. 3Dᱶ㱫✠㢞㥸㬕㴢㗲㑻㢞⛶㦣

DreamFusion 的巧妙之处在于复用 2D diffusion 的知识。设 3D 表示为参数 $\phi$ ，渲染器给出某个相机视角下的图像 $x = g ( \phi , c a m e r a )$ 。预训练文生图 diffusion 能提供一个 score，用来告诉当前渲染图朝哪个方向更像文本prompt。SDS 的梯度常写成：

$$
\nabla_ {\phi} \mathcal {L} _ {\mathrm{SDS}} \approx \mathbb {E} _ {t, \epsilon , c a m e r a} \left[ w (t) (\epsilon_ {\theta} (x _ {t}, t, y) - \epsilon) \frac {\partial x}{\partial \phi} \right].
$$

这个式子直观上说：如果 diffusion 预测的噪声和真实噪声不一致，就把这个差异反传到 3D 表示，让下一次渲染更符合文本 [DreamFusion, 2022]。Magic3D 发现只用低分辨率 NeRF 容易几何粗糙，于是先优化粗 NeRF，再用高分辨率 mesh/texture 细化 [Magic3D,2022]。Zero-1-to-3 把相机位姿显式输入扩散模型，使模型能从单图预测新视角，减少纯文本 SDS 中多面脸和 Janus artifact [Zero123, 2023]。ProlificDreamer 的 VSD 则把优化目标从单个 3D 点估计扩展到 3D 分布，缓解过强 CFG 和单模式优化带来的质量问题[ProlificDreamer, 2023]。

## 7.4 ⤴⮒⤇㖷⫊㢣■⿵

视频 latent diffusion 的基本训练目标：

$$
z _ {0} = E (x _ {1: T}), \quad z _ {t} = \alpha_ {t} z _ {0} + \sigma_ {t} \epsilon , \quad \mathcal {L} = \mathbb {E} \| \epsilon - \epsilon_ {\theta} (z _ {t}, t, c) \| ^ {2}.
$$

这里E 是视频VAE或逐帧图像VAE加时间模块，c可以是文本、首帧、参考图、音频或相机轨迹。相比图像， $z _ { 0 }$ 多了时间维，所以模型需要在空间质量、时间一致和运动幅度之间折中。

统一跨媒体生成流程：

```txt
Input:
condition c: text / image / audio / camera / trajectory
target domain D: audio, video, 3D, multi-modal 
```

```txt
Encode:
choose representation z
audio: waveform, spectrogram, or audio latent
video: 3D latent tokens
3D: NeRF, mesh, multi-view latent, or scene parameters 
```

```txt
Train denoiser:
sample noise level t
corrupt z0 to zt
predict noise, velocity, or flow
add domain-specific losses when needed 
```

```txt
Sample:
start from noise
denoise with condition c
decode to waveform / frames / 3D asset
optionally upsample, edit, align audio, or refine geometry 
```

时空token数量的成本可以写成：

$$
N = T \cdot H ^ {\prime} \cdot W ^ {\prime}, \quad \text { AttentionCost } = O (N ^ {2}).
$$

这就是视频 Transformer 必须使用 latent、patching、window、factorized attention、contextparallel或多阶段生成的原因。

## 7.5 ⤴⮒⭲⤕㟰/➝➈㟰␚ⰶ

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/abc6771dadb70ddcd65d021be5a889d1001687a9a9a7482e71396626d3226be7.jpg)



㟰 7.1: 图 7-1：DiffWave 反向生成与条件波形建模，来源：Kong et al., 2020, Fig. 1。


DiffWave 的图把音频扩散讲得很直观：训练时把真实波形推向噪声，采样时从噪声一步步回到波形。它告诉我们 diffusion 不依赖图像网格，只要能定义加噪和去噪，就能处理连续信号。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/a20c3215d3519f15ca28385c77c6ecd976890e4a7af799515f81fe550da51891.jpg)



㟰 7.2: 图 7-2：AudioLDM 训练与采样主流程，来源：Liu et al., 2023, Fig. 1a。


AudioLDM的图要看两个空间：音频VAElatent负责高效生成，CLAP语义空间负责文本到音频的对齐。它把文生图系统中的“文本编码器+latentdiffusion”搬到音频领域。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/57997a9ed89ef888976dfe14e835684a3f9669f937397072f2ad5225b7acff53.jpg)



㟰 7.3: 图 7-3：Video Diffusion Models 的空间-时间分解 3D U-Net，来源：Ho et al., 2022, Fig. 1。


这张图的重点是把视频 U-Net 拆成空间处理和时间处理。视频生成并非简单逐帧生成，时间模块承担身份保持、动作连续和镜头动态。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/460bc2a66b404aa54b84f39a4ff32f833c4f91f9820ac8fea4eab6f676c84eff.jpg)



㟰 7.4: 图 7-4：Video LDM 中 temporal layers 插入空间 LDM 骨架，来源：Blattmann et al., 2023, Fig. 4。


VideoLDM的图适合理解“图像模型视频化”：空间backbone来自成熟图像LDM，新增时间层负责帧间关系。这一设计让视频模型继承图像质量，同时用较少视频数据学习运动。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/10d27c51e0ddf49ec8902ec91ff3324c500801fe075707ee381c21db9fa23ecd.jpg)



㟰 7.5: 图 7-5：CogVideoX 总体架构，来源：Yang et al., 2024, Fig. 3。


CogVideoX的图展示新一代视频模型的系统复杂度：3DVAE压缩视频，文本编码器提供语义，Transformer backbone 在时空 latent 上去噪，训练和推理还要处理并行、位置编码和长视频。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/e69850f40f005c056cf8dea7de2a998c47dd90d5e97f9ff8e62917d6fbd6f56b.jpg)



㟰 7.6: 图 7-6：Movie Gen Video 总体 pipeline，来源：Meta, 2024, Fig. 3。


Movie Gen 的 pipeline 说明视频 foundation model 已经变成“生成系统”：基础视频模型、空间上采样、时间扩展、个性化、编辑和音频生成协作，单个denoiser已经解释不了全部能力。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/b37c71ce4d6616373823ac3fee9e4d2acce010e261fbc5d867fbf417571cac78.jpg)



㟰 7.7: 图 7-7：DreamFusion algorithm overview，来源：Poole et al., 2022, Fig. 1。


DreamFusion 的图展示 2D diffusion 如何监督 3D：不断随机选视角、渲染图像、用文生图模型给梯度，再更新3D 表示。它是“用生成模型作为优化器老师”的代表。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/e5f52258d3e79dc2983f50f14c954839e9de78b74594993494ed1460fb759d65.jpg)



㟰 7.8: 图 7-8：Zero-1-to-3 view-conditioned diffusion 总览，来源：Liu et al., 2023, Fig. 3。


Zero-1-to-3的图把相机位姿放入条件通道。它把单图新视角生成变成可训练任务，为后续3D 重建提供比纯文本更强的几何约束。

## 7.6 ⡡➝㦢☨㟨♇

第一，时间一致性难。视频模型常见失败包括身份漂移、物体突然消失、背景纹理跳动、运动不符合物理。越长的视频，早期帧与后期帧越难保持同一语义世界。

第二，数据稀缺和数据噪声严重。图像-文本对已经很噪，视频-文本对更难，因为caption 需要描述动作、镜头、事件顺序和时间关系。Movie Gen、CogVideoX、HunyuanVideo都花大量篇幅讨论数据过滤、密集 caption、质量分层和训练课程 [CogVideoX, 2024][MovieGen, 2024][HunyuanVideo, 2024]。

第三，计算成本陡增。视频latent的token数量随TH′W′ 增长，attention成本平方增长。3D生成还要在每步采样中渲染多个视角，DreamFusion类方法通常采样慢、优化久。

第四，评价更困难。图像可以看单张美观度和文本一致性，视频还要看运动自然度、时间连贯性、镜头合理性、音画同步和长时故事一致。3D还要看多视角一致、几何可制造性、纹理完整和物理可用性。

第五，跨媒体对齐难。视频配音需要音频事件和画面事件同步；I2V需要保持输入图身份；3D 需要不同视角共享同一几何；个性化视频需要人物身份和动作同时稳定。

## 7.7 ⧥㨲 insight

跨媒体 diffusion 的核心 insight 是：扩散过程本身很通用，真正变化的是“表示空间”和“条件接口”。音频需要时间信号表示，视频需要时空latent和时间模块，3D需要可微渲染或几何等变表示，多媒体系统需要多个生成器之间的协调。很多研究看起来领域很分散，其实都在回答同一个问题：怎样选择一个既能被 diffusion 去噪、又能保留领域结构的表示。

另一个重要insight是“先继承，再补足”。Make-A-Video继承图像语义再补运动，VideoLDM 继承图像 LDM 再补 temporal layers，AnimateDiff 继承个性化图像模型再补 motionmodule，DreamFusion 继承 2D 文生图先验再补 3D 表示，Movie Gen 和 HunyuanVideo 继承大规模 T2V 训练再补编辑、音频、个性化和 I2V。跨媒体生成的扩展路径通常会把已有强先验迁移到更复杂对象上。

## 7.8 㖯㬕ⰵ⿥

DiffWave 在语音合成中显示 diffusion 可以达到高质量波形生成 [DiffWave, 2020]。Au-dioLDM 证明 latent audio diffusion 能做文本到音频、音频修补和风格迁移 [AudioLDM,2023]。VDM、Make-A-Video、Imagen Video 说明视频生成可以通过空间-时间模块与级联超分逐步扩大分辨率和时长 [VDM, 2022][Make-A-Video, 2022][Imagen Video, 2022]。VideoLDM、AnimateDiff、SVD证明图像LDM通过时间层、运动模块和高质量视频微调可转为强视频模型 [Video LDM, 2023][AnimateDiff, 2023][SVD, 2023]。Latte、CogVideoX、MovieGen、HunyuanVideo 进一步说明 Transformer backbone、3D VAE、数据工程和大规模训练正在成为视频生成的主流形态 [Latte, 2024][CogVideoX, 2024][Movie Gen, 2024][Hunyuan-Video, 2024]。

3D 方向中，DreamFusion 证明 2D diffusion 可以无 3D 数据地监督 3D 生成 [Dream-Fusion, 2022]；Magic3D 证明粗到细和高分辨率 prior 能提升几何纹理 [Magic3D, 2022]；Zero-1-to-3 证明显式视角条件能显著强化新视角合成 [Zero123, 2023]；ProlificDreamer 证明改进 SDS 的分布建模能缓解过饱和和模式塌缩 [ProlificDreamer, 2023]。

## 7.9 ⳨㦎㲓㢦⹂⤀㾗

音频模型仍然难以稳定生成长程结构，例如音乐的主题回归和复杂声场。视频模型的最大瓶颈是长时一致、可控运动和真实物理。3D 模型的瓶颈是几何准确、拓扑稳定、材质真实和可编辑性。系统层面还需要更好的数据治理，因为大规模视频和音频数据涉及版权、隐私、人物身份与合成内容标注。

未来的重要方向包括：更强的3D/4Dlatent表示、音画同步生成、可交互视频世界模型、可编辑3Dasset生成、长视频叙事控制、低成本推理和更可信的跨媒体评测。视频生成和世界模型、具身智能之间也会越来越接近：当模型能生成动作后果，它就不只是生成内容，也在学习动态世界。

## 7.10 ⛣㠞㸆㮥㷦㱎⡡㷪㣇㖬ぼ

1. 音频、视频、3D 生成与图像diffusion的共同点。

2. DiffWave 和 AudioLDM 分别在哪个表示空间去噪。

3. VDM、Make-A-Video、Imagen Video、Video LDM 的视频化策略差异。

4. 为什么视频生成需要 temporal layers、3D VAE、级联超分和数据清洗。

5. SDS 如何把2D 文生图模型变成3D 优化的监督信号。

6. DreamFusion、Magic3D、Zero-1-to-3、ProlificDreamer 各自解决哪类 3D 痛点。

7. MovieGen和HunyuanVideo这类系统论文为什么要同时讨论模型、数据、训练和产品功能。

## 7.11 ⡒㥠㢼㝘

1. 为什么逐帧生成视频会导致时间不一致？

2. Video LDM 为什么可以从强图像 LDM 出发？

3. 级联视频diffusion的每一级分别承担什么？

4. 3DSDS 的梯度从哪里来，又为什么会产生过饱和问题？

5. Zero-1-to-3 的相机条件对 3D 重建有什么帮助？

6. 如果要设计一个文本到带音频视频模型，你会把音频条件放在哪个阶段？

## ☾ 8 㷦 ⳱㔩㲓ⴈ␉ᱶdiffusion 㑥⧨㔶 ⒱⥈⬹ᮢ⛑㾗⧧VLA

## 8.1 〉㷦㮔ⰶⴈ☨㢼㝘

在图像和视频里，diffusion生成的是像素或latent。在机器人和决策任务里，生成对象变成“未来要做什么”。这听起来跨度很大，但数学形式很接近：轨迹可以看成一个序列，动作 chunk 可以看成一个小段连续控制信号，规划可以看成在约束下补全未来状态和动作。本章要解决的问题是：为什么 diffusion 适合做决策，如何从离线轨迹规划走到真实机器人控制，再走到视觉-语言-动作大模型。

核心论文包括 Diffuser、Decision Diffuser、Diffusion Policy、DP3、RDT-1B 和 $\pi _ { 0 } [ \mathrm { D i f f u s e r } ,$ 2022][Decision Diffuser, 2022][Diffusion Policy, 2023][DP3, 2024][RDT-1B, 2024][pi0, 2024]。

## 8.2 ⭒㗯⌟Ⳃ

具身智能中的“生成”指向能被执行的动作。一个轨迹可以写成：

$$
\tau = (s _ {0}, a _ {0}, s _ {1}, a _ {1}, \ldots , s _ {H}, a _ {H}).
$$

其中 $s _ { t }$ 是状态， $a _ { t }$ 是动作，H是规划horizon。传统强化学习通常学习策略 $\pi ( a _ { t } | s _ { t } )$ 或价值函数 $Q ( s _ { t } , a _ { t } )$ 。diffusion决策把视角换成：学习轨迹分布 $p ( \tau )$ 或条件轨迹分布 $p ( \tau \vert c )$ 采样时再用目标、奖励、约束或语言指令引导生成。

这个视角非常适合三类问题。

第一，多模态行为。比如把杯子拿起来可以从左侧抓，也可以从右侧抓；显式回归均值会把两条可行动作平均成一条不可执行动作。diffusion天然能表示多峰分布。

第二，长时规划。单步策略容易短视，整段轨迹生成可以一次考虑目标状态、避障、技能组合和中间状态。

第三，高维连续控制。机器人手臂动作是连续向量，双臂或灵巧手动作维度更高，diffusion的连续去噪过程能逐步修正动作序列。

## 8.3 ⧥㨲➝➈

## 8.3.1 1. Diffuserᱶ≿⥈⬹☕㾗㟰㦡㮥㬥㐣㵑

Diffuser的核心想法很大胆：把一条轨迹排成二维数组，横轴是时间，纵轴是状态和动作维度，然后像扩散图像一样加噪、去噪[Diffuser,2022]。训练时模型学习从噪声轨迹恢复真实轨迹；规划时从噪声开始采样，并通过 reward gradient 或约束引导轨迹往高回报方向走。

它的优势是统一。条件生成、inpainting、避障、目标到达、warm-start都可以转化成“固定轨迹中的一部分，补全剩下部分”。例如 Maze2D 任务中，起点和终点固定，中间路径由模型补全；blockstacking中，目标堆叠结构固定，动作序列由模型生成。

Diffuser的局限也清楚：它通常需要在每次控制前生成整条轨迹，采样步骤多，实时性弱；如果环境偏离计划，需要重新规划。

## 8.3.2 2. Decision Diffuserᱶ≿Ⰵ⺆ᮢㅅ⍖⧧⭒ㅢ㾗㢜㝫⮔

Decision Diffuser 进一步把决策 diffusion 组织成条件轨迹生成 [Decision Diffuser, 2022]。它关注一个问题：轨迹生成模型如何听从不同目标。条件可以是回报、终点、约束、技能标签，甚至可以组合多个约束。

直观理解：Diffuser 学会“什么样的轨迹像数据集中的轨迹”，Decision Diffuser 学会“在给定目标或回报条件下，什么样的轨迹合理”。这让diffusion从无条件轨迹建模走向可控规划。论文中的Kuka、Unitree等实验强调了约束组合能力：给出不同目标、障碍或技能提示，模型可以采样出满足条件的轨迹。

## 8.3.3 3. Diffusion Policyᱶ╹⥈⬹⥂⪆㽊㢜⛑㾗 chunk ⶨ㺨

Diffusion Policy 是把 diffusion 真正带入真实机器人控制的重要工作 [Diffusion Policy,2023]。它根据当前观测生成未来一小段动作：

$$
a _ {t: t + H _ {a}} \sim p _ {\theta} (a _ {t: t + H _ {a}} \mid o _ {t}).
$$

这里 $O _ { t }$ 可以是图像、机器人本体状态或多视角观测。模型每个控制周期生成一个action chunk，只执行前几步，然后滚动更新。这种 receding horizon 方式同时保留规划感和闭环反馈。

它的一个关键贡献是把diffusion用作高维多模态策略。显式策略容易平均多峰动作，隐式策略训练和采样不稳定；DiffusionPolicy用去噪过程生成动作序列，可以在Push-T、tooluse、双臂操作等任务中处理接触丰富、多解和扰动恢复。

## 8.3.4 4. DP3ᱶ㑁 diffusion policy 㺓Ⱗⶄ 3D ♇㴬

DP3关注真实操作中的感知表示[DP3,2024]。二维RGB图像会受视角、遮挡、纹理影响；机器人很多操作更依赖几何位置。DP3 使用 3Dpointcloudencoder提取场景几何，再用diffusionpolicy生成动作。它的核心判断是：如果控制任务本质是“在三维空间里抓、推、插、放”，点云比纯 RGB 更直接。

DP3 的训练和测试流程都围绕“3D 表示 + diffusion action head”。点云 encoder 提取局部和全局几何特征，动作 diffusion 在条件特征下去噪。实验表明，DP3 在模拟和真实机器人上都有更好的泛化，尤其在物体姿态变化、视角变化和几何任务中更稳。

## 8.3.5 5. RDT-1Bᱶ▙⥂ㄩ robot diffusion transformer

RDT-1B将动作生成模型推到大模型尺度[RDT-1B,2024]。它把机器人观测、语言指令和动作序列组织成 transformer 可处理的 token，使用 diffusion/flow 风格目标生成动作。RDT 的难点不只是模型规模，还包括跨机器人形态、双臂动作维度、不同数据源、指令增强和稳定训练。

RDT-1B 采用机器人数据混合、动作条件注入、QK-Norm/RMSNorm 等稳定训练技巧，并强调 action chunk 的生成。对于刚入门的同学，一个好记法是：Diffusion Policy 像“小而强的动作生成器”，RDT-1B像“把动作生成器扩展成机器人基础模型”。

## 8.3.6 6. pi0ᱶVLM + flow action expert

π 是 VLA 方向的重要代表 [pi0, 2024]。它把视觉-语言理解和连续动作生成放在一起：模型既要读懂图像和语言指令，也要输出机器人动作。其方法图中，VLM主干提供语义理解，action expert 使用 flow matching/diffusion 风格目标生成连续动作 chunk。

这里的关键变化是：机器人策略不再只是模仿某个数据集中的动作模式，它开始吸收大规模视觉语言知识。语言可以指定任务，视觉可以定位物体，动作head则把语义意图落到连续控制。对具身智能来说，这意味着 diffusion/flow action model 正在成为 VLA的底层执行接口。

## 8.4 ⤴⮒⤇㖷⫊㢣■⿵

轨迹 diffusion 的训练目标：

$$
\tau_ {t} = \alpha_ {t} \tau_ {0} + \sigma_ {t} \epsilon , \quad \mathcal {L} = \mathbb {E} \| \epsilon - \epsilon_ {\theta} (\tau_ {t}, t, c) \| ^ {2}.
$$

其中c 可以是目标状态、回报、语言、图像观测或任务标签。

Diffusion Policy 的滚动控制伪代码：

```txt
Input:
    current observation o_t
    action horizon H_a
    execute horizon H_e

Loop:
    encode observation o_t
    initialize action chunk A with Gaussian noise
    for denoising step k:
    predict noise or velocity conditioned on o_t
    update A
    execute first H_e actions from A
    receive new observation 
```

如果用flowmatching形式描述动作生成，可以写成：

$$
a _ {\tau} = (1 - \tau) a _ {0} + \tau a _ {1}, v _ {\theta} (a _ {\tau}, \tau , o) \approx a _ {1} - a _ {0}.
$$

这里 $a _ { 0 }$ 是噪声动作， $a _ { 1 }$ 是专家动作，模型学习一条从噪声到专家动作的速度场。这和第2章的FlowMatching是同一思想，只是对象从图像latent换成了动作向量。

## 8.5 ⤴⮒⭲⤕㟰/➝➈㟰␚ⰶ

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/80fed5a177aebd45a981cd4d3b399ed0a6349d03ab9830489a9f16e8206eca60.jpg)



㟰 8.1: 图 8-1：Diffuser 轨迹数组与 guidance，来源：Janner et al., 2022, Fig. 2。


![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/a8050f990cb559b2e956edaa6082f6acaf75e419fe20795ab27f7b2244755b32.jpg)


这张图把轨迹当作可去噪的数组。横轴是时间，纵轴是状态和动作维度。规划时可以固定起点、终点或某些状态片段，再让模型补全可行动作。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/e3c69d1d6f9fa8a0191b6530d705f0fcdde1156d6616a1693dc09ebc7e2131d8.jpg)



㟰 8.2: 图 8-2：Decision Diffuser 规划过程图，来源：Ajay et al., 2022, Fig. 2。


DecisionDiffuser的图展示条件如何控制采样轨迹。它把回报、目标和技能变成生成条件，使同一个轨迹模型能完成多类决策任务。


Output:Action Sequence



a) Diffusion Policy General Formulation



㟰 8.3: 图 8-3：Diffusion Policy 总体结构，来源：Chi et al., 2023, Fig. 1/2。


Diffusion Policy 的图要看“观测条件 + 动作去噪”。模型生成未来动作 chunk，并通过滚动执行形成闭环控制。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/05d926abf7633575ee1d9ae1e8edbecba7e1d2fcbba4b463353e5ad37032bec1.jpg)



㟰 8.4: 图 8-4：DP3 点云感知模块，来源：Ze et al., 2024, Fig. 1/方法图。


DP3 的图展示点云 encoder 如何给动作 diffusion 提供三维几何信息。它适合解释为什么具身任务不能只依赖二维视觉特征。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/49a276304e6571f0672dbf931b0fd069e8e91f87006dd21fd3222d30ac513957.jpg)



㟰 8.5: 图 8-5：RDT-1B 总体框架，来源：Liu et al., 2024, Fig. 1。


RDT-1B的图展示机器人基础模型的输入输出：多模态观测、语言指令、机器人状态进入Transformer，模型输出可执行动作。关键是规模化和异构数据统一。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/e2131186c23c690af39497837588b0fbe361e9ef559fd4d555bffb44de5810d0.jpg)



㟰 8.6: 图 8-6：pi0 总体方法图，来源：Black et al., 2024, Fig. 1。


π 的图适合看 VLA 的整体分工：视觉语言主干理解任务，action expert 负责连续动作生成。它把diffusion/flow从决策算法推进到通用机器人策略接口。

## 8.6 ⡡➝㦢☨㟨♇

第一，实时性。图像生成可以等几秒，机器人控制常常要求几十毫秒级响应。多步采样必须被蒸馏、减少步数或转为flowpolicy，才能在真实机器人上稳定运行。

第二，闭环性。离线规划一次生成整条轨迹，真实环境却会滑动、碰撞、遮挡和偏移。Diffusion Policy 的 receding horizon 正是为了解决这一点：每次只执行短片段，快速用新观测纠偏。

第三，数据分布窄。机器人数据昂贵，不同机器人之间动作空间、相机位置、夹爪、任务风格都不同。RDT-1B和 $\pi _ { 0 }$ 需要数据混合、指令增强和跨embodiment对齐。

第四，评价复杂。图像生成看相似度和偏好即可，机器人要看成功率、安全、碰撞、泛化、执行时间、扰动恢复和硬件损耗。

第五，语义到动作的断层。VLM 能理解“把红杯子放进抽屉”，但把这句话变成抓取点、力控制、避障轨迹和放置动作仍然困难。actiondiffusionhead是桥，但桥的两端仍需大量数据和精细对齐。

## 8.7 ⧥㨲 insight

具身diffusion的核心insight是：动作和轨迹本身也是可以建模的连续数据分布。与其让模型输出一个平均动作，不如让模型在动作分布中采样一条可执行解。对于多解、接触丰富、长时依赖的任务，这一点尤其重要。

第二个 insight 是“生成式策略天然适合约束补全”。起点、终点、目标、语言、避障、已执行动作、部分轨迹都可以作为条件，模型补全剩下的动作。这与图像inpainting、视频延展、3D 多视角补全在形式上高度相似。

第三个 insight 是 VLA 时代需要把语义理解和动作生成分层。视觉语言模型负责读懂任务，diffusion/flow action head 负责连续控制。两者之间的接口质量决定模型能否从“懂话”走向“会做”。

## 8.8 㖯㬕ⰵ⿥

Diffuser 证明离线 RL 可以通过轨迹 diffusion 完成规划、inpainting 和 guided sampling[Diffuser, 2022]。Decision Diffuser 证明回报、目标和技能条件可以组合控制生成轨迹 [De-cision Diffuser, 2022]。Diffusion Policy 在真实机器人任务上展示多模态动作生成、扰动恢复和双臂操作能力 [Diffusion Policy, 2023]。DP3 显示点云表示能提升三维操作任务的泛化 [DP3, 2024]。RDT-1B 和 $\pi _ { 0 }$ 则说明 action diffusion/flow 可以进入大规模 VLA 框架，成为通用机器人策略的重要组件 [RDT-1B, 2024][pi0, 2024]。

## 8.9 ⳨㦎㲓㢦⹂⤀㾗

当前具身 diffusion 仍然依赖高质量示教数据，长时任务的任务分解和失败恢复还不够稳定。模型在训练数据外的物体、场景、动力学变化下可能出现危险动作。另一个未解决问题是动作生成与符号规划、工具使用、世界模型之间的组合：高层模型应当规划子目标，低层diffusionpolicy 应当执行子目标，二者需要可验证接口。

未来方向包括少步动作diffusion、在线纠错、跨机器人动作token统一、仿真到真实迁移、物理约束注入、主动数据收集和安全验证。对于研究者来说，最值得关注的是“动作生成模型如何与大规模视觉语言模型耦合”，这会直接影响下一代具身基础模型。

## 8.10 ⛣㠞㸆㮥㷦㱎⡡㷪㣇㖬ぼ

1. 为什么轨迹可以像图像一样被加噪和去噪。

2. Diffuser 与 Decision Diffuser 的条件控制差异。

3. Diffusion Policy 为什么生成 action chunk，并用 receding horizon 执行。

4. DP3 为什么引入点云表示。

5. RDT-1B 和 $\pi _ { 0 }$ 怎样把 diffusion/flow action model 接入 VLA。

6. 具身diffusion的实时性、闭环性和数据问题。

## 8.11 ⡒㥠㢼㝘

1. 为什么单步动作回归容易失败于多模态任务？

2. Diffuser 的 trajectory inpainting 可以解决哪些规划问题？

3. Diffusion Policy 为什么只执行 action chunk 的前几步？

4. 点云相对RGB 图像在机器人操作中有什么优势？

5. VLM 负责什么，action expert 负责什么？

6. 如果机器人执行中物体滑动，生成式策略应如何重新规划？

## ☾ 9 㷦 AI4Scienceᱶ➶㽳ᮢ☔⊅ᮢ⏮⼛ 㲓㝢㋺㺲☨ⰵ⤕㔶⒱

## 9.1 〉㷦㮔ⰶⴈ☨㢼㝘

科学生成任务和图像生成有一个本质差别：生成结果必须服从物理、化学或几何约束。图像中一条桌腿稍微歪一点可能仍然好看，分子中的键长、键角、构象能量、蛋白骨架、晶体周期性、天气变量守恒关系都不能随意出错。本章要解决的问题是：diffusion如何生成带结构约束的科学对象，为什么等变性、周期性、几何参数化和不确定性建模如此重要。

核心论文包括 CDVAE、GeoDiff、Equivariant Diffusion for Molecules、FoldingDiff、Diff-Dock、FrameDiff、RFdiffusion、FrameFlow、MatterGen、GenCast，以及时间序列和时空 dif-fusion survey [CDVAE, 2021][GeoDiff, 2022][EDM Molecules, 2022][FoldingDiff, 2022][Diff-Dock, 2022][FrameDiff, 2023][RFdiffusion, 2023][FrameFlow, 2023][MatterGen, 2023][Gen-Cast, 2024][Spatiotemporal Diffusion Survey, 2024]。

## 9.2 ⭒㗯⌟Ⳃ

科学对象通常具有对称性。对称性属于任务定义的一部分。以 3D 分子为例，如果把整个分子平移或旋转，分子性质不应改变；如果模型因为坐标系改变而给出不同结果，就学错了问题。我们常说模型要满足SE(3) 等变或不变。

不变性指输出不随变换改变：

$$
f (R x + t) = f (x).
$$

等变性指输入被旋转平移后，输出也以同样方式变换：

$$
f (R x + t) = R f (x) + t.
$$

分子构象生成需要等变坐标更新；蛋白backbone生成需要在残基局部frame上扩散；晶体材料生成需要处理周期边界和lattice；天气预报需要生成未来多个可能状态，因为大气系统混沌，单个确定预测无法表达不确定性。

这一章可以按对象类型理解。

<table><tr><td>对象</td><td>表示</td><td>核心约束</td><td>代表方法</td></tr><tr><td>分子构象</td><td>原子类型 + 3D 坐标</td><td>旋转平移等变、键长键角合理</td><td>GeoDiff, EDM Molecules</td></tr><tr><td>分子 docking</td><td>配体姿态 + 蛋白口袋</td><td>平移、旋转、扭转自由度</td><td>DiffDock</td></tr><tr><td>蛋白骨架</td><td>残基坐标、角度、局部 frame</td><td>SE(3) 几何、可设计性</td><td>FoldingDiff, FrameDiff, RFd-iffusion</td></tr><tr><td>晶体材料</td><td>原子、fractional coordinate、lattice</td><td>周期性、稳定性、对称性</td><td>CDVAE, MatterGen</td></tr><tr><td>天气时空场</td><td>球面网格、多变量时间序列</td><td>时空相关、不确定性、极端事件</td><td>GenCast</td></tr></table>

## 9.3 ⧥㨲➝➈

## 9.3.1 1. ⲹ㝛⏮⼛ᱶCDVAE 㲓 MatterGen

CDVAE 处理周期晶体材料生成 [CDVAE, 2021]。晶体由 unit cell 无限重复形成。模型需要生成原子类型、fractional coordinates 和 lattice parameters。CDVAE 用 encoder 把晶体编码成latent，再通过扩散解码器生成结构。它的关键点是把周期边界作为图结构的一部分，避免模型把晶体当成普通有限点云。

MatterGen 更进一步，把晶体生成做成可控 diffusion [MatterGen, 2023]。它在原子类型、坐标和 lattice 上进行联合去噪，并支持 chemical system、space group、band gap、magneticdensity、bulkmodulus等条件。这里的“条件生成”很重要：科学应用通常需要满足目标性质和可合成约束的候选材料。

可以把材料生成理解为一个多目标搜索问题：模型先给出结构候选，再用稳定性、唯一性、新颖性、性质预测和物理模拟筛选。diffusion 提供的是高质量 proposal distribution，后续还需要第一性原理计算、数据库比对和实验验证。

## 9.3.2 2. ➶㽳⤕㦣ᱶGeoDiff 㲓 Equivariant Diffusion

GeoDiff 关注 drug-like molecule 的构象生成 [GeoDiff, 2022]。同一个分子图可以有多个3D构象，构象决定能量、结合姿态和性质。GeoDiff在原子坐标上加噪和去噪，并使用图神经网络建模原子间关系。它强调equivariantMarkovprocess：如果输入坐标整体旋转，去噪方向也应整体旋转。

Equivariant Diffusion for Molecules 直接把原子位置和原子特征放进等变 diffusion 框架 [EDM Molecules, 2022]。模型通过 E(n)-equivariant GNN 预测噪声，使生成过程满足欧氏空间对称性。它可以做无条件分子生成，也可以做条件性质生成。对初学者来说，这篇论文最重要的点是：科学 diffusion 的网络结构不能随便选，必须让归纳偏置匹配物理对称性。

## 9.3.3 3. DockingᱶDiffDock ☨㽫㜢➶⏦

分子对接的任务是预测小分子配体如何进入蛋白结合口袋。传统方法常把docking当成打分搜索或回归最优姿态。DiffDock 把它看成生成配体姿态分布 [DiffDock, 2022]。姿态由平移、旋转和可旋转键扭转角构成，模型在这些自由度上扩散和去噪。

DiffDock的一个重要洞见是：docking常常有多个合理候选，回归均值会出问题。生成多个姿态，再用 confidence model 排序，更适合真实药物发现流程。它的 selective prediction也很实用：当模型置信度高时给出结构，置信度低时提示需要更多计算或实验。

## 9.3.4 4. ☔⊅㔶⒱ᱶ╹Ⱋ⛪☡ frameᱨ㴿☡ RFdiffusion

FoldingDiff采用蛋白 backbone 的内部角表示 [FoldingDiff, 2022]。它在 ϕ, ψ, ω 等角度序列上做diffusion，生成后再转成3Dbackbone。这种表示天然避免部分坐标系问题，但角度到三维结构的全局几何仍然复杂。

FrameDiff 使用残基局部 frame 表示蛋白骨架 [FrameDiff, 2023]。每个残基有位置和朝向，扩散过程发生在SE(3)frame上。这样做的好处是能直接建模蛋白backbone的三维几何，又能尊重旋转平移结构。FrameFlow 用 flow matching/ODE 视角处理类似问题，采样路径更直接 [FrameFlow, 2023]。

RFdiffusion 是蛋白设计中的里程碑 [RFdiffusion, 2023]。它基于 RoseTTAFold denois-ing idea，把蛋白结构逐步去噪，并支持多种条件：无条件 backbone 生成、motifscaffolding、binder design、对称结构、fold conditioning 等。它强在把结构预测网络的先验、diffusion生成和功能条件设计结合起来。蛋白设计评价也不只看结构长得像，还要看designability：生成backbone后，是否能找到氨基酸序列折回该结构。

## 9.3.5 5. 㝢㋺㲓㖫ⶥ⒉ᱶGenCast

GenCast 将 diffusion 用于中期天气集合预报 [GenCast, 2024]。天气预报不是单张图像生成，它是多变量球面时空场的条件生成：给定过去天气状态，生成未来多个可能轨迹。集合预报的价值在于表达不确定性，尤其对极端天气和能源系统很重要。

GenCast使用扩散模型生成未来天气场分布，并用CRPS等概率预报指标评价。它的结果说明 diffusion 不只适用于视觉内容，也适用于复杂物理系统中的概率预测。时间序列与时空diffusionsurvey也显示，交通、气候、医疗、生物信号、金融等场景都可用“条件历史 + 未来分布生成”的框架组织 [Spatiotemporal Diffusion Survey, 2024]。

## 9.4 ⤴⮒⤇㖷⫊㢣■⿵

科学结构 diffusion 的通用形式：

$$
x _ {t} = \alpha_ {t} x _ {0} + \sigma_ {t} \epsilon , \quad \mathcal {L} = \mathbb {E} \| \epsilon - \epsilon_ {\theta} (x _ {t}, t, c) \| ^ {2},
$$

但这里的 x 可能是坐标、角度、lattice、姿态、frame 或时空场。真正重要的是让 $\epsilon _ { \theta }$ 满足领域对称性。

等变去噪要求：

$$
\epsilon_ {\theta} (R x _ {t} + t _ {0}, t, c) = R \epsilon_ {\theta} (x _ {t}, t, c).
$$

蛋白/材料生成后的筛选流程：

Input: 

condition c: property / motif / binding pocket / composition / weather history 

Generate candidates: 

sample N structures or trajectories with diffusion 

Validate: 

check geometry constraints 

compute stability or confidence 

evaluate target property 

remove duplicates and memorized structures 

Refine: 

run physics simulator, structure predictor, docking score, or DFT 

keep candidates that pass domain filters 

## 9.5 ⤴⮒⭲⤕㟰/➝➈㟰␚ⰶ

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/319a24bed8cb28d8ca2a159c2d26d1a471e9fbb0305c8d1b304352973e9f9c5c.jpg)



㟰 9.1: 图 9-1：CDVAE 编码、属性预测和扩散解码流程，来源：Xie et al., 2021, Fig. 2。


CDVAE 的图要看两件事：晶体先被编码成 latent，解码时同时处理 lattice 和原子位置。周期性晶体不能直接当作普通点云，unitcell与邻接关系是模型的一部分。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/47b4cdf481532c7a14bd7e014ca8f579de936881737f37c29396e9a9d0b8a2df.jpg)



㟰 9.2: 图 9-2：Equivariant Diffusion for Molecules 训练与采样框架，来源：Hoogeboom et al., 2022, Fig.2。


这张图展示分子从噪声点云逐步变成带原子类型的 3D 结构。关键是去噪网络使用等变GNN，保证坐标系变化不会改变物理含义。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/3a5e01fd63ff669e84c8ebdb12bdb26592b4d05053b4571b6bfbdbd63411152b.jpg)



㟰 9.3: 图 9-3：DiffDock 主流程图，来源：Corso et al., 2022, Fig. 1。


DiffDock的图把docking分解为平移、旋转和扭转自由度上的扩散。配体姿态从噪声分布开始，逐步进入蛋白口袋，并通过置信度模型排序。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/01599e3786e0155d5d62ffe6d6cff9bb0748a84954636f305d1ab4e12c6b42e9.jpg)



㟰 9.4: 图 9-4：FrameDiff 残基 frame 参数化，来源：Yim et al., 2023, Fig. 1A。


FrameDiff的图说明蛋白backbone不只是点坐标，还包含每个残基的局部坐标系。用frame表示可以同时描述位置和朝向，适合SE(3) 几何生成。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/0b871293b554bfe3dc1f4cb232fabe62d7c34c0aeb92925903e26e0fb9cd011e.jpg)



㟰 9.5: 图 9-5：RFdiffusion 条件蛋白设计任务总览，来源：Watson et al., 2023, Fig. 1b。


RFdiffusion的图展示同一个结构去噪框架如何支持不同设计条件：motif、binder、sym-metry、unconditional backbone。它的价值在于把 diffusion 变成蛋白工程工具箱。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/c6f1695915d8a2fa4e5722fa7429bb2dfbf6463784ee5d2c94bc351fb7d894c5.jpg)



㟰 9.6: 图 9-6：MatterGen 晶体 forward corruption 与 reverse denoising，来源：Zeni et al., 2023, Fig. 1a。


![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/99a60fb9a6cc7371874c1b6dbdfcbd56f491bd93f1c7bf36b4881c0ff90513fa.jpg)



㟰 9.7: 图 9-7：GenCast 方法总览，来源：Price et al., 2024, Fig. 1。


GenCast的图把扩散模型放进天气集合预报流程：历史天气状态作为条件，模型生成未来多个样本，再用概率预报指标评价。它说明 diffusion 在科学预测中常常用于生成分布，而不只是单点答案。

## 9.6 ⡡➝㦢☨㟨♇

第一，生成质量必须接受领域验证。图像生成的美观不等于科学有效；分子要看化学有效性，蛋白要看可设计性，材料要看稳定性和合成可能，天气要看概率校准和极端

事件。

第二，对称性和坐标系处理很容易出错。普通神经网络可能学到与坐标系相关的伪规律，导致旋转或平移后结果不一致。

第三，数据集偏差很强。已知材料、蛋白和药物都来自人类探索过的狭窄区域，生成模型可能只会在已知化学空间附近插值。

第四，评价成本高。材料需要DFT，蛋白需要结构预测和实验，药物docking需要更高精度模拟，天气需要长时回放和多指标比较。生成模型只是候选产生器，后续验证占据大量成本。

第五，条件控制难。要求“高 band gap、低供应链风险、稳定、含某些元素”的材料，或要求“保留 motif、结合某靶点、可表达”的蛋白，都是多目标条件生成。目标之间经常冲突。

## 9.7 ⧥㨲 insight

AI4Science diffusion 的核心 insight 是：科学生成要把“逐步去噪”嵌入科学对象的正确表示空间。表示一旦选错，模型再大也会学到错误归纳偏置；表示选对后，扩散模型可以在复杂约束下给出多样候选。

第二个 insight 是生成和验证必须成对出现。CDVAE、MatterGen、RFdiffusion、Diff-Dock、GenCast都不是只给样本图，它们都强调稳定性、置信度、可设计性、选择性预测或概率预报指标。科学领域需要“生成候选+可信筛选”的闭环。

第三个 insight 是多样性本身有科学价值。药物发现需要多个候选姿态，蛋白设计需要多种scaffold，天气预报需要ensemble，材料搜索需要大量可筛选结构。diffusion的随机采样能力正好适合这种探索式任务。

## 9.8 㖯㬕ⰵ⿥

CDVAE 展示周期晶体生成和属性预测可以结合 [CDVAE, 2021]。GeoDiff 与 EDMMolecules 表明等变 diffusion 能生成合理分子构象和分子样本 [GeoDiff, 2022][EDM Molecules,2022]。DiffDock 显示生成多个 docking pose 并用 confidence 排序可以提升实用性 [Diff-Dock, 2022]。FoldingDiff、FrameDiff、RFdiffusion 和 FrameFlow 说明蛋白结构生成需要从角度、frame、结构预测先验和 flow 采样等多条路线共同推进 [FoldingDiff, 2022][FrameD-iff, 2023][RFdiffusion, 2023][FrameFlow, 2023]。MatterGen 显示条件材料生成可以面向化学系统、对称性和目标性质 [MatterGen, 2023]。GenCast 则说明 diffusion 可以做高质量概率天气预报 [GenCast, 2024]。

## 9.9 ⳨㦎㲓㢦⹂⤀㾗

科学diffusion的局限不只在模型分数，也在实验闭环。很多生成结构在指标上好看，但合成、表达、稳定、毒性、成本、环境影响都可能失败。另一个局限是数据闭环慢：模型提出候选，实验验证后再反馈训练，周期很长。

未来工作包括更强物理约束的生成模型、可微模拟与 diffusion 联合、主动学习、实验机器人闭环、多尺度表示、生成结果可解释性和安全审查。材料、蛋白、药物和天气都会从“生成一个样本”转向“生成带置信度、可验证路径和候选排序的一组方案”。

## 9.10 ⛣㠞㸆㮥㷦㱎⡡㷪㣇㖬ぼ

1. 不变性和等变性的区别。

2. 为什么分子、蛋白、材料生成不能忽视坐标系和物理约束。

3. CDVAE 与 MatterGen 怎样处理周期晶体。

4. GeoDiff、EDM Molecules 和 DiffDock 的任务差异。

5. FoldingDiff、FrameDiff、RFdiffusion 分别使用什么蛋白表示。

6. GenCast为什么使用概率集合预报。

7. 科学生成为什么必须与验证和筛选结合。

## 9.11 ⡒㥠㢼㝘

1. 如果把分子整体旋转，模型输出应该怎样变化？

2. 晶体材料生成为什么需要lattice和周期边界？

3. DiffDock 为什么生成多个 pose 再排序？

4. 蛋白backbone用角度表示和frame表示各有什么优缺点？

5. RFdiffusion 的 motif scaffolding 解决什么问题？

6. 天气预报中ensemble比单点预测有什么价值？

# ☾10㷦 ㋂␌ᮢ≠㐩ᮢ⡽㨕⪇㲓㢦⹂⿁ 㦏

## 10.1 〉㷦㮔ⰶⴈ☨㢼㝘

学完前九章后，我们已经知道diffusion可以生成图像、视频、音频、3D、动作和科学结构。最后必须回答一个更现实的问题：如何判断这些模型真的好、真的安全、真的可用。高分辨率样图很容易让人兴奋，但研究和产品都需要系统评测：文本是否被正确理解，组合关系是否准确，训练数据是否被记忆，采样是否足够快，部署是否可控，失败模式是否可诊断。

本章把 text-to-image survey、vision diffusion survey、training data extraction、T2I-CompBench、GenEval、video diffusion survey 和 efficient diffusion survey 作为材料，建立一套从质量、对齐、安全、效率到未来研究路线的判断框架 [T2I Survey, 2023][Vision Diffusion Survey,2022][Training Data Extraction, 2023][T2I-CompBench, 2023][GenEval, 2023][Video Diffu-sion Survey, 2024][Efficient Diffusion Survey, 2024]。

## 10.2 ⭒㗯⌟Ⳃ

早期生成模型常用FID、IS、NLL这类指标。FID衡量生成图像和真实图像在Inceptionfeature空间中的分布距离：

$$
\mathrm{FID} = \left\| \mu_ {r} - \mu_ {g} \right\| ^ {2} + \mathrm{Tr} \left(\Sigma_ {r} + \Sigma_ {g} - 2 (\Sigma_ {r} \Sigma_ {g}) ^ {1 / 2}\right).
$$

它有用，但只回答“分布像不像”，不能回答“prompt里有两个红球和一个蓝方块时，模型是否画对数量、颜色、关系”。CLIPScore 衡量文本和图像 embedding 相似度，也容易被全局语义欺骗。比如图片里有一只猫和一辆车，CLIP可能给高分，却不检查“猫在车下面”还是“猫在车上面”。

于是评测从单一分数转向能力拆解。T2I-CompBench把组合能力分成颜色、形状、纹理、空间关系、数量、复杂组合等维度 [T2I-CompBench, 2023]。GenEval 用目标检测器和规则化 prompt 检查 object presence、counting、color binding、position、attribute binding等 [GenEval, 2023]。Video diffusion survey 提醒我们：视频还要评估时间一致、运动自然、文本-视频对齐、长时故事和自动指标局限 [Video Diffusion Survey, 2024]。

安全维度也不可缺。Training Data Extraction from Diffusion Models 证明扩散模型可能记忆并再现训练样本，尤其在重复样本、过拟合或特定提示下 [Training Data Extraction,2023]。这说明 diffusion 的风险不只是“生成不好”，也包括隐私泄漏、版权争议、身份滥用和可追溯性不足。

效率则贯穿全书。Efficientdiffusionsurvey将高效化分成训练、采样、架构、参数高效微调、压缩、部署等方向 [Efficient Diffusion Survey, 2024]。从 DDIM、DPM-Solver 到LCM/Consistency，从 U-Net 到 DiT/MMDiT，从 full fine-tuning 到 LoRA/adapter，从云端批量到端侧交互，效率直接决定模型能否被日常使用。

## 10.3 ⧥㨲➝➈

## 10.3.1 1. 㾉⧩㋂␌ᱶ╹᮰㦡⏥㦡᮱☡᮰㱸ゃ㱸≢⪈㾖

T2I-CompBench 的价值在于把文本理解拆开 [T2I-CompBench, 2023]。一个 prompt 可能包含多个对象、属性和关系。模型生成的图片整体看起来不错，但可能把颜色绑定错、数量画错、空间关系颠倒。比如“a red cube on a blue sphere”中，模型可能画出 red sphere和 blue cube。人眼一看就知道错，FID 和 CLIPScore 未必敏感。

GenEval 更进一步，用可程序化的 prompt 和检测器构造评测 [GenEval, 2023]。它问的问题很朴素：该有的物体是否出现？数量是否正确？颜色是否绑定到正确对象？两个物体的左右关系是否正确？这种评测不完美，因为检测器也会错，但它比单个全局相似度更接近生成模型的实际短板。

## 10.3.2 2. 㗍㊷㋂␌ᱶ㮔ⶄ㖫⭺㢞⛪

视频生成的评测比图像更难。一个视频模型可能单帧画质很好，但帧间闪烁严重；也可能运动自然，但prompt中的动作没发生。Videodiffusionsurvey将视频评测分为视觉质量、时间一致、文本对齐、多样性、人类偏好和应用指标 [Video Diffusion Survey, 2024]。

常见指标包括 FVD、CLIP-based text-video alignment、人类偏好、motion consistency、temporal warping consistency 等。关键是不要只看某一个指标。FVD 可能偏向数据集统计，CLIP 可能忽略细节，人类评测成本高且主观。好的protocol 应该组合自动指标、人工偏好和可控probe，例如固定prompt，只改变数量、运动方向、镜头轨迹或时间顺序。

## 10.3.3 3. 㗷⳯⭝㯎㲓㯨㙵ᱶㄩ㨻⶙ㅢ⡒㦆㫡⼃㬥〉

Training Data Extraction from Diffusion Models 的核心提醒是：生成模型可能记住训练图像，并在特定采样策略下复现 [Training Data Extraction, 2023]。风险与重复样本、训练轮数、模型容量、提示选择和采样策略有关。论文通过 membership inference、nearestneighbor、重复图像分析和自适应阈值展示了提取风险。

对研究者来说，这意味着数据清洗不是可选项。去重、隐私过滤、版权管理、敏感人物保护、水印和模型输出审计都应进入训练流程。对使用者来说，这意味着模型生成内容需要溯源和风险提示，尤其在人脸、医疗、私人图像和艺术作品上。

## 10.3.4 4. ⡽㨕⪇ᱶ╹㔕⏧⏳㬥☡㥥㟧⏩㗪

高效 diffusion 可以分成五层。

第一，采样器高效化。DDIM、PNDM、DPM-Solver、DPM-Solver++、EDM sampler 都在减少反向步数。第二，蒸馏高效化。Progressive Distillation、Consistency Models、LCM、ADD 把多步教师压成少步学生。第三，架构高效化。latent diffusion、3D VAE、patchify、linear attention、MMDiT 分流、MoE、token 压缩都在减少计算。第四，训练高效化。LoRA、adapter、ControlNet、IP-Adapter 等方法减少全量微调成本。第五，部署高效化。量化、缓存、并行、端云协同、批处理和服务调度决定实际吞吐 [Efficient Diffusion Survey, 2024]。

## 10.3.5 5. 㢦⹂⿁㦏ᱶ╹㔶⒱ㄩ㨻☡⶙ⶨ㖺ⰻㄩㅨ㋹

扩散模型的未来不会只停在文生图。图像方向会继续追求组合理解、可控编辑和高效交互；视频方向会追求长时一致、物理合理和故事控制；3D方向会追求可编辑asset与多视角一致；具身方向会把 action generation 变成 VLA 的执行头；AI4Science 会把生成模型接入实验和模拟闭环。

最重要的趋势是：diffusion 正在从“生成样本”走向“生成可验证方案”。一个好的模型不仅要给结果，还要给置信度、证据、可控参数、失败诊断和后续筛选接口。

## 10.4 ⤴⮒⤇㖷⫊㢣■⿵

一套面向 diffusion 系统的评测 protocol：

```txt
Input:
    model M
    prompt suite P
    optional reference data R

Quality:
    compute FID/FVD where appropriate
    run human preference study

Alignment:
    run object, attribute, count, relation probes
    run text-image or text-video alignment 
```

## 10.5 关键架构图 / 方法图拆解

```txt
Robustness:
perturb prompt wording
test rare objects and compositional prompts
test long video temporal consistency 
```

Safety: run memorization and nearest-neighbor audit test privacy-sensitive prompts inspect watermark and provenance behavior 

```txt
Efficiency:
measure steps, latency, throughput, memory, energy
compare under equal hardware and equal resolution 
```

```txt
Report:
show aggregate score
show category score
show failure cases
disclose data and evaluation limits 
```

组合准确率可以按子能力拆分：

$$
\operatorname{Score} _ {\text { comp }} = \frac {1}{K} \sum_ {k = 1} ^ {K} \mathbf {1} [ \operatorname{judge} _ {k} (x, p) = 1 ].
$$

其中 $\mathrm { j u d g e } _ { k }$ 可以是检测器、VQA模型、规则判定或人工标注。关键是报告每个子项，避免平均分掩盖严重失败。

效率可以写成多目标约束：

$$
\max \text { Quality } (M) \quad \text { s.t. } \quad \text { Latency } \leq L, \text { Memory } \leq B, \text { Cost } \leq C.
$$

真实系统很少单纯追求最高质量，通常是在时延、显存、价格和安全约束下求最优。

## 10.5 ⤴⮒⭲⤕㟰 /➝➈㟰␚ⰶ

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/a528d53498ff43804f31cb4ea73e230b6dc033c0c32cfdeb30238a262c7610d0.jpg)



㟰 10.1: 图 10-1：Text-to-image 发展时间线，来源：Cao et al., 2023, survey figure。


这张时间线适合回看全书：从 GAN/VAE、自回归、CLIP 引导，到 latent diffusion、DiT和大规模T2I系统。技术路线一直在围绕质量、控制、效率和语义对齐迭代。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/c6b3a7cbdc34e2f5cc83552a3e4d85a270a4b1b9862722b5630b4eb5a6a718c1.jpg)



㟰 10.2: 图 10-2：T2I-CompBench 失败案例，来源：Huang et al., 2023, Fig. 1。


T2I-CompBench 的失败图说明：漂亮图片也可能不理解组合关系。颜色、数量、空间关系、属性绑定这些基础能力需要单独诊断。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/c71614b522eaafbd4bda0729226290fd9cacc6b9853e4c65f9707a1cb78704ab.jpg)



㟰 10.3: 图 10-3：GenEval overview，来源：Ghosh et al., 2023, Fig. 1。


GenEval 的图展示自动化组合评测流程。prompt 被结构化为可检查任务，生成图像经过检测器和规则判定，从而得到更细粒度的能力分数。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/53cda3ac9a14a69c2cd34e190d122daec94da0447671615dfcbafce2d5a5067d.jpg)



㟰 10.4: 图 10-4：训练数据提取中的 precision-recall 分析，来源：Carlini et al., 2023, Fig. 4。


这张图提醒我们，生成模型的安全问题可以被实验化测量。记忆和隐私风险不是抽象担忧，需要在训练和发布前进行系统审计。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/8ef56f1a5c25fd52cca44fb9086eb6fb308014f5510299c2eea42d02ae59094e.jpg)



㟰 10.5: 图 10-5：视频 diffusion 关键方面总览，来源：Melnik et al., 2024, Fig. 1。


视频survey的总览图把视频diffusion的任务、架构、训练、条件和评测放在一起。它说明视频生成已经是多因素系统工程。

![image](https://cdn-mineru.openxlab.org.cn/result/2026-09-29/57b2e205-3582-4d58-96e9-5d070dea6f54/906cc7deebae9038f7cd3313254b2dd9d46a8490df297a585dcc1bc0606aec94.jpg)



㟰 10.6: 图 10-6：高效 diffusion 方法组织框架，来源：Ma et al., 2024, Fig. 2。


高效diffusion的图适合作为路线图：模型压缩、采样加速、训练优化、条件控制、部署优化互相影响。高效化是一整套工程-算法协同。

## 10.6 ⡡➝㦢☨㟨♇

第一，指标与人类感知不完全一致。FID、FVD、CLIPScore、检测器分数都可能误判。指标应服务于诊断，不能替代人工分析和失败案例展示。

第二，评测集会被过拟合。公开 benchmark 一旦成为排行榜，模型可能针对测试分

布优化，真实复杂 prompt 仍然失败。

第三，安全审计成本高。训练数据去重、版权管理、隐私检测、输出过滤、滥用防护都需要系统工具。越大的多模态数据集，审计越困难。

第四，效率优化可能牺牲能力。少步采样可能降低细节，多级蒸馏可能损失多样性，量化可能影响文字和小物体，token压缩可能损伤视频时间一致。

第五，开放模型与闭源系统难比较。数据规模、过滤规则、训练 compute、promptrewrite、后处理、安全策略都不同，只比较最终样图不公平。

## 10.7 ⧥㨲 insight

这一章的核心 insight 是：diffusion 系统的能力需要分解评价。一个模型可能画质强但数量差，速度快但细节弱，视频连贯但动作不符合文本，科学结构多样但验证失败。好的研究结论必须说明在哪些维度变好，在哪些条件下失效。

第二个 insight 是安全和效率不是“上线前的附加项”，它们会反过来塑造算法。隐私风险推动去重和审计；版权风险推动数据治理；实时交互推动少步模型；端侧部署推动压缩和量化；视频长时生成推动3DVAE和并行训练。

第三个 insight 是未来 diffusion 的核心竞争会落在完整 pipeline 上：数据、表示、back-bone、条件接口、采样器、蒸馏、对齐、安全、评测和部署共同决定系统上限。

## 10.8 㖯㬕ⰵ⿥

T2I-CompBench和GenEval表明，主流T2I模型在复杂组合、属性绑定、计数和空间关系上仍有明显短板 [T2I-CompBench, 2023][GenEval, 2023]。Training Data Extraction 说明扩散模型存在训练样本记忆风险，重复数据和过拟合会提高提取成功率 [Training DataExtraction, 2023]。Video diffusion survey 总结了自动指标与人类感知不一致、时间一致性难评估等问题 [Video Diffusion Survey, 2024]。Efficient diffusion survey 则表明高效化已经从采样器扩展到训练、架构、微调和部署全流程 [Efficient Diffusion Survey, 2024]。

## 10.9 ⳨㦎㲓㢦⹂⤀㾗

当前评测仍然缺少统一可信标准。自动评测依赖检测器和VQA模型，这些模型自身会犯错；人工评测昂贵且难复现；安全评测常常无法覆盖所有滥用场景。未来需要更强的可控生成诊断集、更透明的数据报告、更细粒度的失败分类、更可信的水印与溯源、更严格的隐私审计和跨媒体统一benchmark。

技术路线方面，diffusion 会继续与 flow matching、autoregressive modeling、world mod-els、RL、agentic tool use 和科学模拟结合。MMDiT、3D VAE、consistency/LCM、动作 flowpolicy、AI4Science等方向已经显示出这种融合趋势。接下来最有价值的问题是：谁能在可控、安全、高效、可验证的约束下稳定生成有用结果。

## 10.10 ⛣㠞㸆㮥㷦㱎⡡㷪㣇㖬ぼ

1. FID、CLIPScore 等指标的用途和局限。

2. 为什么 T2I 需要组合能力评测。

3. 视频生成为什么必须评估时间一致和运动。

4. diffusion模型为什么可能记忆训练数据。

5. 高效化可以从采样、蒸馏、架构、训练和部署五层展开。

6. 为什么未来diffusion系统要同时关注质量、安全、效率和验证。

## 10.11 ⡒㥠㢼㝘

1. FID 高低为什么不能完全代表 prompt following 能力？

2. 颜色绑定和空间关系为什么需要单独评测？

3. 视频生成中单帧质量高但时间闪烁，应该用哪些指标和案例诊断？

4. 训练数据重复为什么会增加记忆风险？

5. 少步采样和蒸馏可能牺牲哪些能力？

6. 如果要发布一个开源文生图模型，训练前后应做哪些安全审计？

## ⡛⿆A 㐩㗣㺬⼋⮂␓㎥☉

• 每章都有要解决的问题、技术背景、核心方法、公式或伪代码、关键图、痛点、insight、实验结论和局限

• 重点论文至少在正文中被引用一次

• 所有图都使用绝对路径，并标明来源论文、年份和 figure/page 信息

• 正文以中文讲义方式综合展开，没有大段复制论文原文

• 区分论文结论、方法解释和综合判断

• 对图像、视频、3D、具身、AI4Science、评测安全和高效化都给出局限与未来工作

• 保留可继续扩展为TeX/PDF的章节结构