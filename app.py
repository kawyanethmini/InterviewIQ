import streamlit as st
from groq import Groq
import speech_recognition as sr
import re, os, base64, time, json, hashlib
from gtts import gTTS
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import streamlit.components.v1 as components


# PERSISTENT USER DATABASE

USERS_FILE = Path(__file__).parent / "users.json"

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_users() -> dict:
    if USERS_FILE.exists():
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    default = {"admin": _hash("1234")}
    save_users(default)
    return default

def save_users(db: dict) -> None:
    with open(USERS_FILE, "w") as f:
        json.dump(db, f, indent=2)

def register_user(username: str, password: str) -> tuple[bool, str]:
    db = load_users()
    if username in db:
        return False, "Username already taken."
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    db[username] = _hash(password)
    save_users(db)
    return True, "Account created successfully."

def verify_user(username: str, password: str) -> bool:
    db = load_users()
    return db.get(username) == _hash(password)


# CONFIG

st.set_page_config(
    page_title="InterviewIQ",
    layout="wide",
    page_icon="🎯",
    initial_sidebar_state="expanded",
)

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = ""
client = Groq(api_key=GROQ_API_KEY)


# ANIMATED LOGO SVG

ANIMATED_LOGO_SVG_CODE = """
<svg width="64" height="64" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .lg { animation: floatY 3.5s ease-in-out infinite; }
      @keyframes floatY { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-4px)} }
      .mbg { fill:rgba(201,168,76,.10); stroke:rgba(201,168,76,.4); stroke-width:1.5;
             animation:pr 2.8s ease-in-out infinite; }
      @keyframes pr { 0%,100%{stroke-opacity:.4} 50%{stroke-opacity:.85} }
      .oring { fill:none; stroke:rgba(201,168,76,.2); stroke-width:1; stroke-dasharray:3 5; }
      .odot  { fill:#c9a84c; animation:os 4s linear infinite; transform-origin:60px 60px; }
      @keyframes os {
        from{transform:rotate(0deg) translateX(46px) rotate(0deg)}
        to  {transform:rotate(360deg) translateX(46px) rotate(-360deg)}
      }
      .mp { fill:none; stroke:#c9a84c; stroke-width:2.5; stroke-linecap:round;
            stroke-dasharray:120; stroke-dashoffset:120;
            animation:dp 1.4s ease forwards .2s; }
      @keyframes dp { to{stroke-dashoffset:0} }
      .ml  { fill:none; stroke:#c9a84c; stroke-width:2; stroke-linecap:round;
             stroke-dasharray:30; stroke-dashoffset:30;
             animation:dp 0.8s ease forwards .9s; }
      .md  { fill:#c9a84c; opacity:0; animation:pi .4s ease forwards 1.5s; }
      .md2 { fill:rgba(201,168,76,.55); opacity:0; animation:pi .4s ease forwards 1.7s; }
      @keyframes pi {
        0%  {opacity:0;transform:scale(0);transform-box:fill-box;transform-origin:center}
        70% {transform:scale(1.4);transform-box:fill-box;transform-origin:center;opacity:1}
        100%{transform:scale(1);transform-box:fill-box;transform-origin:center;opacity:1}
      }
      .b1{animation:wv 1.2s ease-in-out infinite 0s;  transform-origin:bottom;transform-box:fill-box}
      .b2{animation:wv 1.2s ease-in-out infinite .15s;transform-origin:bottom;transform-box:fill-box}
      .b3{animation:wv 1.2s ease-in-out infinite .3s; transform-origin:bottom;transform-box:fill-box}
      .b4{animation:wv 1.2s ease-in-out infinite .45s;transform-origin:bottom;transform-box:fill-box}
      .b5{animation:wv 1.2s ease-in-out infinite .6s; transform-origin:bottom;transform-box:fill-box}
      @keyframes wv { 0%,100%{transform:scaleY(.4)} 50%{transform:scaleY(1)} }
    </style>
  </defs>
  <rect width="120" height="120" fill="#080c14" rx="22"/>
  <g class="lg">
    <g transform="translate(60,58)">
      <rect class="mbg" x="-30" y="-30" width="60" height="60" rx="13"/>
      <circle class="oring" cx="0" cy="0" r="46"/>
      <circle class="odot" cx="46" cy="0" r="4"/>
      <path class="mp" d="M-14 14 L0 -16 L14 14"/>
      <line class="ml" x1="-7" y1="5" x2="7" y2="5"/>
      <circle class="md"  cx="0"   cy="-16" r="3.5"/>
      <circle class="md2" cx="-14" cy="14"  r="2.5"/>
      <circle class="md2" cx="14"  cy="14"  r="2.5"/>
    </g>
    <g transform="translate(20, 88)" opacity=".85">
      <rect x="0"  y="8"  width="5" height="10" rx="1.5" fill="#c9a84c" class="b1"/>
      <rect x="7"  y="4"  width="5" height="14" rx="1.5" fill="#c9a84c" class="b2"/>
      <rect x="14" y="0"  width="5" height="18" rx="1.5" fill="#c9a84c" class="b3"/>
      <rect x="21" y="4"  width="5" height="14" rx="1.5" fill="#c9a84c" class="b4"/>
      <rect x="28" y="8"  width="5" height="10" rx="1.5" fill="#c9a84c" class="b5"/>
    </g>
  </g>
</svg>
"""

ANIMATED_LOGO_LARGE_CODE = """
<svg width="96" height="96" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .lg2 { animation: floatY2 3.5s ease-in-out infinite; }
      @keyframes floatY2 { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-5px)} }
      .mbg2 { fill:rgba(201,168,76,.10); stroke:rgba(201,168,76,.4); stroke-width:1.5;
              animation:pr2 2.8s ease-in-out infinite; }
      @keyframes pr2 { 0%,100%{stroke-opacity:.4} 50%{stroke-opacity:.85} }
      .oring2 { fill:none; stroke:rgba(201,168,76,.2); stroke-width:1; stroke-dasharray:3 5; }
      .odot2  { fill:#c9a84c; animation:os2 4s linear infinite; transform-origin:60px 60px; }
      @keyframes os2 {
        from{transform:rotate(0deg) translateX(46px) rotate(0deg)}
        to  {transform:rotate(360deg) translateX(46px) rotate(-360deg)}
      }
      .mp2 { fill:none; stroke:#c9a84c; stroke-width:2.5; stroke-linecap:round;
             stroke-dasharray:120; stroke-dashoffset:120;
             animation:dp2 1.4s ease forwards .2s; }
      @keyframes dp2 { to{stroke-dashoffset:0} }
      .ml2  { fill:none; stroke:#c9a84c; stroke-width:2; stroke-linecap:round;
              stroke-dasharray:30; stroke-dashoffset:30;
              animation:dp2 0.8s ease forwards .9s; }
      .md3  { fill:#c9a84c; opacity:0; animation:pi2 .4s ease forwards 1.5s; }
      .md4  { fill:rgba(201,168,76,.55); opacity:0; animation:pi2 .4s ease forwards 1.7s; }
      @keyframes pi2 {
        0%  {opacity:0;transform:scale(0);transform-box:fill-box;transform-origin:center}
        70% {transform:scale(1.4);transform-box:fill-box;transform-origin:center;opacity:1}
        100%{transform:scale(1);transform-box:fill-box;transform-origin:center;opacity:1}
      }
      .c1{animation:wv2 1.2s ease-in-out infinite 0s;  transform-origin:bottom;transform-box:fill-box}
      .c2{animation:wv2 1.2s ease-in-out infinite .15s;transform-origin:bottom;transform-box:fill-box}
      .c3{animation:wv2 1.2s ease-in-out infinite .3s; transform-origin:bottom;transform-box:fill-box}
      .c4{animation:wv2 1.2s ease-in-out infinite .45s;transform-origin:bottom;transform-box:fill-box}
      .c5{animation:wv2 1.2s ease-in-out infinite .6s; transform-origin:bottom;transform-box:fill-box}
      @keyframes wv2 { 0%,100%{transform:scaleY(.4)} 50%{transform:scaleY(1)} }
    </style>
  </defs>
  <rect width="120" height="120" fill="#080c14" rx="22"/>
  <g class="lg2">
    <g transform="translate(60,58)">
      <rect class="mbg2" x="-30" y="-30" width="60" height="60" rx="13"/>
      <circle class="oring2" cx="0" cy="0" r="46"/>
      <circle class="odot2" cx="46" cy="0" r="4"/>
      <path class="mp2" d="M-14 14 L0 -16 L14 14"/>
      <line class="ml2" x1="-7" y1="5" x2="7" y2="5"/>
      <circle class="md3"  cx="0"   cy="-16" r="3.5"/>
      <circle class="md4"  cx="-14" cy="14"  r="2.5"/>
      <circle class="md4"  cx="14"  cy="14"  r="2.5"/>
    </g>
    <g transform="translate(20, 88)" opacity=".85">
      <rect x="0"  y="8"  width="5" height="10" rx="1.5" fill="#c9a84c" class="c1"/>
      <rect x="7"  y="4"  width="5" height="14" rx="1.5" fill="#c9a84c" class="c2"/>
      <rect x="14" y="0"  width="5" height="18" rx="1.5" fill="#c9a84c" class="c3"/>
      <rect x="21" y="4"  width="5" height="14" rx="1.5" fill="#c9a84c" class="c4"/>
      <rect x="28" y="8"  width="5" height="10" rx="1.5" fill="#c9a84c" class="c5"/>
    </g>
  </g>
</svg>
"""

