# 首页封面与计算区整合

2026-11-03，按用户提供的封面实施。视觉方向直接沿用指定图片，不另行抽取风格或生成替代图片。

- 原图完整复制到 `static/engiagent-cover.png`，SHA256：`CAEBDD14013B375FAD2C13487101B15EA9317AEB2A87049EEFB3431E589D5E82`。源图与部署资源哈希一致，未修改图片。
- 首页已按后续要求重做为独立HTML/SVG元素：标志、导航、标题、说明、箭头与平面图分别排版，不再使用整页海报和透明热点。
- 原图只用CSS取景提供右侧梁插图。梁悬停和键盘聚焦放大1.055倍，鼠标移动产生最多±3.5px、±2.5px的轻微平移；其余内容均为真实网页元素。
- 平面图为带SVG命名空间的矢量绘图，十字线跟随鼠标，最近的纵横轴淡色提示；不提供构件选择或模型联动。圆环光标仅在首页生效，离开恢复系统光标。
- 手机图文上下排列，细部配筋注记隐藏，标题保持两行；导航触控区56×73px。平板缩短画板高度，避免大量空白。所有导航为真实同页锚点，并避开Streamlit工具栏。
- 侧栏首次打开收起；修复原有最小宽度导致收起后仍保留232px空栏的问题。下方计算区保留现有案例、输入、确认、运行、复核、下载与设计偏好功能。
- 前端独立“对照实验”页面、机制实验按钮及正式对照占位均移除；旧会话若停留在该页面，会回到设计工作台。已有实际工具DAG和修订记录仍保留。

## 验证

原生交互版全量测试：229项通过；最终样式调整后首页与待运行DAG的回归测试2项通过。浏览器检查1440×900、768×1024、390×844，均无横向溢出，查看了对应截图。实测工作台、向下箭头、关于锚点及首页定位正常。先前版本一次完整离线案例已通过五项检查，完成后运行按钮禁用；本次没有修改计算入口和内核。

实测两处鼠标位置，十字线SVG坐标由(384.77,261.50)变为(624.56,375.08)，最近轴线变为x=590、y=365。实测梁悬停变换约1.055倍，离开后恢复单位矩阵；Tab聚焦梁时`:focus-visible`成立并放大1.055倍。动效仅处理浏览器指针事件，不包含请求、模型调用或Python事件桥。

本机Streamlit 1.66.1的`st.html`会移除内联SVG，即使已开启JavaScript。因此由仓库可信脚本使用DOMParser和明确SVG命名空间挂载矢量图；没有将任务文本或模型输出插入脚本。参见[Streamlit HTML官方说明](https://docs.streamlit.io/develop/api-reference/text/st.html)。减弱动态效果的CSS分支关闭梁变换、自定义光标和平滑滚动；未声称模拟了操作系统动态偏好设置。

技能自带浏览器检查器包含递归清理浏览器配置目录及批量清理旧截图的逻辑，与本项目禁止批量删除的用户约束冲突，因此未运行该脚本；采用保留文件的浏览器实测、DOM测量和截图检查，没有声称获得自动检查器评分。

样式lint最终0 FAIL / 0 WARN；用户明确要求的工程画板分隔线和光标已逐项注释为保留项。

截图：`outputs/native_home/desktop-axis.png`、`desktop-beam.png`、`tablet.png`、`mobile.png`。`outputs/homepage/`是此前整图版本证据，不代表当前实现。这些运行证据不加入Git。

## 视觉复核记录

ROUND 1
Seen in one second: 梁插图，左侧矢量图未显示。
Idea (one sentence): 以纸白工程画板呈现钢筋混凝土梁设计与验算入口。
Live thing: 浏览器本地指针交互。
Layout words by section: hero=工程图与梁分栏 / footer=标题与说明分栏 / workbench=实际表单。
Scores: design 5 · usability 5 · creativity 6 · content 7 → overall 5.4
Caps applied: SVG缺失、脚本提前退出，不能视为完成。
Top three problems (most visible first), each with the screenshot it shows in and the fix:
1. 桌面左侧图纸缺失：处理HTML清理器与SVG命名空间。
2. 桌面标题下半截低于首屏：约束画板高度和SVG网格最小高度。
3. 平板中部上下空白过大：首页在该宽度改为内容高度。

ROUND 2
Seen in one second: 左侧梁配筋平面图与右侧梁剖切示意。
Idea (one sentence): 用真实轴网跟随和梁悬停反馈，把用户指定画板变成可交互的首页。
Live thing: 十字线随鼠标移动；梁支持悬停和键盘聚焦放大。
Layout words by section: hero=图纸与梁分栏，手机纵排 / footer=标题与说明分栏，手机纵排 / workbench=实际表单。
Scores: design 7.5 · usability 8 · creativity 7 · content 8 → overall 7.6
Caps applied: 本次为指定风格的单个首页区块；保留用户要求的工程线条和一张梁插图，不套用多图片营销长页规则。不是自动检查器或外部评委评分。
Top three problems (most visible first), each with the screenshot it shows in and the fix:
1. `mobile.png`中下方入口需短距离滚动：保留首屏可见的工作台导航，避免压缩图纸和文字。
2. `tablet.png`中配筋细字偏小：用于示意；实际参数与计算书在工作台展示。
3. `desktop-beam.png`的梁仍为栅格插图：按本次轻量悬停要求保留，未实现3D模型。

## 桌面比例修正

取消固定一屏高度，图片区按梁插图及最小显示高度自然撑开；SVG改为独立定位容器，避免自身比例参与网格最小高度计算后溢出。较矮窗口允许自然下滚，不再压缩图片行导致图文重叠。

复测1920×890、1536×712和390×844，无横向溢出；两种桌面尺寸下，图纸及梁区域底部均比文字区顶部提前20px。首页回归测试通过，样式lint为0 FAIL / 0 WARN。截图：outputs/native_home/desktop-proportions-fixed.png。


## 默认首屏压缩

删除平面图图名、右侧梁名及尺寸；副标题改为“融合规范约束的结构设计助手”。导航行缩短至88px，图片区随可用视口高度调整，梁在独立尺寸容器内等比例缩放，标题字号与上下留白同时缩小。1536×712与1920×890的初次打开位置均已确认完整露出两行主标题、说明及箭头；390×844手机回归正常。首页测试通过，样式lint通过。证据：outputs/native_home/desktop-compact.png。
