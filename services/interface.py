"""Shared presentation for RackMind's operations workspace."""
from html import escape
import streamlit as st


def apply_design():
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    :root {--rm-lime:#d4f77d;--rm-text:#e8ede4;--rm-muted:#a4b2a6;--rm-border:#344239;}
    .stApp {background:#101813;color:var(--rm-text);font-family:'DM Sans',sans-serif;}
    [data-testid="stHeader"] {background:transparent;}
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {display:none;}
    [data-testid="stMainBlockContainer"] {max-width:1510px;padding:2.4rem 3.2rem 4rem;}
    h1,h2,h3,[data-testid="stMetricValue"] {font-family:'Space Grotesk',sans-serif!important;letter-spacing:-.035em;}
    h2 {font-size:1.7rem!important;} h3 {font-size:1.12rem!important;}
    [data-testid="stCaptionContainer"] {color:var(--rm-muted);}
    [data-baseweb="tab-list"] {gap:1.6rem;border-bottom:1px solid var(--rm-border);}
    button[data-baseweb="tab"] {font-family:'Space Grotesk',sans-serif;font-size:.92rem;padding:12px 0;}
    button[data-baseweb="tab"][aria-selected="true"] {color:var(--rm-lime)!important;}
    [data-baseweb="tab-highlight"] {background:var(--rm-lime);height:3px;}
    [data-testid="stMetric"] {background:#1b281f;border:1px solid var(--rm-border);border-radius:4px;padding:20px 22px;min-height:124px;}
    [data-testid="stMetricLabel"] {color:var(--rm-muted);text-transform:uppercase;font-size:.72rem;letter-spacing:.09em;}
    [data-testid="stMetricValue"] {color:#eaf2df;font-size:2.15rem;}
    [data-testid="stFileUploader"] {border:1px dashed #566951;border-radius:5px;padding:8px 16px;background:#19241c;}
    [data-testid="stAlert"] {border-radius:4px;border-left:3px solid #b7cfa1;}
    [data-baseweb="select"] > div {background:#1b281f;border-color:#405244;}
    [data-baseweb="tag"] {background:#d4f77d!important;color:#152014!important;}
    [data-testid="stDownloadButton"] button {background:#d4f77d;color:#122014;border:0;font-weight:700;border-radius:4px;}
    .rm-brand {display:flex;align-items:center;justify-content:space-between;padding-bottom:24px;border-bottom:1px solid #344239;margin-bottom:14px;gap:20px;}
    .rm-logo {display:flex;align-items:center;gap:13px;font-family:'Space Grotesk',sans-serif;font-size:26px;font-weight:700;letter-spacing:-1px;}
    .rm-mark {display:grid;gap:4px;padding:9px;background:#d4f77d;border-radius:3px;}
    .rm-mark i {display:block;width:21px;height:4px;background:#17231a;}
    .rm-brand small {font:11px monospace;letter-spacing:2px;color:#a4b2a6;}
    .rm-mode {border:1px solid #566951;padding:8px 12px;color:#d4f77d;font:11px monospace;letter-spacing:1.4px;white-space:nowrap;}
    .rm-hero {display:flex;justify-content:space-between;align-items:end;gap:30px;margin:22px 0 24px;}
    .rm-eyebrow {color:#b5ca9f;font:11px monospace;letter-spacing:2px;text-transform:uppercase;}
    .rm-hero h1 {font:500 clamp(32px,4vw,56px)/1.08 'Space Grotesk',sans-serif;margin:12px 0;color:#e8ede4;letter-spacing:-2px;}
    .rm-hero p {color:#a4b2a6;margin:0;font-size:14px;max-width:470px;}
    .rm-hero-aside {border-left:1px solid #536149;padding-left:24px;font:12px/1.9 monospace;color:#a4b2a6;min-width:195px;}
    .rm-hero-aside strong {color:#d4f77d;font-weight:400;}
    .rm-section {display:flex;justify-content:space-between;align-items:center;margin:24px 0 14px;}
    .rm-section h3 {margin:0!important;padding:0!important;}
    .rm-section span {color:#a4b2a6;font:11px monospace;letter-spacing:1px;}
    .rm-racks {display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin-bottom:16px;}
    .rm-rack {background:#19241c;border:1px solid #344239;border-top:3px solid var(--accent);border-radius:4px;padding:20px;}
    .rm-rack-head {display:flex;justify-content:space-between;align-items:center;gap:8px;font:600 17px 'Space Grotesk',sans-serif;}
    .rm-badge {font:10px monospace;text-transform:uppercase;letter-spacing:1px;color:var(--accent);padding:5px 7px;border:1px solid var(--accent);border-radius:2px;}
    .rm-rack-body {display:flex;align-items:center;gap:22px;margin:20px 0;}
    .rm-chassis {width:50px;padding:6px;border:1px solid #4c5c4d;border-radius:3px;flex-shrink:0;}
    .rm-slot {height:9px;border:1px solid #435343;margin:3px 0;position:relative;}
    .rm-slot:after {content:'';position:absolute;right:3px;top:2px;width:3px;height:3px;background:var(--accent);}
    .rm-reading {font:500 32px 'Space Grotesk',sans-serif;letter-spacing:-1px;color:#ecf1e7;}
    .rm-unit {font:11px monospace;color:#a4b2a6;letter-spacing:0;display:block;margin-top:4px;}
    .rm-rack-foot {display:flex;justify-content:space-between;gap:10px;border-top:1px solid #344239;padding-top:12px;color:#acbaad;font:11px monospace;}
    .rm-note {color:#a4b2a6;font-size:12px;margin:4px 0 18px;}
    @media(max-width:700px) {[data-testid="stMainBlockContainer"] {padding:1.5rem 1rem;} .rm-hero {display:block;} .rm-hero-aside {display:none;} .rm-brand small {display:none;} .rm-racks {grid-template-columns:1fr;} [data-baseweb="tab-list"] {gap:18px;} }
    </style>""", unsafe_allow_html=True)


def brand_header():
    st.markdown('''<div class="rm-brand"><div class="rm-logo"><span class="rm-mark" aria-hidden="true"><i></i><i></i><i></i></span>rackmind<span style="color:#d4f77d;font-weight:400">/</span><small>DATA CENTER INTELLIGENCE</small></div><span class="rm-mode">SNAPSHOT WORKSPACE</span></div>''', unsafe_allow_html=True)


def overview_header():
    st.markdown('''<div class="rm-hero"><div><div class="rm-eyebrow">01 / OPERATIONS OVERVIEW</div><h1>Every rack.<br>One clear picture.</h1><p>Review facility telemetry, isolate exceptions, and turn readings into the next action.</p></div><div class="rm-hero-aside"><strong>OBSERVE / ASSESS / RESPOND</strong><br>Temperature &amp; rack power<br>Local telemetry assessment<br>Snapshot data, not live monitoring</div></div>''', unsafe_allow_html=True)


def rack_overview(racks):
    colors={"Critical":"#ff9c7c","Warning":"#f0cc79","Incomplete":"#b4b9cf","Normal":"#d4f77d"}
    cards=[]
    for rack in racks:
        status=rack['Status']
        temp=rack['Peak temperature (°F)']
        power=rack['Peak power (kW)']
        temperature='N/A' if temp is None else f'{temp:.1f}°'
        power_text='N/A' if power is None else f'{power:.2f} kW'
        cards.append(f'''<div class="rm-rack" style="--accent:{colors.get(status,'#b4b9cf')}"><div class="rm-rack-head">{escape(str(rack['Rack']))}<span class="rm-badge">{escape(status)}</span></div><div class="rm-rack-body"><div class="rm-chassis" aria-hidden="true">{'<div class="rm-slot"></div>'*6}</div><div class="rm-reading">{temperature}<span class="rm-unit">PEAK TEMPERATURE / °F</span></div></div><div class="rm-rack-foot"><span>{power_text} peak</span><span>{rack['Samples']} samples</span></div><div class="rm-unit">{rack['Missing / invalid readings']} missing / invalid readings</div></div>''')
    st.markdown('<div class="rm-section"><h3>Rack landscape</h3><span>SELECTED FILE WINDOW</span></div><div class="rm-racks">'+''.join(cards)+'</div>',unsafe_allow_html=True)
