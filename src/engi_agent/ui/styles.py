"""Presentation tokens for the CN engineering workbench."""

CSS = '''
<style>
:root {
  --ea-ink: #303436;
  --ea-muted: #666963;
  --ea-primary: #303436;
  --ea-border: #d9d7d0;
  --ea-surface: #fcfbf8;
  --ea-soft: #eeece6;
  --ea-ground: #f7f5f0;
  --ea-selected: #e5e3dd;
  --ea-accent: #496779;
  --ea-control: #b9bcb7;
  --ea-info-bg: #eaf0f2;
  --ea-info-ink: #3f5c6d;
  --ea-info-border: #becdd3;
  --ea-warn-bg: #f5efe2;
  --ea-warn-ink: #785d2b;
  --ea-warn-border: #d9caab;
  --ea-fail-bg: #f6ecea;
  --ea-fail-ink: #914c48;
  --ea-fail-border: #d9bdb7;
  --ea-pass-bg: #edf2eb;
  --ea-pass-ink: #386143;
  --ea-pass-border: #bfcebc;
}
.stApp {font-family: "Segoe UI", "Microsoft YaHei", sans-serif; color:var(--ea-ink);}
.block-container {max-width:1640px; padding:2.1rem 2rem 3rem;}
[data-testid="stHeader"] {background:transparent;}
[data-testid="stSidebar"] {min-width:232px; max-width:232px; border-right:1px solid var(--ea-border);}
[data-testid="stSidebarUserContent"] {padding:1.5rem 1.1rem;}
[data-testid="stSidebar"] [role="radiogroup"] {gap:6px;}
[data-testid="stSidebar"] [role="radiogroup"] label {padding:7px 9px; border-radius:6px;}
[data-testid="stSidebar"] label:has(input:checked) {background:var(--ea-selected); color:var(--ea-ink); font-weight:600;}
h1 {font-size:1.8rem!important; font-weight:700!important; letter-spacing:-.02em;}
h2 {font-size:1.25rem!important; font-weight:650!important;}
h3 {font-size:1.08rem!important; font-weight:650!important;}
h4 {font-size:1rem!important;}
[data-testid="stCaptionContainer"] {color:var(--ea-muted); font-size:.85rem; line-height:1.65;}
[data-testid="stCaptionContainer"] p {color:var(--ea-muted)!important;}
[data-testid="stMetricLabel"] {font-size:.85rem; color:var(--ea-muted);}
[data-testid="stMetricValue"] {font-size:1.4rem; font-variant-numeric:tabular-nums;}
[data-testid="stMetricValue"], [data-testid="stMetricValue"] > div {
  white-space:normal!important; overflow:visible!important; text-overflow:clip!important; overflow-wrap:anywhere;
}
[data-testid="stVerticalBlockBorderWrapper"] {border-color:var(--ea-border)!important; border-radius:10px!important;}
div[class*="st-key-card_"] {background:var(--ea-surface); border-radius:10px;}
[data-testid="stExpander"] {background:var(--ea-surface); border-radius:8px;}
[data-testid="stDataFrame"] {font-variant-numeric:tabular-nums;}
button, input, textarea {font-family:inherit!important;}
button {min-height:40px; transition:background-color .15s, border-color .15s;}
button:not(:disabled), [role="tab"], summary {cursor:pointer;}
button[kind="primary"] {font-weight:650;}
button[kind="secondary"], button[kind="secondaryFormSubmit"] {background:var(--ea-surface); border-color:var(--ea-control); color:var(--ea-ink);}
button[kind="secondary"]:hover:not(:disabled), button[kind="secondaryFormSubmit"]:hover:not(:disabled) {background:var(--ea-soft); border-color:var(--ea-accent); color:var(--ea-ink);}
button:disabled {background:var(--ea-soft)!important; border-color:var(--ea-border)!important; color:var(--ea-muted)!important;}
[class*="st-key-expert_suggestion_"] button {
  min-height:68px; height:auto; justify-content:flex-start; text-align:left;
}
[class*="st-key-expert_suggestion_"] button [data-testid="stMarkdownContainer"],
[class*="st-key-expert_suggestion_"] button p {
  white-space:normal!important; overflow:visible!important; text-overflow:clip!important;
  -webkit-line-clamp:unset!important; overflow-wrap:anywhere; line-height:1.5;
}
button:focus-visible, input:focus-visible, textarea:focus-visible,
[role="tab"]:focus-visible, summary:focus-visible, a:focus-visible {
  outline:3px solid var(--ea-accent)!important; outline-offset:3px;
}
.brand {font-size:25px; font-weight:750; color:var(--ea-primary); letter-spacing:-.04em;}
.brand-dot {color:var(--ea-muted);}
.eyebrow {font-size:12px; color:var(--ea-muted); font-weight:600; letter-spacing:.06em;}
.meta {color:var(--ea-muted); font-size:13px; line-height:1.7; overflow-wrap:anywhere;}
.task-status {text-align:right;}
.pill {display:inline-block; padding:5px 10px; border:1px solid var(--ea-info-border); border-radius:6px; background:var(--ea-info-bg); color:var(--ea-info-ink); font-size:13px; font-weight:600;}
.pill.warn {background:var(--ea-warn-bg); border-color:var(--ea-warn-border); color:var(--ea-warn-ink);}
.pill.fail {background:var(--ea-fail-bg); border-color:var(--ea-fail-border); color:var(--ea-fail-ink);}
.pill.pass {background:var(--ea-pass-bg); border-color:var(--ea-pass-border); color:var(--ea-pass-ink);}
.section-title {font-size:13px; color:var(--ea-muted); font-weight:600; margin:0 0 12px;}
.workflow-steps {display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; list-style:none; padding:0; margin:10px 0 22px;}
.workflow-steps li {padding:10px 12px; border:1px solid var(--ea-border); border-radius:7px; color:var(--ea-muted); font-size:13px; background:var(--ea-surface);}
.workflow-steps li[aria-current="step"] {border-color:var(--ea-control); background:var(--ea-selected); color:var(--ea-ink); font-weight:650;}
.workflow-steps .done {color:var(--ea-pass-ink);}
.result-grid {display:grid; grid-template-columns:repeat(auto-fit,minmax(125px,1fr)); gap:10px; margin:0 0 16px;}
.result-tile {border:1px solid var(--ea-border); border-radius:8px; padding:12px; background:var(--ea-surface);}
.result-tile strong {display:block; font-size:14px; margin-bottom:8px;}
.result-tile .pill {margin-bottom:8px;}
.result-tile p {font-size:13px; color:var(--ea-muted); line-height:1.65; margin:0; font-variant-numeric:tabular-nums;}
.empty-state {padding:28px 8px;}
.empty-state p {color:var(--ea-muted); line-height:1.8;}
@media (max-width:1100px) {
  [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] .st-key-card_parameters),
  [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] .st-key-card_start) {flex-direction:column;}
  [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] .st-key-card_parameters) > [data-testid="stColumn"],
  [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] .st-key-card_start) > [data-testid="stColumn"] {width:100%!important; flex:1 1 100%!important;}
}
@media (max-width:768px) {
  .block-container {padding:4rem 1rem 2rem;}
  h1 {font-size:1.5rem!important;}
  .workflow-steps {grid-template-columns:repeat(2,minmax(0,1fr));}
  [data-testid="stHorizontalBlock"] {flex-wrap:wrap;}
  [data-testid="stColumn"] {min-width:0!important; flex:1 1 100%!important; width:100%!important;}
  .task-status {text-align:left;}
  .result-grid {grid-template-columns:repeat(2,minmax(0,1fr));}
  button {min-height:44px;}
}
@media (prefers-reduced-motion:reduce) {
  *, *::before, *::after {scroll-behavior:auto!important; transition:none!important; animation:none!important;}
}
</style>
'''