def render_logo_large():
    components.html(f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
      body {{
        margin: 0; padding: 0;
        background: transparent;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-family: 'DM Sans', 'Segoe UI', sans-serif;
      }}
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;600&family=Playfair+Display:wght@700&display=swap');
      .logo-wrap {{
        filter: drop-shadow(0 0 24px rgba(201,168,76,.35));
        margin-bottom: 14px;
      }}
      .wordmark {{
        font-size: 2.2rem;
        color: #c9a84c;
        font-family: 'Playfair Display', serif;
        letter-spacing: -.02em;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        margin-bottom: 6px;
      }}
      .wordmark .light {{
        font-weight: 300;
        font-family: 'DM Sans', sans-serif;
        color: #eaf0fb;
      }}
      .tagline {{
        color: #4a5a72;
        font-size: .78rem;
        letter-spacing: .08em;
        text-transform: uppercase;
        font-family: 'DM Sans', sans-serif;
        text-align: center;
      }}
      @media (max-width: 480px) {{
        .wordmark {{ font-size: 1.7rem; }}
        .tagline {{ font-size: .68rem; }}
      }}
    </style>
    </head>
    <body>
      <div class="logo-wrap">
        {ANIMATED_LOGO_LARGE_CODE}
      </div>
      <div class="wordmark">
        <span class="light">Interview</span>IQ
      </div>
      <div class="tagline">AI-powered interview coaching platform</div>
    </body>
    </html>
    """, height=200, scrolling=False)


def render_logo_sidebar():
    components.html(f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
      body {{
        margin: 0; padding: 0;
        background: transparent;
        display: flex;
        align-items: center;
        gap: 10px;
        font-family: 'DM Sans', 'Segoe UI', sans-serif;
      }}
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;600&family=Playfair+Display:wght@700&display=swap');
      .logo-wrap {{
        filter: drop-shadow(0 0 10px rgba(201,168,76,.2));
        flex-shrink: 0;
      }}
      .brand-text {{
        display: flex;
        flex-direction: column;
      }}
      .brand-name {{
        font-family: 'Playfair Display', serif;
        font-size: 1rem;
        font-weight: 700;
        color: #c9a84c;
        letter-spacing: -.01em;
        display: flex;
        align-items: center;
        gap: 4px;
      }}
      .brand-name .light {{
        font-family: 'DM Sans', sans-serif;
        font-weight: 300;
        color: #eaf0fb;
      }}
      .brand-sub {{
        font-size: .65rem;
        color: #4a5a72;
        letter-spacing: .06em;
        text-transform: uppercase;
        font-family: 'DM Sans', sans-serif;
        margin-top: 2px;
      }}
    </style>
    </head>
    <body>
      <div class="logo-wrap">
        {ANIMATED_LOGO_SVG_CODE}
      </div>
      <div class="brand-text">
        <div class="brand-name">
          <span class="light">Interview</span>IQ
        </div>
        <div class="brand-sub">AI Coach</div>
      </div>
    </body>
    </html>
    """, height=72, scrolling=False)


# DESIGN SYSTEM — FULLY RESPONSIVE

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,300&family=DM+Mono:wght@300;400;500&family=Playfair+Display:wght@600;700&display=swap');

:root {
  --c-bg:         #080c14;
  --c-surface:    #0e1420;
  --c-surface2:   #141b28;
  --c-surface3:   #1a2235;
  --c-border:     #1e2a3d;
  --c-border2:    #253347;
  --c-gold:       #c9a84c;
  --c-gold-light: #e8c96a;
  --c-gold-dim:   rgba(201,168,76,.12);
  --c-blue:       #4a8eff;
  --c-blue-dim:   rgba(74,142,255,.10);
  --c-green:      #34d399;
  --c-red:        #f87171;
  --c-amber:      #fbbf24;
  --c-text:       #eaf0fb;
  --c-text2:      #94a3b8;
  --c-text3:      #4a5a72;
  --radius-sm:    8px;
  --radius-md:    14px;
  --radius-lg:    20px;
  --radius-xl:    28px;
  --shadow-card:  0 4px 24px rgba(0,0,0,.4), 0 1px 4px rgba(0,0,0,.3);
  --shadow-glow:  0 0 40px rgba(201,168,76,.07);
}

*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main,
section[data-testid="stSidebar"] ~ div {
  font-family: 'DM Sans', sans-serif !important;
  background-color: var(--c-bg) !important;
  color: var(--c-text) !important;
}

/* ── Responsive viewport meta equivalent via CSS ── */
[data-testid="stAppViewContainer"] {
  max-width: 100% !important;
  overflow-x: hidden !important;
}

/* ── Main content area padding responsive ── */
[data-testid="stMain"] > div {
  padding-left: clamp(0.75rem, 3vw, 2rem) !important;
  padding-right: clamp(0.75rem, 3vw, 2rem) !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--c-surface); }
::-webkit-scrollbar-thumb { background: var(--c-border2); border-radius: 99px; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
  background: var(--c-surface) !important;
  border-right: 1px solid var(--c-border) !important;
  min-width: 220px !important;
  max-width: 260px !important;
}
[data-testid="stSidebar"] * { font-family: 'DM Sans', sans-serif !important; }

/* Mobile: sidebar becomes a drawer overlay */
@media (max-width: 768px) {
  [data-testid="stSidebar"] {
    min-width: 200px !important;
    max-width: 80vw !important;
  }
  /* Tighten sidebar padding */
  [data-testid="stSidebar"] > div {
    padding: 0.75rem !important;
  }
}

/* ── BUTTONS ── */
.stButton > button {
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 500 !important;
  font-size: .875rem !important;
  letter-spacing: .01em !important;
  color: var(--c-text2) !important;
  background: var(--c-surface2) !important;
  border: 1px solid var(--c-border) !important;
  border-radius: var(--radius-sm) !important;
  padding: .55rem 1.1rem !important;
  transition: all .18s ease !important;
  box-shadow: none !important;
  width: 100% !important;      /* always full-width for touch targets */
  min-height: 44px !important; /* accessible touch target */
}
.stButton > button:hover {
  color: var(--c-text) !important;
  background: var(--c-surface3) !important;
  border-color: var(--c-border2) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 16px rgba(0,0,0,.3) !important;
}
.stButton > button[kind="primary"] {
  color: #0a0f1a !important;
  background: linear-gradient(135deg, var(--c-gold) 0%, var(--c-gold-light) 100%) !important;
  border-color: transparent !important;
  font-weight: 600 !important;
}
.stButton > button[kind="primary"]:hover {
  background: linear-gradient(135deg, var(--c-gold-light) 0%, var(--c-gold) 100%) !important;
  box-shadow: 0 4px 24px rgba(201,168,76,.35) !important;
  transform: translateY(-2px) !important;
}

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
  font-family: 'DM Sans', sans-serif !important;
  font-size: .9rem !important;
  background: var(--c-surface2) !important;
  color: var(--c-text) !important;
  border: 1px solid var(--c-border2) !important;
  border-radius: var(--radius-sm) !important;
  padding: .65rem .9rem !important;
  -webkit-appearance: none;  /* remove iOS default styling */
  appearance: none;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--c-gold) !important;
  box-shadow: 0 0 0 3px rgba(201,168,76,.12) !important;
  outline: none !important;
}
.stTextInput > label,
.stTextArea > label {
  color: var(--c-text2) !important;
  font-size: .8rem !important;
  font-weight: 500 !important;
  letter-spacing: .04em !important;
  text-transform: uppercase !important;
}

/* Increase font size on mobile to prevent iOS auto-zoom (must be ≥16px) */
@media (max-width: 768px) {
  .stTextInput > div > div > input,
  .stTextArea > div > div > textarea {
    font-size: 16px !important;
  }
}

/* ── SELECTBOX ── */
.stSelectbox > div > div {
  background: var(--c-surface2) !important;
  border: 1px solid var(--c-border2) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--c-text) !important;
  min-height: 44px !important;
}
.stSelectbox > label {
  color: var(--c-text2) !important;
  font-size: .8rem !important;
  text-transform: uppercase !important;
  letter-spacing: .04em !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--c-surface2) !important;
  border-radius: var(--radius-sm) !important;
  border: 1px solid var(--c-border) !important;
  padding: 3px !important;
  gap: 2px !important;
  flex-wrap: wrap !important; /* wrap on very small screens */
}
.stTabs [role="tab"] {
  font-family: 'DM Sans', sans-serif !important;
  font-size: .83rem !important;
  font-weight: 500 !important;
  color: var(--c-text3) !important;
  background: transparent !important;
  border: none !important;
  border-radius: 6px !important;
  padding: .45rem 1rem !important;
  transition: all .15s ease !important;
  min-height: 40px !important;
  white-space: nowrap !important;
}
.stTabs [aria-selected="true"] {
  color: #0a0f1a !important;
  background: linear-gradient(135deg, var(--c-gold) 0%, var(--c-gold-light) 100%) !important;
  font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.2rem !important; }

@media (max-width: 480px) {
  .stTabs [role="tab"] {
    font-size: .78rem !important;
    padding: .4rem .7rem !important;
  }
}

/* ── ALERTS ── */
.stAlert { border-radius: var(--radius-sm) !important; font-size: .875rem !important; }
.stSuccess { background: rgba(52,211,153,.08) !important; border-color: rgba(52,211,153,.25) !important; }
.stError   { background: rgba(248,113,113,.08) !important; border-color: rgba(248,113,113,.25) !important; }
.stInfo    { background: rgba(74,142,255,.08) !important; border-color: rgba(74,142,255,.20) !important; }
.stWarning { background: rgba(251,191,36,.08) !important; border-color: rgba(251,191,36,.25) !important; }

/* ── METRICS ── */
[data-testid="stMetric"] {
  background: var(--c-surface2) !important;
  border: 1px solid var(--c-border) !important;
  border-radius: var(--radius-md) !important;
  padding: 1.1rem 1.3rem !important;
}
[data-testid="stMetricLabel"] { color: var(--c-text3) !important; font-size: .78rem !important; text-transform: uppercase; letter-spacing: .06em; }
[data-testid="stMetricValue"] { color: var(--c-text) !important; font-family: 'DM Mono', monospace !important; font-size: 1.8rem !important; }
[data-testid="stMetricDelta"] { font-size: .8rem !important; }

@media (max-width: 480px) {
  [data-testid="stMetricValue"] { font-size: 1.3rem !important; }
  [data-testid="stMetric"] { padding: .8rem 1rem !important; }
}

/* ── SPINNER ── */
.stSpinner > div { border-top-color: var(--c-gold) !important; }

/* ── HIDE CHROME ── */
#MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stHeader"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], header { display: none !important; }

[data-testid="stAppViewContainer"] > [data-testid="stHeader"] { display:none !important; }
section[data-testid="stSidebar"] + div > div:first-child { background: var(--c-bg) !important; }
.stApp > header { background: transparent !important; display: none !important; }

