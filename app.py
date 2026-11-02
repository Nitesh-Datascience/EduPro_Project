import streamlit as st
import pandas as pd
import plotly.express as px
from pipeline import load_data, build_profiles, fit_segments, recommend

st.set_page_config(page_title='EduPro | Learner Intelligence',page_icon='◈',layout='wide',initial_sidebar_state='expanded')
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,.stApp {font-family:Inter,sans-serif;background:#070b16;color:#eaf1fb}
.stApp {
  background:
    radial-gradient(ellipse 55% 32% at 82% 0%,#203c70 0%,transparent 68%),
    radial-gradient(ellipse 42% 28% at 4% 35%,#123b45 0%,transparent 72%),
    linear-gradient(135deg,#070b16 0%,#0a1222 52%,#090d1b 100%);
  background-attachment:fixed;
}
.stApp:before {
  content:""; position:fixed; inset:0; pointer-events:none; z-index:0; opacity:.16;
  background-image:linear-gradient(#5debd00d 1px,transparent 1px),linear-gradient(90deg,#5debd00d 1px,transparent 1px);
  background-size:42px 42px;
}
.block-container {position:relative;z-index:1}
[data-testid="stHeader"] {background:#090e19b8;backdrop-filter:blur(12px)}
[data-testid="stSidebar"] {background:#0b1220;border-right:1px solid #22354c;min-width:260px!important;max-width:260px!important}
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {padding:2.8rem 1rem 1rem}
[data-testid="stAppViewContainer"] .block-container {max-width:1700px;padding:2.6rem 2.25rem 4rem}
h1,h2,h3 {color:#f2f8ff!important;letter-spacing:-.035em}
h3 {font-size:1.18rem!important;margin:1.2rem 0 .3rem!important}
.brand {padding:8px 10px 18px;border-bottom:1px solid #23364d;margin-bottom:18px}
.brand .icon {display:inline-grid;place-items:center;width:36px;height:36px;color:#0b1727;background:#45f0d1;border-radius:11px;margin-right:8px;box-shadow:0 0 24px #35e6bf55}
.brand b {font-size:20px;color:#f6fbff;letter-spacing:-.04em}.brand em {font-style:normal;color:#54e6d2}
.brand small {display:block;margin:12px 0 0 2px;color:#7491aa;letter-spacing:.12em;font-size:9px;font-weight:700}
.sidebar-foot {border:1px solid #255348;background:#102620;border-radius:11px;color:#72e6bd;padding:10px 12px;font-size:11px;font-weight:700;margin-top:28px}
[data-testid="stSidebar"] [role="radiogroup"] {gap:5px}
[data-testid="stSidebar"] [role="radiogroup"] label {border-radius:10px;padding:9px 10px;font-weight:600;color:#aabed0;transition:background .15s}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {background:#17283a;color:white}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {background:linear-gradient(90deg,#133f45,#163247);color:#70f6db;box-shadow:inset 3px 0 #37e7c1}
[data-testid="stSidebar"] [role="radiogroup"] [data-testid="stWidgetLabel"] {display:none}
[data-testid="stSidebar"] [role="radiogroup"] label [data-testid="stMarkdownContainer"] p {font-size:13px}
.hero {position:relative;overflow:hidden;padding:29px 32px;border:1px solid #345777;border-radius:20px;background:radial-gradient(circle at 82% 12%,#245c79 0%,transparent 32%),linear-gradient(110deg,#10283b,#171d3b 58%,#102c38);margin:0 0 24px;box-shadow:0 18px 55px #0006,inset 0 1px #ffffff12}
.hero:before {content:"";position:absolute;inset:0;opacity:.22;background:linear-gradient(115deg,transparent 15%,#5ef5dc18 48%,transparent 75%);transform:translateX(-100%);animation:heroSweep 8s ease-in-out infinite}
.hero:after {content:"";position:absolute;right:28px;top:-112px;width:255px;height:255px;border:1px solid #49eccc55;border-radius:50%;box-shadow:0 0 0 28px #49eccc0d,0 0 0 58px #49eccc0a,0 0 48px #49eccc22;animation:orbit 18s linear infinite}
@keyframes heroSweep {0%,35%{transform:translateX(-100%)}65%,100%{transform:translateX(100%)}}
@keyframes orbit {to{transform:rotate(360deg)}}
.hero small {color:#49edc9;letter-spacing:.16em;font-size:10px;font-weight:800}
.hero h1 {margin:7px 0 4px;font-size:34px}.hero p {color:#a9bfd2;margin:0;font-size:14px}
.card {position:relative;overflow:hidden;background:linear-gradient(145deg,#1a2b42dd,#101b2ddd);backdrop-filter:blur(14px);border:1px solid #38516c;border-top:3px solid var(--accent);border-radius:16px;padding:18px 19px;min-height:119px;box-shadow:0 14px 32px #0005,inset 0 1px #ffffff10;transition:transform .22s ease,border-color .22s ease}
.card:hover {transform:translateY(-4px);border-color:var(--accent);box-shadow:0 18px 42px #0007,0 0 22px color-mix(in srgb,var(--accent) 18%,transparent)}
.card:after {content:"";position:absolute;width:110px;height:110px;right:-48px;bottom:-58px;border-radius:50%;background:var(--accent);opacity:.08;filter:blur(4px)}
.card .label {color:#aebfd1;font-size:10px;letter-spacing:.09em;font-weight:800}
.card .value {font-size:27px;font-weight:800;color:var(--accent);margin:9px 0 2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.card .note{color:#7993a9;font-size:11px}
[data-testid="stPlotlyChart"] {border:1px solid #344d69;background:linear-gradient(145deg,#17263add,#101b2ddd);border-radius:17px;padding:7px;box-shadow:0 16px 38px #0004,inset 0 1px #ffffff0c;transition:border-color .2s,box-shadow .2s}
[data-testid="stPlotlyChart"]:hover {border-color:#4d8c9a;box-shadow:0 18px 42px #0006,0 0 24px #42e9d018}
.stButton button {background:#102b33;border:1px solid #23bca8;color:#d9fff5;border-radius:9px}
[data-testid="stDataFrame"] {border:1px solid #3a526e;border-radius:13px;overflow:hidden}
[data-testid="stMetric"] {background:linear-gradient(145deg,#182a40,#111c2d);border:1px solid #304963;border-radius:13px;padding:12px}
.stSelectbox [data-baseweb="select"],.stMultiSelect [data-baseweb="select"] {background:#14243a;border-radius:10px}
.stTabs [data-baseweb="tab-list"] {gap:8px}
.stTabs [data-baseweb="tab"] {background:#14243a;border:1px solid #2d455e;border-radius:9px;padding:8px 15px}
.stTabs [aria-selected="true"] {background:#16423f!important;color:#6ff5d8!important}
.stCaption {color:#88a5bd}
div[data-testid="stAlert"] {border-radius:12px;border:1px solid #36546a;background:#13263a}
@media(max-width:900px){[data-testid="stAppViewContainer"] .block-container {padding:2.2rem 1rem 3rem}.hero{padding:22px}.card{min-height:105px}}
</style>''',unsafe_allow_html=True)
@st.cache_data(show_spinner='Preparing learner intelligence…')
def data():
    users,courses,tx=load_data()
    profiles=build_profiles(users,courses,tx)
    active,metrics=fit_segments(profiles)
    return users,courses,tx,profiles,active,metrics
try: users,courses,tx,profiles,active,metrics=data()
except Exception as exc: st.error(f'Could not load project data: {exc}');st.stop()
with st.sidebar:
    st.markdown('<div class="brand"><span class="icon">✧</span><b>EduPro <em>AI</em></b><small>NEURAL LEARNING INTELLIGENCE</small></div>',unsafe_allow_html=True)
    page=st.radio('NAVIGATION',['Overview','Learner Explorer','Recommendations','Segment Comparison','Model Comparison','Model & Data'],label_visibility='collapsed')
    st.markdown(f'<div class="sidebar-foot">● DATA READY &nbsp; · &nbsp; {len(tx):,} enrollments</div>',unsafe_allow_html=True)
st.markdown(f'<div class="hero"><small>✧ EDUPRO / AI PERSONALIZATION ENGINE</small><h1>{page}</h1><p>Understand every learner. Discover patterns. Recommend a smarter next step.</p></div>',unsafe_allow_html=True)
st.markdown('<div style="display:flex;gap:9px;flex-wrap:wrap;margin:-7px 0 20px;color:#8eabc1;font-size:10px;letter-spacing:.08em"><span style="padding:6px 10px;border:1px solid #285b5b;border-radius:30px;background:#102b2a;color:#71f2d4">● AI ENGINE READY</span><span style="padding:6px 10px;border:1px solid #344c68;border-radius:30px;background:#111f32">◈ BEHAVIOR ANALYTICS</span><span style="padding:6px 10px;border:1px solid #344c68;border-radius:30px;background:#111f32">✧ 3D LEARNER SPACE</span></div>',unsafe_allow_html=True)
def cards(items):
    cols=st.columns(len(items))
    for col,(label,value,note,color) in zip(cols,items):
        col.markdown(f'<div class="card" style="--accent:{color}"><div class="label">{label}</div><div class="value">{value}</div><div class="note">{note}</div></div>',unsafe_allow_html=True)
def chart(fig):
    existing_height=fig.layout.height or 350
    existing_margin=fig.layout.margin
    margin=dict(l=existing_margin.l if existing_margin.l is not None else 48,
                r=existing_margin.r if existing_margin.r is not None else 24,
                t=existing_margin.t if existing_margin.t is not None else 55,
                b=existing_margin.b if existing_margin.b is not None else 48)
    fig.update_layout(paper_bgcolor='#141f30',plot_bgcolor='#141f30',font=dict(family='Inter, sans-serif',size=11,color='#b7c9dc'),
        margin=margin,legend_title_text='',height=existing_height,
        title_font=dict(size=15,color='#ecf5ff'),hoverlabel=dict(bgcolor='#20344a',font_color='white'))
    fig.update_xaxes(gridcolor='#273a50',zeroline=False,title_font_size=11,tickfont_size=10)
    fig.update_yaxes(gridcolor='#273a50',zeroline=False,title_font_size=11,tickfont_size=10)
    st.plotly_chart(fig,width='stretch',theme=None)
if page=='Overview':
