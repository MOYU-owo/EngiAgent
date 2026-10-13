// Rebuild the standalone reading edition from its Markdown source.
// Usage: node scripts/render_structureclaw_notes.mjs [node_modules directory]
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const project = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const resolver = createRequire(process.argv[2]
  ? path.join(path.resolve(process.argv[2]), '__renderer__.cjs')
  : import.meta.url);
const { marked } = await import(pathToFileURL(resolver.resolve('marked')).href);
const source = fs.readFileSync(path.join(project, 'docs/structureclaw_notes.md'), 'utf8');
let article = marked.parse(source, { gfm: true });
const escape = value => value.replaceAll('&', '&amp;').replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const plain = value => value.replace(/<[^>]*>/g, '');
article = article.replace('<h1>StructureClaw：从一句工程需求到可追溯的计算结果</h1>',
  '<h1>StructureClaw<span class="subtitle">从一句工程需求<br>到可追溯的计算结果</span></h1>');
article = article.replace(/<p>(<a id="[^"]+"><\/a>)<\/p>/g, '$1');
article = article.replace(/<h2>阅读导航<\/h2>[\s\S]*?(?=<a id="chapter-0")/, '');
article = article.replace(/<a id="([^"]+)"><\/a>\s*<h2>(.*?)<\/h2>/g,
  '<h2 id="$1">$2</h2>');
article = article.replace(/<h3>(.*?)<\/h3>/g, (_, title) => {
  const number = plain(title).match(/^(\d+)\.(\d+)/);
  return `<h3${number ? ` id="section-${number[1]}-${number[2]}"` : ''}>${title}</h3>`;
});
article = article.replace(/<table>/g, '<div class="table-scroll" role="region" aria-label="对照表，可横向滚动" tabindex="0"><table>')
  .replace(/<\/table>/g, '</table></div>');
article = article.replace(/<pre><code(?: class="language-([^"]+)")?>/g, (_, lang = 'text') =>
  `<figure class="code-block ${lang === 'text' ? 'diagram' : ''}"><figcaption>${lang === 'text' ? '流程 · 结构 · 轨迹' : escape(lang.toUpperCase())}</figcaption><pre tabindex="0"><code class="language-${escape(lang)}">`)
  .replace(/<\/code><\/pre>/g, '</code></pre></figure>');