/* ── ANIMATIONS ── */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}
.page-enter { animation: fadeUp .4s ease forwards; }

/* ─────────────────────────────────────────────────────
   LOGIN CARD
───────────────────────────────────────────────────── */
.login-card {
  background: var(--c-surface);
  border: 1px solid var(--c-border2);
  border-radius: var(--radius-lg);
  padding: 32px 28px;
  box-shadow: var(--shadow-card), var(--shadow-glow);
  animation: fadeUp .5s ease forwards;
}
@media (max-width: 480px) {
  .login-card {
    padding: 24px 16px;
    border-radius: var(--radius-md);
  }
}

/* ─────────────────────────────────────────────────────
   TYPOGRAPHY
───────────────────────────────────────────────────── */
.section-eyebrow {
  font-size: .72rem;
  font-weight: 600;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: var(--c-gold);
  margin-bottom: 6px;
}
.section-heading {
  font-family: 'Playfair Display', serif;
  font-size: clamp(1.3rem, 4vw, 1.75rem);
  font-weight: 700;
  color: var(--c-text);
  line-height: 1.2;
  margin: 0 0 6px;
}
.section-sub {
  color: var(--c-text2);
  font-size: clamp(.82rem, 2vw, .9rem);
  font-weight: 300;
}

/* ─────────────────────────────────────────────────────
   KPI CHIPS
───────────────────────────────────────────────────── */
.kpi-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin: 18px 0;
}
.kpi-chip {
  display: flex;
  align-items: center;
  gap: 9px;
  background: var(--c-surface2);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-sm);
  padding: 9px 16px;
  font-family: 'DM Mono', monospace;
  font-size: .82rem;
  color: var(--c-text2);
  flex: 1 1 auto;
  min-width: 110px;
}
.kpi-chip .val { color: var(--c-text); font-weight: 500; }
.kpi-chip .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--c-gold); flex-shrink: 0; }

@media (max-width: 480px) {
  .kpi-chip {
    padding: 8px 12px;
    font-size: .75rem;
    min-width: 90px;
  }
}

/* ─────────────────────────────────────────────────────
   ROLE CARDS — Responsive Grid
───────────────────────────────────────────────────── */
.role-card {
  position: relative;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-md);
  padding: 0;
  cursor: pointer;
  transition: border-color .2s, transform .2s, box-shadow .2s;
  overflow: hidden;
  margin-bottom: 4px;
}
.role-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: var(--c-gold-dim);
  opacity: 0;
  transition: opacity .2s;
}
.role-card:hover {
  border-color: var(--c-gold);
  transform: translateY(-3px);
  box-shadow: 0 12px 36px rgba(0,0,0,.5), 0 0 0 1px var(--c-gold);
}
.role-card:hover::before { opacity: 1; }
.role-card .rc-img-wrap {
  width: 100%;
  height: clamp(60px, 12vw, 100px);
  overflow: hidden;
}
.role-card .rc-img-wrap img {
  width: 100%; height: 100%; object-fit: cover;
  transition: transform .3s ease;
  display: block;
}
.role-card:hover .rc-img-wrap img { transform: scale(1.05); }
.role-card .rc-body { padding: 12px 14px; position: relative; }
.role-card .rc-badge {
  position: absolute;
  top: 10px; right: 10px;
  font-size: .65rem;
  font-weight: 600;
  letter-spacing: .06em;
  text-transform: uppercase;
  padding: 3px 8px;
  border-radius: 99px;
  border: 1px solid var(--c-border2);
  color: var(--c-text3);
  background: var(--c-surface);
}
.role-card .rc-title {
  font-size: clamp(.82rem, 2vw, .93rem);
  font-weight: 600;
  color: var(--c-text);
  margin-bottom: 3px;
}
.role-card .rc-desc { font-size: .76rem; color: var(--c-text3); line-height: 1.5; }

/* ─────────────────────────────────────────────────────
   MISC COMPONENTS
───────────────────────────────────────────────────── */
.hr { border: none; border-top: 1px solid var(--c-border); margin: 22px 0; }

.q-block {
  position: relative;
  background: var(--c-surface);
  border: 1px solid var(--c-border2);
  border-left: 3px solid var(--c-gold);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  padding: clamp(14px, 3vw, 24px) clamp(14px, 4vw, 28px);
  margin-bottom: 22px;
}
.q-block .q-label {
  font-size: .7rem; letter-spacing: .12em; text-transform: uppercase;
  color: var(--c-gold); font-weight: 600; margin-bottom: 8px;
}
.q-block .q-text { font-size: clamp(.95rem, 2.5vw, 1.12rem); font-weight: 500; line-height: 1.65; color: var(--c-text); }
.q-block .q-meta { margin-top: 12px; font-size: .75rem; color: var(--c-text3); font-family: 'DM Mono', monospace; }

.fb-card {
  background: var(--c-surface);
  border: 1px solid var(--c-border2);
  border-radius: var(--radius-md);
  padding: clamp(16px, 3vw, 28px);
  font-size: clamp(.82rem, 2vw, .9rem);
  line-height: 1.75;
  color: var(--c-text2);
  overflow-x: auto; /* allow horizontal scroll for tables on mobile */
}
.fb-card strong { color: var(--c-text); }
.fb-card h2, .fb-card h3, .fb-card h4 {
  color: var(--c-text);
  font-family: 'DM Sans', sans-serif !important;
  font-size: 1rem; font-weight: 600; margin: 1.2em 0 .4em;
}
.fb-card table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: .85rem; min-width: 300px; }
.fb-card th {
  background: var(--c-surface2) !important;
  color: var(--c-gold) !important;
  padding: 9px 14px; text-align: left; font-weight: 600;
  font-size: .75rem; letter-spacing: .05em; text-transform: uppercase;
  border-bottom: 1px solid var(--c-border2);
}
.fb-card td { padding: 9px 14px; border-bottom: 1px solid var(--c-border); color: var(--c-text2); }
.fb-card tr:last-child td { border-bottom: none; }

.score-badge { text-align: center; padding: 20px 0; }
.score-badge .sb-num { font-family: 'DM Mono', monospace; font-size: 3.6rem; font-weight: 500; line-height: 1; }
.score-badge .sb-label { font-size: .72rem; letter-spacing: .1em; text-transform: uppercase; color: var(--c-text3); margin-top: 6px; }
.score-badge .sb-bar { height: 4px; background: var(--c-surface3); border-radius: 99px; margin: 14px auto; width: 80%; position: relative; overflow: hidden; }
.score-badge .sb-fill { height: 100%; border-radius: 99px; transition: width .6s ease; }

/* ── SESSION LOG TABLE ── */
.log-row {
  display: grid;
  grid-template-columns: 140px 1fr 70px 60px;
  gap: 8px;
  padding: 12px 0;
  border-bottom: 1px solid var(--c-border);
  align-items: center;
  font-size: .85rem;
}
.log-row:last-child { border-bottom: none; }

/* Stack log rows on small screens */
@media (max-width: 600px) {
  .log-row {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto auto;
    gap: 4px 8px;
  }
  .log-row .log-q { grid-column: 1 / -1; font-size: .78rem; }
}

.log-role-chip {
  background: var(--c-blue-dim);
  border: 1px solid rgba(74,142,255,.2);
  border-radius: 6px; padding: 3px 10px;
  font-size: .75rem; color: var(--c-blue); font-weight: 500;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.log-q { color: var(--c-text2); }
.log-score { font-family: 'DM Mono', monospace; font-weight: 600; font-size: .95rem; }
.log-time { color: var(--c-text3); font-size: .75rem; font-family: 'DM Mono', monospace; }

/* ── SIDEBAR USER BLOCK ── */
.sb-user {
  display: flex; align-items: center; gap: 12px;
  padding: 14px 0 18px;
  border-bottom: 1px solid var(--c-border);
  margin-bottom: 16px;
}
.sb-avatar {
  width: 40px; height: 40px;
  background: var(--c-gold-dim);
  border: 1.5px solid var(--c-gold);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.1rem; font-weight: 700;
  color: var(--c-gold);
  font-family: 'Playfair Display', serif;
  flex-shrink: 0;
}
.sb-user-name { font-weight: 600; font-size: .92rem; color: var(--c-text); line-height: 1.2; }
.sb-user-sub  { font-size: .75rem; color: var(--c-text3); }

/* ── INTERVIEW HEADER ── */
.iv-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 0 20px;
  border-bottom: 1px solid var(--c-border);
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.iv-role-badge {
  background: var(--c-gold-dim);
  border: 1px solid rgba(201,168,76,.3);
  border-radius: 6px; padding: 4px 12px;
  font-size: .78rem; font-weight: 600;
  color: var(--c-gold); letter-spacing: .04em;
}

/* ── TIP CALLOUT ── */
.tip-callout {
  background: var(--c-blue-dim);
  border: 1px solid rgba(74,142,255,.18);
  border-left: 3px solid var(--c-blue);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  padding: 13px 16px;
  font-size: clamp(.78rem, 2vw, .82rem);
  color: var(--c-text2);
  line-height: 1.6;
}
.tip-callout b { color: var(--c-blue); }

/* ── PLOTLY ── */
.js-plotly-plot, .plot-container { background: transparent !important; }

/* ── IFRAME ── */
iframe { background: transparent !important; }

/* ─────────────────────────────────────────────────────
   MOBILE-SPECIFIC LAYOUT OVERRIDES
   (Streamlit columns collapse automatically, but we
    add extra polish for narrow viewports)
───────────────────────────────────────────────────── */

/* Ensure Streamlit columns don't overflow on mobile */
@media (max-width: 768px) {
  /* Full-bleed column on mobile */
  [data-testid="column"] {
    min-width: 0 !important;
    padding-left: 4px !important;
    padding-right: 4px !important;
  }

  /* Interview header: stack title + badge */
  .iv-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    padding-bottom: 14px;
    margin-bottom: 16px;
  }
  .iv-header span:first-child { font-size: 1.2rem !important; }

  /* Q block tighter on mobile */
  .q-block { margin-bottom: 14px; }

  /* Section headings */
  .section-eyebrow { font-size: .68rem; }
}

@media (max-width: 480px) {
  /* KPI row: 2 per row on very small screens */
  .kpi-chip { flex: 1 1 calc(50% - 10px); }

  /* Shrink score badge */
  .score-badge .sb-num { font-size: 2.6rem; }

  /* Tighter hr */
  .hr { margin: 14px 0; }

  /* Login card full width */
  .login-card { margin: 0 !important; }
}

/* ─────────────────────────────────────────────────────
   TOUCH / ACTIVE STATES (no hover on mobile)
───────────────────────────────────────────────────── */
@media (hover: none) {
  .stButton > button:hover {
    transform: none !important;
    box-shadow: none !important;
  }
  .stButton > button:active {
    transform: scale(0.97) !important;
    opacity: .9 !important;
  }
  .role-card:hover {
    transform: none !important;
  }
  .role-card:active {
    border-color: var(--c-gold) !important;
    transform: scale(0.98) !important;
  }
}
</style>
""", unsafe_allow_html=True)


# HELPERS

def tts_play(text: str, lang: str = "en", tld: str = "us"):
    import io
    try:
        buf = io.BytesIO()
        gTTS(text=text[:250], lang=lang, tld=tld, slow=False).write_to_fp(buf)
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode()
        _render_audio(b64)
    except Exception as e:
        st.error(f"Voice error: {e}")


def _render_audio(b64: str):
    st.components.v1.html(f"""
    <div id="audio-wrap" style="
        font-family:'DM Sans',sans-serif;
        background:#141b28;
        border:1px solid #253347;
        border-radius:10px;
        padding:10px 16px;
        margin:8px 0;
        display:flex;
        align-items:center;
        gap:12px;
    ">
      <span style="font-size:1.2rem;">🔊</span>
      <audio id="iv-player" controls style="flex:1;height:34px;accent-color:#c9a84c;">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
      </audio>
    </div>
    <script>
      (function() {{
        var player = document.getElementById('iv-player');
        if (!player) return;
        function tryPlay() {{
          var promise = player.play();
          if (promise !== undefined) {{
            promise.then(function() {{}}).catch(function(err) {{
              var wrap = document.getElementById('audio-wrap');
              var btn  = document.createElement('button');
              btn.innerText = '▶  Play';
              btn.style = [
                'padding:6px 16px','background:#c9a84c','color:#0a0f1a',
                'border:none','border-radius:6px','cursor:pointer',
                'font-size:13px','font-weight:700','white-space:nowrap','flex-shrink:0'
              ].join(';');
              btn.onclick = function() {{ player.play(); btn.remove(); }};
              wrap.appendChild(btn);
            }});
          }}
        }}
        if (player.readyState >= 2) {{ tryPlay(); }}
        else {{ player.addEventListener('canplay', tryPlay, {{ once: true }}); }}
      }})();
    </script>
    """, height=70)


INTERVIEWER_PERSONAS = {
    "Sarah  ·  Female / US":   {"lang": "en", "tld": "us",   "gender": "female", "avatar": "👩‍💼", "color": "#c9a84c"},
    "Emma   ·  Female / UK":   {"lang": "en", "tld": "co.uk","gender": "female", "avatar": "👩‍💻", "color": "#a78bfa"},
    "Priya  ·  Female / IN":   {"lang": "en", "tld": "co.in","gender": "female", "avatar": "👩‍🔬", "color": "#f87171"},
    "Nimasha · Female / LK":   {"lang": "en", "tld": "co.in","gender": "female", "avatar": "👩‍🎓", "color": "#34d399"},
    "James  ·  Male / US":     {"lang": "en", "tld": "us",   "gender": "male",   "avatar": "👨‍💼", "color": "#4a8eff"},
    "Oliver ·  Male / UK":     {"lang": "en", "tld": "co.uk","gender": "male",   "avatar": "👨‍💻", "color": "#34d399"},
    "Arjun  ·  Male / IN":     {"lang": "en", "tld": "co.in","gender": "male",   "avatar": "👨‍🔬", "color": "#fb923c"},
    "Kasun  ·  Male / LK":     {"lang": "en", "tld": "co.in","gender": "male",   "avatar": "👨‍🎓", "color": "#38bdf8"},
}


def build_interviewer_speech(role: str, persona_name: str) -> str:
    import random
    p       = INTERVIEWER_PERSONAS.get(persona_name, list(INTERVIEWER_PERSONAS.values())[0])
    first   = persona_name.split()[0].strip()
    is_lk   = "LK" in persona_name
    stage   = st.session_state.get("interview_stage", 0)
    q       = st.session_state.get("current_q", "")
    cname   = st.session_state.get("candidate_name", "").strip()
    cname_f = cname.split()[0] if cname else ""
    addr    = f", {cname_f}" if cname_f else ""

    if stage == 0:
        if is_lk:
            opts = [
                f"Good morning! Welcome, please have a seat. I'm {first} from the HR team. "
                f"It's great to have you here today. So, could you start by telling me about yourself?",
                f"Hello, welcome! I'm {first}. Thank you for coming in today. "
                f"Let's begin — please tell me a little about yourself.",
            ]
        elif p["gender"] == "female":
            opts = [
                f"Hi, good morning! I'm {first}, I'll be your interviewer today. "
                f"It's lovely to meet you. Let's start — tell me about yourself.",
                f"Hello! Welcome, I'm {first}. Please make yourself comfortable. "
                f"So — tell me a little about yourself and your background.",
            ]
        else:
            opts = [
                f"Good morning! I'm {first}, I'll be conducting your interview today. "
                f"Great to meet you. Let's start — tell me about yourself.",
                f"Hi there, I'm {first}. Thanks for coming in. "
                f"Let's begin — walk me through your background.",
            ]
        return random.choice(opts)

    if stage == 1:
        warmups = [
            f"That's great{addr}, thank you for sharing that. "
            f"Now let's move to the role. {q}",
            f"Wonderful{addr}. It sounds like you have a strong background. "
            f"So, for this {role} position — {q}",
            f"Excellent{addr}. I appreciate you sharing that. "
            f"Alright, let's get into it. {q}",
        ]
        return random.choice(warmups)[:300]

    q_num = stage - 2
    use_name = bool(cname_f and q_num % 3 == 0)
    if use_name:
        opts = [
            f"Thank you{addr}. Moving on — {q}",
            f"Good answer{addr}. Next question — {q}",
            f"Appreciated{addr}. Here's another one. {q}",
        ]
    else:
        opts = [
            f"Good. Let's continue. {q}",
            f"Thank you. Next — {q}",
            f"Alright, moving on. {q}",
            f"Right. Here's the next one. {q}",
            f"Great. Let's keep going. {q}",
        ]
    return random.choice(opts)[:300]


def play_interviewer_speech(role: str, persona_name: str) -> str:
    import io
    p      = INTERVIEWER_PERSONAS.get(persona_name, list(INTERVIEWER_PERSONAS.values())[0])
    first  = persona_name.split()[0].strip()
    script = build_interviewer_speech(role, persona_name)
    cache_key = f"_audio_{hash(script + persona_name)}"
    if cache_key not in st.session_state:
        with st.spinner(f"🎙 {first} is speaking…"):
            try:
                import io
                buf = io.BytesIO()
                gTTS(text=script[:300], lang=p["lang"], tld=p["tld"], slow=False).write_to_fp(buf)
                buf.seek(0)
                st.session_state[cache_key] = base64.b64encode(buf.read()).decode()
            except Exception as e:
                st.error(f"TTS failed: {e}")
                return script
    st.session_state["last_audio_key"] = cache_key
    return script


def ai_question(role: str) -> str:
    intern = is_intern_role(role)
    field  = get_field_context(role)
    if intern:
        prompt = (
            f"You are a friendly hiring manager interviewing a student or fresh graduate "
            f"for a {role} position in the {field} field. "
            "Write ONE beginner-friendly interview question that tests fundamentals, curiosity, "
            "and eagerness to learn — no deep expertise required. "
            "Return only the question, no preamble."
        )
    else:
        prompt = (
            f"You are a Senior Hiring Manager recruiting for a {role} position in the {field} field. "
            "Write ONE specific, challenging interview question that tests real expertise. "
            "Avoid generic questions. Return only the question, no preamble."
        )
    try:
        r = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile", max_tokens=80)
        return r.choices[0].message.content.strip()
    except:
        return f"Tell me about yourself and why you are interested in the {role} position."


def ai_evaluate(q: str, ans: str, role: str) -> str:
    intern  = is_intern_role(role)
    field   = get_field_context(role)
    stage   = st.session_state.get("interview_stage", 0)
    cname   = st.session_state.get("candidate_name", "").strip()

    if stage <= 1 and not cname:
        try:
            name_prompt = (
                f"From this self-introduction: \"{ans}\"\n"
                "Extract only the person's first name (one word). "
                "If no name found, return 'Candidate'. Return ONLY the name."
            )
            nr = client.chat.completions.create(
                messages=[{"role": "user", "content": name_prompt}],
                model="llama-3.3-70b-versatile", max_tokens=10)
            extracted = nr.choices[0].message.content.strip().split()[0]
            if len(extracted) > 1 and extracted.isalpha():
                st.session_state.candidate_name = extracted.capitalize()
        except:
            pass

    if stage <= 1:
        prompt = f"""You are {role} interviewer. Evaluate this self-introduction answer.

Question: {q}
Answer: {ans}

This is an INTRODUCTORY question — do NOT evaluate technical knowledge.
Evaluate ONLY: confidence, clarity, relevance to role, and communication.

Use this exact format:

**Overall Score: X/10**

| Dimension | Score | Feedback |
|---|---|---|
| Confidence & Presence | X/10 | … |
| Communication Clarity | X/10 | … |
| Relevance to Role | X/10 | … |
| Structure & Flow | X/10 | … |

**What Worked Well:**
(2 specific positives from their answer)

**Perfect "Tell Me About Yourself" Answer for a {role}:**
(Write a 5-6 sentence ideal self-introduction that mentions name, background, key skills, why this role, and enthusiasm)

**Coaching Tips:**
- Tip 1: (specific improvement)
- Tip 2: (specific improvement)
- Tip 3: (specific improvement)