const chapters = [...article.matchAll(/<h2 id="([^"]+)">(.*?)<\/h2>/g)];
const navigation = chapters.map(([, id, title]) => `<a href="#${id}">${title}</a>`).join('\n');
const html = `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<meta name="description" content="沿着一个钢框架请求，理解 StructureClaw 的知识、状态、工具、运行时与求解器如何协作。">
<title>StructureClaw · 从工程需求到计算结果</title>
<style>
:root{--paper:#fffefb;--bg:#f3f4f1;--ink:#243438;--muted:#647477;--line:#dce3df;--accent:#16645b;--soft:#edf5f1;--code:#f2f5f4}
*{box-sizing:border-box}html{scroll-behavior:auto;scroll-padding-top:32px}
body{margin:0;background:var(--bg);color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI","Microsoft YaHei","PingFang SC",sans-serif;font-size:17px;line-height:1.95}
a{color:var(--accent);text-decoration-thickness:1px;text-underline-offset:4px;overflow-wrap:anywhere}
a:hover{color:#083b34}a:focus-visible,summary:focus-visible,button:focus-visible,pre:focus-visible,.table-scroll:focus-visible{outline:3px solid #dfac53;outline-offset:4px}
.skip{position:fixed;top:-100px;left:20px;z-index:10;padding:8px;background:white}.skip:focus{top:12px}
.progress{position:fixed;left:0;top:0;height:3px;background:var(--accent);width:0;z-index:9}
aside{position:fixed;inset:0 auto 0 0;width:285px;padding:40px 25px 24px;overflow-y:auto;background:#edf0eb;border-right:1px solid var(--line)}
.brand{font-size:22px;font-weight:750;letter-spacing:-.6px;line-height:1.4}.brand small{display:block;font-size:11px;letter-spacing:2px;color:var(--accent);margin-bottom:7px}
.aside-note{font-size:13px;color:var(--muted);margin:12px 0 28px;line-height:1.8}summary{font-weight:650;font-size:13px;color:var(--muted);cursor:pointer;margin-bottom:12px}
nav a{display:block;padding:9px 11px;margin:4px 0;font-size:13px;line-height:1.65;text-decoration:none;border-left:2px solid transparent;border-radius:0 6px 6px 0}
nav a:hover{background:#e1e9e2}nav a[aria-current="location"]{background:#dce9e1;border-left-color:var(--accent);color:#124e46;font-weight:650}
.aside-footer{margin-top:24px;font-size:12px;color:var(--muted);border-top:1px solid var(--line);padding-top:16px;display:flex;gap:16px;align-items:center}
button{font:inherit;color:var(--accent);background:none;border:1px solid #becfc6;border-radius:5px;padding:5px 10px;cursor:pointer}button:hover{background:white}
main{margin-left:285px;padding:50px 40px 90px;min-width:0}.sheet{max-width:970px;margin:auto;background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:58px 66px 64px;box-shadow:0 8px 35px #223a2f06}
.eyebrow{font-size:11px;letter-spacing:2px;font-weight:700;color:var(--accent);margin-bottom:16px}
h1{font-size:36px;line-height:1.5;letter-spacing:-.7px;margin:0 0 25px;font-weight:750;text-wrap:balance}
.subtitle{display:block;font-size:.82em;line-height:1.65;margin-top:8px;letter-spacing:0}
h2{font-size:25px;line-height:1.6;margin:70px 0 28px;padding-top:32px;border-top:2px solid var(--line);text-wrap:balance}
h2::before{content:'CHAPTER';display:block;font-size:10px;letter-spacing:2px;color:var(--accent);font-weight:650;margin-bottom:8px}h2#sources::before{content:'REFERENCES'}
h3{font-size:20px;line-height:1.65;margin:38px 0 17px;color:#244c44}p{margin:0 0 20px;overflow-wrap:anywhere}strong{font-weight:700;color:#174c43}
blockquote{margin:24px 0;padding:19px 24px;background:var(--soft);border-left:3px solid #70a291;border-radius:0 7px 7px 0;font-size:16px}blockquote p{margin:0}
ul,ol{padding-left:1.4em;margin:16px 0 24px}li{margin:7px 0}
code{font-family:"Cascadia Mono",Consolas,"Microsoft YaHei",monospace;font-size:.87em;background:#edf1ec;padding:2px 5px;border-radius:4px;overflow-wrap:anywhere}
.code-block{margin:25px 0 29px;border:1px solid #dce5df;border-radius:8px;overflow:hidden;background:var(--code)}
figcaption{padding:7px 17px;background:#e7eeea;border-bottom:1px solid #dce5df;color:#4c6b60;font-size:10px;letter-spacing:1.3px;font-weight:650;line-height:1.8}
pre{margin:0;padding:21px 22px;overflow-x:auto;tab-size:4;line-height:1.85;font-size:14px;max-width:100%}pre code{background:none;padding:0;font-size:inherit;white-space:pre;overflow-wrap:normal;border-radius:0}
.diagram{background:#f7f8f4}.diagram figcaption{background:#eef1e8}
.table-scroll{overflow-x:auto;margin:25px 0 30px;border:1px solid var(--line);border-radius:8px}table{width:100%;border-collapse:collapse;font-size:14px;line-height:1.8}th{text-align:left;background:#eaf0eb;font-weight:650;color:#254b41}th,td{padding:12px 15px;vertical-align:top;border-bottom:1px solid var(--line);min-width:110px}tr:last-child td{border-bottom:0}tr:nth-child(even) td{background:#f8faf6}
footer{margin-top:45px;border-top:1px solid var(--line);padding-top:18px;color:var(--muted);font-size:12px}
@media(min-width:1500px){body{font-size:18px}.sheet{max-width:1030px;padding:65px 80px}}
@media(max-width:1050px){aside{width:240px;padding:30px 18px}main{margin-left:240px;padding:30px 24px}.sheet{padding:38px 32px}h1{font-size:30px}}
@media(max-width:760px){html{scroll-padding-top:18px}body{font-size:16px}aside{position:static;width:auto;padding:22px 20px 16px;border-right:0;border-bottom:1px solid var(--line)}.brand{font-size:22px}.brand small{font-size:10px}.aside-note{margin:8px 0 14px}nav{max-height:230px;overflow-y:auto}.aside-footer{margin-top:12px;padding-top:10px}main{margin:0;padding:18px 10px 35px}.sheet{padding:28px 20px;border-radius:8px}h1{font-size:27px}h2{font-size:23px;margin-top:48px;padding-top:26px}h3{font-size:19px;margin-top:30px}blockquote{padding:15px 17px}.code-block{margin-inline:-6px}pre{padding:16px 14px;font-size:12px}th,td{padding:10px 12px;font-size:13px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
@media print{html{scroll-behavior:auto}body{background:white;font-size:11pt;color:#111;line-height:1.7}aside,.progress,.skip,.eyebrow{display:none}main{margin:0;padding:0}.sheet{border:0;border-radius:0;padding:0;max-width:none;box-shadow:none}h1{font-size:25pt}h2{break-before:page;font-size:19pt;margin:0 0 20px;padding-top:0;border-top:0}h3{font-size:14pt;break-after:avoid}p{orphans:3;widows:3}pre{font-size:8pt;white-space:pre-wrap;overflow-wrap:anywhere}pre code{white-space:pre-wrap;overflow-wrap:anywhere}.code-block,table,blockquote{break-inside:avoid}.table-scroll{overflow:visible}a{color:inherit;text-decoration:none}footer{font-size:9pt}@page{size:A4;margin:18mm}}
</style>
</head>
<body>
<a class="skip" href="#reading">跳至正文</a><div class="progress" aria-hidden="true"></div>
<aside aria-label="阅读导航">
<div class="brand"><small>ENGINEERING AGENT NOTES</small>StructureClaw</div>
<p class="aside-note">沿着一次工程任务<br>读懂知识、决策与执行的协作</p>
<details open><summary>目录 · 第 0—7 章</summary><nav>${navigation}</nav></details>
<div class="aside-footer"><a href="structureclaw_notes.md" download>Markdown 源文</a><button type="button" id="print">打印 / PDF</button></div>
</aside>
<main id="reading"><article class="sheet"><div class="eyebrow">技术讲义 / 2026.10.13</div>${article}
<footer>本页由同目录 Markdown 自动生成 · 离线阅读无需外部字体或脚本 · 源码关系还原不等于实测记录</footer></article></main>
<script>
const headings = [...document.querySelectorAll('h2[id]')];
const links = [...document.querySelectorAll('nav a')];
const bar = document.querySelector('.progress');
function refresh() {
  const height = document.documentElement.scrollHeight - innerHeight;
  bar.style.width = (height > 0 ? scrollY / height * 100 : 0) + '%';
  let active = headings[0]?.id;
  for (const h of headings) { if (h.getBoundingClientRect().top < 150) active = h.id; }
  for (const link of links) {
    if (link.hash === '#' + active) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  }
}
document.getElementById('print').addEventListener('click', () => window.print());
let scheduled = false;
addEventListener('scroll', () => { if (!scheduled) { scheduled = true; requestAnimationFrame(() => { refresh(); scheduled = false; }); } }, {passive:true});
addEventListener('resize', refresh); refresh();
</script>
</body></html>`;
const output = path.join(project, 'docs/structureclaw_notes.html');
fs.writeFileSync(output, html, 'utf8');
console.log(`Rendered ${chapters.length} navigable sections to ${output}`);