**What to Say vs What NOT to Say:**
✅ DO: (one example phrase)
❌ AVOID: (one example phrase)
"""
    else:
        tone = "encouraging and constructive" if intern else "rigorous and professional"
        prompt = f"""You are a Senior {role} Interviewer in the {field} field. Tone: {tone}.

Question: {q}
Answer: {ans}

**Overall Score: X/10**

| Dimension | Score | Feedback |
|---|---|---|
| Technical Depth | X/10 | … |
| Communication Clarity | X/10 | … |
| Structure & Logic | X/10 | … |
| Relevance | X/10 | … |

**Strengths:**
(2 specific strengths from their answer)

**Perfect Model Answer:**
(Ideal 5-7 sentence answer showing senior-level thinking)

**Coaching Tips:**
- Tip 1: (specific improvement)
- Tip 2: (specific improvement)

**Key Phrases to Use Next Time:**
(2-3 power phrases interviewers love for this type of question)
"""

    try:
        r = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile", max_tokens=700)
        return r.choices[0].message.content
    except Exception as e:
        return f"Evaluation failed: {str(e)}"


def record_mic(timeout=12) -> str | None:
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as src:
            recognizer.adjust_for_ambient_noise(src, duration=1)
            audio = recognizer.listen(src, timeout=timeout)
        return recognizer.recognize_google(audio)
    except: return None


def extract_score(fb: str) -> int | None:
    m = re.search(r"Overall Score:\s*(\d+)/10", fb)
    return int(m.group(1)) if m else None


def score_color(s: int) -> str:
    if s >= 8: return "#34d399"
    if s >= 5: return "#fbbf24"
    return "#f87171"


def make_gauge(score: float):
    c = score_color(int(score))
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        gauge=dict(
            axis=dict(range=[0,10], tickcolor="#4a5a72", tickwidth=1, ticklen=4),
            bar=dict(color=c, thickness=.35),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            steps=[{"range":[0,10],"color":"#141b28"}],
            threshold=dict(line=dict(color=c,width=2), thickness=.7, value=score),
        ),
        number=dict(font=dict(color=c, size=32, family="DM Mono")),
        title=dict(text="Score", font=dict(color="#4a5a72", size=12)),
    ))
    fig.update_layout(height=190, margin=dict(l=10,r=10,t=24,b=0),
                      paper_bgcolor="rgba(0,0,0,0)", font_color="#94a3b8")
    return fig


def make_progress_chart(scores):
    if len(scores) < 2: return None
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(1, len(scores)+1)), y=scores,
        mode="lines+markers",
        line=dict(color="#c9a84c", width=2, shape="spline"),
        marker=dict(size=7, color="#c9a84c", line=dict(color="#0e1420", width=2)),
        fill="tozeroy", fillcolor="rgba(201,168,76,.06)",
    ))
    avg = sum(scores) / len(scores)
    fig.add_hline(y=avg, line_dash="dot", line_color="#4a5a72",
                  annotation_text=f"avg {avg:.1f}", annotation_position="right",
                  annotation_font_color="#4a5a72")
    fig.update_layout(
        height=200, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, color="#4a5a72", title="Attempt"),
        yaxis=dict(range=[0,10], showgrid=True, gridcolor="#141b28", color="#4a5a72"),
        margin=dict(l=10,r=40,t=10,b=30), font_color="#94a3b8",
    )
    return fig


def make_dist_chart(scores):
    counts = {str(i): scores.count(i) for i in range(1, 11)}
    colors = [score_color(i) for i in range(1, 11)]
    fig = go.Figure(go.Bar(
        x=list(counts.keys()), y=list(counts.values()),
        marker=dict(color=colors, opacity=.75),
        text=list(counts.values()), textposition="outside",
        textfont=dict(color="#94a3b8", size=10),
    ))
    fig.update_layout(
        height=220, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, color="#4a5a72", title="Score"),
        yaxis=dict(showgrid=True, gridcolor="#141b28", color="#4a5a72"),
        margin=dict(l=10,r=10,t=10,b=30), font_color="#94a3b8",
    )
    return fig


# SESSION STATE

_D = dict(
    logged_in=False, username="", page="login",
    score_history=[], attempt_log=[],
    selected_role="", current_q="",
    last_feedback="", q_generated_at=None,
    interviewer_persona="Sarah  ·  Female / US",
    last_script="",
    interview_stage=0,
    last_audio_key="",
    candidate_name="",
    conversation_history=[],
)
for k, v in _D.items():
    if k not in st.session_state:
        st.session_state[k] = v

def goto(page):
    st.session_state.page = page
    st.session_state.last_feedback = ""

def start_practice(role):
    st.session_state.selected_role        = role
    with st.spinner("Generating question…"):
        st.session_state.current_q        = ai_question(role)
    st.session_state.last_feedback        = ""
    st.session_state.last_script          = ""
    st.session_state.last_audio_key       = ""
    st.session_state.interview_stage      = 0
    st.session_state.candidate_name       = ""
    st.session_state.conversation_history = []
    st.session_state.q_generated_at       = datetime.now()
    st.session_state.page                 = "interview"


# FIELD / ROLE CATALOGUE

FIELDS = {
    "it": {
        "label": "Information Technology",
        "icon": "💻",
        "color": "rgba(74,142,255,.10)",
        "accent": "#4a8eff",
        "roles": [
            ("Software Developer",          "💻", "System design, coding & architecture",     "DEV",   "pro"),
            ("SQA Engineer",                "🔍", "Quality assurance & test automation",       "QA",    "pro"),
            ("DevOps Engineer",             "⚙️", "CI/CD, cloud & infrastructure",            "OPS",   "pro"),
            ("UI/UX Designer",              "🎨", "Research, wireframes & interaction",        "UX",    "pro"),
            ("Data Scientist",              "📊", "ML, statistics & data analysis",            "DS",    "pro"),
            ("Cybersecurity Analyst",       "🔐", "Threat detection, compliance & security",   "SEC",   "pro"),
            ("Cloud Architect",             "☁️", "AWS / Azure / GCP architecture",           "CLD",   "pro"),
            ("Mobile App Developer",        "📱", "iOS / Android & cross-platform apps",       "MOB",   "pro"),
            ("Software Engineering Intern", "🖥️", "Coding fundamentals & problem solving",    "INT",   "intern"),
            ("QA Intern",                   "🧪", "Manual testing, bug reporting & tools",     "INT",   "intern"),
            ("UI/UX Design Intern",         "✏️", "Figma, wireframing & design thinking",      "INT",   "intern"),
            ("Data Science Intern",         "🔬", "Python, pandas & basic ML",                 "INT",   "intern"),
            ("IT Support Intern",           "🛠️", "Helpdesk, troubleshooting & networking",   "INT",   "intern"),
            ("Cybersecurity Intern",        "🛡️", "Security basics, OWASP & ethical hacking", "INT",   "intern"),
        ],
    },
    "hrm": {
        "label": "Human Resource Management",
        "icon": "🤝",
        "color": "rgba(251,191,36,.08)",
        "accent": "#fbbf24",
        "roles": [
            ("HR Manager",               "🤝", "Talent strategy, policy & people ops",       "HRM",  "pro"),
            ("Talent Acquisition Lead",  "🎯", "Sourcing, recruitment & employer branding",  "TA",   "pro"),
            ("L&D Specialist",           "📚", "Training, upskilling & performance mgmt",    "L&D",  "pro"),
            ("Compensation & Benefits",  "💰", "Pay structures, benchmarking & rewards",     "C&B",  "pro"),
            ("HR Business Partner",      "🏢", "Org design, change mgmt & leadership",       "HRBP", "pro"),
            ("Employee Relations Mgr",   "⚖️", "Conflict resolution, policy & compliance",  "ER",   "pro"),
            ("HR Intern",                "👥", "HR basics, recruitment support & admin",     "INT",  "intern"),
            ("Recruitment Intern",       "📋", "Job posting, screening & coordination",      "INT",  "intern"),
            ("L&D Intern",               "📖", "Training materials & session support",       "INT",  "intern"),
        ],
    },
    "accounting": {
        "label": "Accounting & Finance",
        "icon": "📒",
        "color": "rgba(52,211,153,.08)",
        "accent": "#34d399",
        "roles": [
            ("Chartered Accountant",     "📒", "Financial reporting, auditing & standards",  "CA",   "pro"),
            ("Financial Analyst",        "📈", "Valuation, forecasting & investment analysis","FA",   "pro"),
            ("Management Accountant",    "🏦", "Cost accounting, budgeting & controls",      "MA",   "pro"),
            ("Audit & Assurance",        "🔎", "Internal / external audit & risk",           "AUD",  "pro"),
            ("Tax Consultant",           "🧾", "Tax planning, compliance & advisory",        "TAX",  "pro"),
            ("CFO / Finance Director",   "💼", "Treasury, capital structure & strategy",     "CFO",  "pro"),
            ("Accounting Intern",        "🧮", "Bookkeeping basics, ledgers & reconciliation","INT", "intern"),
            ("Finance Intern",           "📊", "Financial modelling, Excel & reporting",     "INT",  "intern"),
            ("Audit Intern",             "🗂️", "Workpapers, sampling & audit procedures",   "INT",  "intern"),
        ],
    },
    "marketing": {
        "label": "Marketing & Communications",
        "icon": "📣",
        "color": "rgba(248,113,113,.08)",
        "accent": "#f87171",
        "roles": [
            ("Digital Marketing Manager","📣", "SEO, paid media, analytics & growth",        "DMM",  "pro"),
            ("Brand Strategist",         "🎨", "Positioning, identity & brand campaigns",    "BRD",  "pro"),
            ("Content Marketing Lead",   "✍️", "Content strategy, SEO & editorial",         "CNT",  "pro"),
            ("Social Media Manager",     "📱", "Community, engagement & paid social",        "SMM",  "pro"),
            ("PR & Communications",      "📰", "Media relations, messaging & crisis comms",  "PR",   "pro"),
            ("Marketing Intern",         "📊", "Campaigns, analytics & social media",        "INT",  "intern"),
            ("Content Creation Intern",  "🖊️", "Copywriting, blogs & visual content",       "INT",  "intern"),
            ("Social Media Intern",      "📲", "Scheduling, engagement & reporting",         "INT",  "intern"),
        ],
    },
    "management": {
        "label": "Business & Management",
        "icon": "🏢",
        "color": "rgba(167,139,250,.08)",
        "accent": "#a78bfa",
        "roles": [
            ("Product Manager",          "🗂️", "Roadmaps, stakeholders & product strategy", "PM",   "pro"),
            ("Project Manager",          "📅", "Planning, delivery & risk management",       "PJM",  "pro"),
            ("Business Analyst",         "🔍", "Requirements, process mapping & solutions",  "BA",   "pro"),
            ("Operations Manager",       "⚙️", "Process optimisation & supply chain",       "OPS",  "pro"),
            ("Strategy Consultant",      "♟️", "Market analysis, problem solving & decks",  "STR",  "pro"),
            ("Entrepreneur / Founder",   "🚀", "Pitching, business model & growth",          "FND",  "pro"),
            ("Business Analyst Intern",  "📋", "Process flow, requirements & reporting",     "INT",  "intern"),
            ("Operations Intern",        "📦", "Logistics, process support & coordination",  "INT",  "intern"),
            ("Strategy Intern",          "💡", "Research, slide decks & market analysis",    "INT",  "intern"),
        ],
    },
    "engineering": {
        "label": "Engineering",
        "icon": "⚙️",
        "color": "rgba(251,146,60,.08)",
        "accent": "#fb923c",
        "roles": [
            ("Mechanical Engineer",      "🔧", "Design, thermodynamics & manufacturing",     "ME",   "pro"),
            ("Civil Engineer",           "🏗️", "Structures, surveying & project delivery",  "CE",   "pro"),
            ("Electrical Engineer",      "⚡", "Power systems, circuits & automation",       "EE",   "pro"),
            ("Chemical Engineer",        "🧪", "Process design, safety & optimisation",      "CHE",  "pro"),
            ("Industrial Engineer",      "🏭", "Lean, process improvement & ergonomics",     "IE",   "pro"),
            ("Engineering Intern",       "🔩", "CAD basics, lab work & technical support",   "INT",  "intern"),
            ("Civil Engineering Intern", "📐", "Site surveys, drawings & calculations",      "INT",  "intern"),
            ("Electrical Intern",        "🔌", "Circuit basics, testing & documentation",    "INT",  "intern"),
        ],
    },
}

ROLE_IMAGES = {
    "Software Developer":          "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=400&h=180&fit=crop&auto=format",
    "SQA Engineer":                "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400&h=180&fit=crop&auto=format",
    "DevOps Engineer":             "https://images.unsplash.com/photo-1667372393119-3d4c48d07fc9?w=400&h=180&fit=crop&auto=format",
    "UI/UX Designer":              "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=180&fit=crop&auto=format",
    "Data Scientist":              "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=180&fit=crop&auto=format",
    "Cybersecurity Analyst":       "https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=400&h=180&fit=crop&auto=format",
    "Cloud Architect":             "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=400&h=180&fit=crop&auto=format",
    "Mobile App Developer":        "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=400&h=180&fit=crop&auto=format",
    "Software Engineering Intern": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400&h=180&fit=crop&auto=format",
    "QA Intern":                   "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=400&h=180&fit=crop&auto=format",
    "UI/UX Design Intern":         "https://images.unsplash.com/photo-1587440871875-191322ee64b0?w=400&h=180&fit=crop&auto=format",
    "Data Science Intern":         "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=180&fit=crop&auto=format",
    "IT Support Intern":           "https://images.unsplash.com/photo-1588702547919-26089e690ecc?w=400&h=180&fit=crop&auto=format",
    "Cybersecurity Intern":        "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=400&h=180&fit=crop&auto=format",
    "HR Manager":                  "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=400&h=180&fit=crop&auto=format",
    "Talent Acquisition Lead":     "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=400&h=180&fit=crop&auto=format",
    "L&D Specialist":              "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=400&h=180&fit=crop&auto=format",
    "Compensation & Benefits":     "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=400&h=180&fit=crop&auto=format",
    "HR Business Partner":         "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?w=400&h=180&fit=crop&auto=format",
    "Employee Relations Mgr":      "https://images.unsplash.com/photo-1582213782179-e0d53f98f2ca?w=400&h=180&fit=crop&auto=format",
    "HR Intern":                   "https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?w=400&h=180&fit=crop&auto=format",
    "Recruitment Intern":          "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=180&fit=crop&auto=format",
    "L&D Intern":                  "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=400&h=180&fit=crop&auto=format",
    "Chartered Accountant":        "https://images.unsplash.com/photo-1554224154-26032ffc0d07?w=400&h=180&fit=crop&auto=format",
    "Financial Analyst":           "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400&h=180&fit=crop&auto=format",
    "Management Accountant":       "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=400&h=180&fit=crop&auto=format",
    "Audit & Assurance":           "https://images.unsplash.com/photo-1601597111158-2fceff292cdc?w=400&h=180&fit=crop&auto=format",
    "Tax Consultant":              "https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=400&h=180&fit=crop&auto=format",
    "CFO / Finance Director":      "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=400&h=180&fit=crop&auto=format",
    "Accounting Intern":           "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=400&h=180&fit=crop&auto=format",
    "Finance Intern":              "https://images.unsplash.com/photo-1579621970795-87facc2f976d?w=400&h=180&fit=crop&auto=format",
    "Audit Intern":                "https://images.unsplash.com/photo-1542621334-a254cf47733d?w=400&h=180&fit=crop&auto=format",
    "Digital Marketing Manager":   "https://images.unsplash.com/photo-1432888622747-4eb9a8efeb07?w=400&h=180&fit=crop&auto=format",
    "Brand Strategist":            "https://images.unsplash.com/photo-1493612276216-ee3925520721?w=400&h=180&fit=crop&auto=format",
    "Content Marketing Lead":      "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=400&h=180&fit=crop&auto=format",
    "Social Media Manager":        "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=400&h=180&fit=crop&auto=format",
    "PR & Communications":         "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=400&h=180&fit=crop&auto=format",
    "Marketing Intern":            "https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=180&fit=crop&auto=format",
    "Content Creation Intern":     "https://images.unsplash.com/photo-1504691342899-4d92b50853e1?w=400&h=180&fit=crop&auto=format",
    "Social Media Intern":         "https://images.unsplash.com/photo-1516251193007-45ef944ab0c6?w=400&h=180&fit=crop&auto=format",
    "Product Manager":             "https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=400&h=180&fit=crop&auto=format",
    "Project Manager":             "https://images.unsplash.com/photo-1572021335469-31706a17aaef?w=400&h=180&fit=crop&auto=format",
    "Business Analyst":            "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=180&fit=crop&auto=format",
    "Operations Manager":          "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=400&h=180&fit=crop&auto=format",
    "Strategy Consultant":         "https://images.unsplash.com/photo-1553877522-43269d4ea984?w=400&h=180&fit=crop&auto=format",
    "Entrepreneur / Founder":      "https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=400&h=180&fit=crop&auto=format",
    "Business Analyst Intern":     "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=400&h=180&fit=crop&auto=format",
    "Operations Intern":           "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=400&h=180&fit=crop&auto=format",
    "Strategy Intern":             "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=400&h=180&fit=crop&auto=format",
    "Mechanical Engineer":         "https://images.unsplash.com/photo-1537462715879-360eeb61a0ad?w=400&h=180&fit=crop&auto=format",
    "Civil Engineer":              "https://images.unsplash.com/photo-1503387762-592deb58ef4e?w=400&h=180&fit=crop&auto=format",
    "Electrical Engineer":         "https://images.unsplash.com/photo-1620283085068-5f0be3b3ee5b?w=400&h=180&fit=crop&auto=format",
    "Chemical Engineer":           "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=400&h=180&fit=crop&auto=format",
    "Industrial Engineer":         "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400&h=180&fit=crop&auto=format",
    "Engineering Intern":          "https://images.unsplash.com/photo-1581092921461-eab62e97a780?w=400&h=180&fit=crop&auto=format",
    "Civil Engineering Intern":    "https://images.unsplash.com/photo-1590725121839-892b458a74fe?w=400&h=180&fit=crop&auto=format",
    "Electrical Intern":           "https://images.unsplash.com/photo-1621905251918-48416bd8575a?w=400&h=180&fit=crop&auto=format",
}

DEFAULT_IMAGE = "https://images.unsplash.com/photo-1497366216548-37526070297c?w=400&h=180&fit=crop&auto=format"

def get_role_image(role: str) -> str:
    return ROLE_IMAGES.get(role, DEFAULT_IMAGE)

def get_field_context(role: str) -> str:
    for fdata in FIELDS.values():
        for r in fdata["roles"]:
            if r[0] == role:
                return fdata["label"]
    return "General"

def is_intern_role(role: str) -> bool:
    for fdata in FIELDS.values():
        for r in fdata["roles"]:
            if r[0] == role:
                return r[4] == "intern"
    return "Intern" in role


# PAGES


def page_login():
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        render_logo_large()

        st.markdown('<div class="login-card">', unsafe_allow_html=True)

        tab_in, tab_up = st.tabs(["  Sign In  ", "  Create Account  "])

        with tab_in:
            st.markdown("<br>", unsafe_allow_html=True)
            user = st.text_input("Username", key="li_u", placeholder="your username")
            pw   = st.text_input("Password", type="password", key="li_p", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In →", type="primary", use_container_width=True):
                if not user.strip():
                    st.warning("Please enter your username.")
                elif verify_user(user.strip(), pw):
                    st.session_state.logged_in = True
                    st.session_state.username  = user.strip()
                    goto("dashboard"); st.rerun()
                else:
                    st.error("Credentials not recognised. Please try again.")

        with tab_up:
            st.markdown("<br>", unsafe_allow_html=True)
            nu = st.text_input("Choose a username", key="ru")
            np = st.text_input("Password",          type="password", key="rp1")
            nc = st.text_input("Confirm password",  type="password", key="rp2")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account →", type="primary", use_container_width=True):
                if not nu.strip() or not np:
                    st.warning("All fields are required.")
                elif np != nc:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = register_user(nu.strip(), np)
                    if ok:
                        st.success(f"✅ {msg} Sign in as **{nu.strip()}**.")
                    else:
                        st.error(msg)

        st.markdown('</div>', unsafe_allow_html=True)


def page_dashboard():
    h = st.session_state.score_history
    avg  = round(sum(h)/len(h), 1) if h else "—"
    best = max(h) if h else "—"
    last = h[-1]    if h else "—"

    st.markdown(f"""
    <div class="page-enter">
      <div class="section-eyebrow">Dashboard</div>
      <div class="section-heading">Good day, {st.session_state.username}.</div>
      <div class="section-sub">Select a discipline below to begin your AI-coached practice session.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi-chip"><div class="dot"></div>Sessions <span class="val">{len(h)}</span></div>
      <div class="kpi-chip"><div class="dot"></div>Average <span class="val">{avg}/10</span></div>
      <div class="kpi-chip"><div class="dot"></div>Best <span class="val">{best}/10</span></div>
      <div class="kpi-chip"><div class="dot"></div>Latest <span class="val">{last}/10</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    FIELD_KEYS  = list(FIELDS.keys())
    FIELD_TABS  = [f"  {FIELDS[k]['icon']}  {FIELDS[k]['label']}  " for k in FIELD_KEYS]

    if "active_field" not in st.session_state:
        st.session_state.active_field = FIELD_KEYS[0]

    field_tabs = st.tabs(FIELD_TABS)

    def _render_field(fkey, tab_obj):
        fdata = FIELDS[fkey]
        accent = fdata["accent"]
        pro_roles    = [r for r in fdata["roles"] if r[4] == "pro"]
        intern_roles = [r for r in fdata["roles"] if r[4] == "intern"]

        with tab_obj:
            if pro_roles:
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;margin:14px 0 12px;">
                  <span style="font-size:.7rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:{accent};">
                    💼 Professional
                  </span>
                  <div style="flex:1;height:1px;background:var(--c-border);"></div>
                </div>""", unsafe_allow_html=True)
                # Responsive: 3 cols on desktop, 2 on tablet, 1 on mobile
                cols = st.columns(3)
                for i, (role, icon, desc, badge, _) in enumerate(pro_roles):
                    with cols[i % 3]:
                        img = get_role_image(role)
                        st.markdown(f"""
                        <div class="role-card">
                          <div class="rc-img-wrap">
                            <img src="{img}" alt="{role}" loading="lazy">
                          </div>
                          <span class="rc-badge" style="border-color:{accent}33;color:{accent};">{badge}</span>
                          <div class="rc-body">
                            <div class="rc-title">{role}</div>
                            <div class="rc-desc">{desc}</div>
                          </div>
                        </div>""", unsafe_allow_html=True)
                        if st.button("Practice", key=f"p_{fkey}_{role}", use_container_width=True):
                            start_practice(role); st.rerun()

            if intern_roles:
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;margin:22px 0 12px;">
                  <span style="font-size:.7rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#34d399;">
                    🎓 Internship
                  </span>
                  <div style="flex:1;height:1px;background:var(--c-border);"></div>
                  <span style="
                    background:rgba(52,211,153,.1);border:1px solid rgba(52,211,153,.25);
                    border-radius:99px;padding:2px 10px;font-size:.68rem;font-weight:600;
                    color:#34d399;letter-spacing:.05em;">Intern Friendly</span>
                </div>""", unsafe_allow_html=True)
                cols = st.columns(3)
                for i, (role, icon, desc, badge, _) in enumerate(intern_roles):
                    with cols[i % 3]:
                        img = get_role_image(role)
                        st.markdown(f"""
                        <div class="role-card" style="border-color:rgba(52,211,153,.15);">
                          <div class="rc-img-wrap">
                            <img src="{img}" alt="{role}" loading="lazy">
                          </div>
                          <span class="rc-badge" style="border-color:rgba(52,211,153,.3);color:#34d399;">{badge}</span>
                          <div class="rc-body">
                            <div class="rc-title">{role}</div>
                            <div class="rc-desc">{desc}</div>
                          </div>
                        </div>""", unsafe_allow_html=True)
                        if st.button("Practice", key=f"i_{fkey}_{role}", use_container_width=True):
                            start_practice(role); st.rerun()

    for fkey, tab_obj in zip(FIELD_KEYS, field_tabs):
        _render_field(fkey, tab_obj)

    if len(h) >= 2:
        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-eyebrow">Performance</div>', unsafe_allow_html=True)
        fig = make_progress_chart(h)
        if fig: st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    if st.session_state.attempt_log:
        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-eyebrow">Recent Sessions</div>', unsafe_allow_html=True)
        st.markdown('<div style="background:var(--c-surface);border:1px solid var(--c-border);border-radius:var(--radius-md);padding:18px 22px;overflow-x:auto;">', unsafe_allow_html=True)
        st.markdown("""
        <div class="log-row" style="color:var(--c-text3);font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;border-bottom:1px solid var(--c-border2);padding-bottom:8px;">
          <div>Role</div><div>Question</div><div>Score</div><div>Time</div>
        </div>""", unsafe_allow_html=True)
        for log in reversed(st.session_state.attempt_log[-8:]):
            sc = log["score"]
            clr = score_color(sc)
            q_short = log["question"][:65] + "…" if len(log["question"]) > 65 else log["question"]
            st.markdown(f"""
            <div class="log-row">
              <div><span class="log-role-chip">{log['role']}</span></div>
              <div class="log-q">{q_short}</div>
              <div class="log-score" style="color:{clr};">{sc}/10</div>
              <div class="log-time">{log['time']}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def page_interview():
    role         = st.session_state.selected_role
    persona_name = st.session_state.get("interviewer_persona", "Sarah  ·  Female / US")
    p            = INTERVIEWER_PERSONAS.get(persona_name, list(INTERVIEWER_PERSONAS.values())[0])
    first_name   = persona_name.split()[0].strip()

    hc1, hc2 = st.columns([6, 2])
    with hc1:
        st.markdown(f"""
        <div class="iv-header">
          <span style="font-size:1.5rem;font-family:'Playfair Display',serif;font-weight:700;">Practice Session</span>
          <span class="iv-role-badge">{role}</span>
        </div>""", unsafe_allow_html=True)
    with hc2:
        c_exit, c_new = st.columns(2)
        with c_exit:
            if st.button("← Exit", use_container_width=True):
                goto("dashboard"); st.rerun()
        with c_new:
            if st.button("↻ New Q", use_container_width=True):
                with st.spinner("Generating…"):
                    st.session_state.current_q = ai_question(role)
                st.session_state.last_feedback   = ""
                st.session_state.last_script     = ""
                st.session_state.last_audio_key  = ""
                st.session_state.q_generated_at  = datetime.now()
                if st.session_state.get("interview_stage", 0) < 2:
                    st.session_state.interview_stage = 2
                st.rerun()

    # On mobile, interviewer panel goes above Q panel (single column stacks)
    col_iv, col_qa = st.columns([1, 3])

    with col_iv:
        personas = list(INTERVIEWER_PERSONAS.keys())
        chosen = st.selectbox(
            "🎭 Choose Interviewer",
            personas,
            index=personas.index(persona_name),
            key="persona_select",
        )
        if chosen != persona_name:
            st.session_state.interviewer_persona = chosen
            st.session_state.last_script = ""
            st.rerun()

        p_chosen   = INTERVIEWER_PERSONAS[chosen]
        clr        = p_chosen["color"]
        first      = chosen.split()[0].strip()
        accent_parts = clr.lstrip("#")
        r_val = int(accent_parts[0:2], 16)
        g_val = int(accent_parts[2:4], 16)
        b_val = int(accent_parts[4:6], 16)

        is_speaking = bool(st.session_state.get("last_script", ""))

        st.markdown(f"""<style>
          @keyframes wb_{first}{{0%,100%{{height:5px}}50%{{height:22px}}}}
          .wb_{first}{{display:inline-block;width:4px;border-radius:99px;
            background:{clr};animation:wb_{first} .75s ease infinite;}}
          .wb_{first}:nth-child(2){{animation-delay:.1s}}
          .wb_{first}:nth-child(3){{animation-delay:.2s}}
          .wb_{first}:nth-child(4){{animation-delay:.3s}}
          .wb_{first}:nth-child(5){{animation-delay:.12s}}
          @keyframes pulse_{first}{{
            0%{{box-shadow:0 0 0 0 rgba({r_val},{g_val},{b_val},.45)}}
            70%{{box-shadow:0 0 0 14px rgba({r_val},{g_val},{b_val},0)}}
            100%{{box-shadow:0 0 0 0 rgba({r_val},{g_val},{b_val},0)}}
          }}
          .av-pulse_{first}{{animation:pulse_{first} 1.5s ease infinite;}}
        </style>""", unsafe_allow_html=True)

        wave = ""
        if is_speaking:
            wave = f"""<div style="display:flex;align-items:center;justify-content:center;gap:3px;height:28px;margin:10px 0 4px;">
              <span class="wb_{first}" style="height:8px;"></span>
              <span class="wb_{first}" style="height:16px;"></span>
              <span class="wb_{first}" style="height:22px;"></span>
              <span class="wb_{first}" style="height:16px;"></span>
              <span class="wb_{first}" style="height:8px;"></span>
            </div>"""

        status_label = "🔴&nbsp; SPEAKING" if is_speaking else "⬤&nbsp; READY"
        avatar_cls   = f"av-pulse_{first}" if is_speaking else ""
        accent_label = chosen.split("·")[1].strip() if "·" in chosen else ""

        st.markdown(f"""
        <div style="
          text-align:center;
          background:var(--c-surface);
          border:1.5px solid {clr}50;
          border-radius:var(--radius-md);
          padding:22px 14px 18px;
          box-shadow:0 4px 20px rgba(0,0,0,.3);
        ">
          <div class="{avatar_cls}" style="
            font-size:2.8rem;width:74px;height:74px;
            background:{clr}18;border:2px solid {clr}70;
            border-radius:50%;display:flex;align-items:center;justify-content:center;
            margin:0 auto 12px;">
            {p_chosen['avatar']}
          </div>
          <div style="font-weight:700;font-size:.95rem;color:var(--c-text);letter-spacing:.01em;">{first}</div>
          <div style="font-size:.73rem;color:var(--c-text3);margin-top:3px;">{accent_label}</div>
          {wave}
          <div style="
            margin-top:12px;font-size:.68rem;padding:4px 12px;
            background:{clr}18;border:1px solid {clr}35;border-radius:99px;
            color:{clr};font-weight:700;letter-spacing:.06em;display:inline-block;">
            {status_label}
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        stage = st.session_state.get("interview_stage", 0)
        if stage == 0:
            btn_label = f"🎙  {first}  ·  Start Interview"
        elif stage == 1:
            btn_label = f"🎙  {first}  ·  Ask First Question"
        else:
            btn_label = f"🎙  {first}  ·  Next Question"

        if st.button(btn_label, type="primary", use_container_width=True, key="btn_ask"):
            script = play_interviewer_speech(role, chosen)
            st.session_state.last_script = script
            if stage == 0:
                st.session_state.interview_stage = 1
            elif stage == 1:
                st.session_state.interview_stage = 2

        if st.session_state.get("last_audio_key") and st.session_state["last_audio_key"] in st.session_state:
            _render_audio(st.session_state[st.session_state["last_audio_key"]])

        if st.session_state.get("last_script"):
            if st.button("🔁  Replay Voice", use_container_width=True, key="btn_replay"):
                cache_key = f"_audio_{hash(st.session_state.last_script + chosen)}"
                if cache_key in st.session_state:
                    _render_audio(st.session_state[cache_key])
                else:
                    tts_play(st.session_state.last_script, lang=p_chosen["lang"], tld=p_chosen["tld"])

        if st.session_state.get("last_script"):
            st.markdown(f"""
            <div style="
              margin-top:14px;
              background:var(--c-surface2);
              border:1px solid {clr}30;
              border-left:3px solid {clr};
              border-radius:0 var(--radius-sm) var(--radius-sm) 0;
              padding:12px 14px;
              font-size:.78rem;
              color:var(--c-text2);
              font-style:italic;
              line-height:1.65;
            ">
              <div style="font-size:.66rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
                           color:{clr};margin-bottom:6px;">💬 {first} said</div>
              "{st.session_state.last_script}"
            </div>""", unsafe_allow_html=True)

    with col_qa:
        q = st.session_state.current_q
        gen_time  = st.session_state.q_generated_at
        gen_label = gen_time.strftime("%H:%M") if gen_time else ""
        stage     = st.session_state.get("interview_stage", 0)

        if stage == 0:
            cname_input = st.text_input(
                "Your Name (so the interviewer can address you naturally)",
                value=st.session_state.get("candidate_name", ""),
                placeholder="e.g. Kasun, Nimasha…",
                key="cname_input",
            )
            if cname_input.strip():
                st.session_state.candidate_name = cname_input.strip().capitalize()

            st.markdown(f"""
            <div class="q-block" style="border-left-color:#34d399; margin-top:14px;">
              <div class="q-label" style="color:#34d399;">Ready to Begin</div>
              <div class="q-text" style="font-size:.98rem; font-weight:400; color:var(--c-text2); line-height:1.8;">
                Click <strong style="color:var(--c-text);">"Start Interview"</strong> on the left.<br><br>
                {first_name} will greet you and ask <em>"Tell me about yourself"</em> — just like a real interview.
                Type or speak your answer, then click <strong style="color:var(--c-text);">"Ask First Question"</strong>
                to move to your first technical question.
              </div>
            </div>
            <div class="tip-callout" style="margin-top:12px;">
              <b>💡 How to answer "Tell me about yourself"</b><br>
              State your <b>name → background → key skills → why this role → enthusiasm</b>.
              Keep it under 90 seconds. Be confident and natural.
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="q-block">
              <div class="q-label">Question {max(stage-1,1)} · {role}</div>
              <div class="q-text">{q}</div>
              <div class="q-meta">{gen_label} · {first_name}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

        if stage == 0:
            st.markdown(f"""
            <div class="tip-callout" style="margin-top:16px;">
              <b>How the interview works</b><br>
              1. Enter your name above so {first_name} can address you naturally.<br>
              2. Click <b>Start Interview</b> — {first_name} introduces themselves.<br>
              3. Answer "Tell me about yourself" → click <b>Evaluate</b> to get feedback + tips.<br>
              4. Click <b>Ask First Question</b> → technical questions begin.<br>
              5. Each <b>Next Question</b> flows naturally — no repeated introductions.
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="section-eyebrow" style="margin-bottom:14px;">Your Response</div>', unsafe_allow_html=True)

        def _run_eval(answer_text):
            with st.spinner("Analysing your response…"):
                fb = ai_evaluate(q, answer_text, role)
                st.session_state.last_feedback = fb
                sc = extract_score(fb)
                if sc is not None:
                    st.session_state.score_history.append(sc)
                    st.session_state.attempt_log.append({
                        "role": role, "question": q,
                        "answer": answer_text[:120], "score": sc,
                        "time": datetime.now().strftime("%H:%M"),
                    })
            st.rerun()

        if stage > 0:
            tab_type, tab_mic = st.tabs(["  ✍  Type Answer  ", "  🎙  Speak Answer  "])

            with tab_type:
                ans = st.text_area(
                    "Write your answer",
                    height=180, key="typed_ans",
                    placeholder="Provide a detailed, structured answer. Aim for 150–250 words…",
                )
                if st.button("Evaluate Answer →", type="primary", use_container_width=True, key="ev_t"):
                    if ans.strip():
                        _run_eval(ans.strip())
                    else:
                        st.warning("Please write your answer before evaluating.")

            with tab_mic:
                c_rec, c_tip = st.columns([5, 7])
                with c_rec:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("⬤  Start Recording", type="primary", use_container_width=True, key="ev_m"):
                        with st.spinner("Listening — speak clearly…"):
                            transcript = record_mic(timeout=14)
                        if transcript:
                            st.success(f"Captured: *{transcript[:80]}{'…' if len(transcript)>80 else ''}*")
                            _run_eval(transcript)
                        else:
                            st.error("No speech detected. Check your microphone and try again.")
                with c_tip:
                    st.markdown("""
                    <div class="tip-callout" style="margin-top:14px;">
                      <b>Tips for a strong recording</b><br>
                      Speak at a measured pace · Minimise background noise ·
                      Aim for 60–90 seconds · Use the SAR method
                      (Situation → Action → Result).
                    </div>""", unsafe_allow_html=True)

        if st.session_state.last_feedback:
            st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
            st.markdown('<div class="section-eyebrow" style="margin-bottom:14px;">Performance Report</div>', unsafe_allow_html=True)
            sc = extract_score(st.session_state.last_feedback)
            if sc is not None:
                c_gauge, c_fb = st.columns([1, 3])
                with c_gauge:
                    st.plotly_chart(make_gauge(sc), use_container_width=True,
                                    config={"displayModeBar": False})
                    clr_sc = score_color(sc)
                    pct    = sc * 10
                    st.markdown(f"""
                    <div class="score-badge">
                      <div class="sb-bar"><div class="sb-fill" style="width:{pct}%;background:{clr_sc};"></div></div>
                      <div class="sb-label">{sc}/10 Overall</div>
                    </div>""", unsafe_allow_html=True)
                with c_fb:
                    st.markdown(f'<div class="fb-card">{st.session_state.last_feedback}</div>',
                                unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="fb-card">{st.session_state.last_feedback}</div>',
                            unsafe_allow_html=True)


def page_stats():
    if st.button("← Dashboard"):
        goto("dashboard"); st.rerun()

    st.markdown("""
    <div class="section-eyebrow">Analytics</div>
    <div class="section-heading">Your Performance</div>
    """, unsafe_allow_html=True)

    h = st.session_state.score_history
    if not h:
        st.info("Complete at least one session to see your analytics.")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sessions",   len(h))
    c2.metric("Average",    f"{round(sum(h)/len(h),1)}/10")
    c3.metric("Peak Score", f"{max(h)}/10")
    c4.metric("Latest",     f"{h[-1]}/10")

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    if len(h) >= 2:
        fig = make_progress_chart(h)
        if fig:
            st.markdown('<div class="section-eyebrow">Score Trajectory</div>', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="section-eyebrow" style="margin-top:20px;">Score Distribution</div>', unsafe_allow_html=True)
    st.plotly_chart(make_dist_chart(h), use_container_width=True, config={"displayModeBar": False})


# SIDEBAR

def render_sidebar():
    with st.sidebar:
        uname   = st.session_state.username
        initial = uname[0].upper() if uname else "?"

        render_logo_sidebar()

        st.markdown(f"""
        <div style="border-top:1px solid var(--c-border);margin-bottom:14px;"></div>
        <div class="sb-user">
          <div class="sb-avatar">{initial}</div>
          <div>
            <div class="sb-user-name">{uname}</div>
            <div class="sb-user-sub">Active session</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        pages = [("dashboard","🏠  Dashboard"), ("stats","📈  Analytics")]
        for pg, label in pages:
            if st.button(label, key=f"nav_{pg}", use_container_width=True):
                goto(pg); st.rerun()

        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

        h = st.session_state.score_history
        if h:
            st.plotly_chart(make_gauge(h[-1]), use_container_width=True,
                            config={"displayModeBar": False})
            st.markdown(f"""
            <div style='text-align:center;font-size:.75rem;color:var(--c-text3);
                        font-family:"DM Mono",monospace; margin-top:-8px;'>
              {len(h)} session{"s" if len(h)!=1 else ""}  ·  avg {round(sum(h)/len(h),1)}/10
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='text-align:center;color:var(--c-text3);font-size:.82rem;padding:16px 0;'>
              No sessions yet.<br>Start practising to see your score.
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True):
            for k, v in _D.items():
                st.session_state[k] = v
            st.rerun()


# ROUTER

if not st.session_state.logged_in:
    page_login()
else:
    render_sidebar()
    pg = st.session_state.page
    if   pg == "interview": page_interview()
    elif pg == "stats":     page_stats()
    else:                   page_dashboard()
