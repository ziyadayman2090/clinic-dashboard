import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta, date

st.set_page_config(
    page_title="AL-Basma Clinic",
    page_icon="🏥",
    layout="wide",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

    :root {
        --bg:        #0B0F1A;
        --panel:     #111827;
        --panel2:    #161D2E;
        --border:    rgba(99,179,237,0.12);
        --border2:   rgba(99,179,237,0.22);
        --teal:      #00D4C8;
        --blue:      #3B82F6;
        --purple:    #8B5CF6;
        --pink:      #EC4899;
        --amber:     #F59E0B;
        --red:       #EF4444;
        --green:     #10B981;
        --text:      #E2E8F0;
        --muted:     #64748B;
        --dim:       #94A3B8;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: var(--bg) !important;
        font-family: 'Inter', sans-serif !important;
        color: var(--text) !important;
    }

    [data-testid="stSidebar"] {
        background: #0A0E18 !important;
        border-right: 1px solid var(--border) !important;
    }
    [data-testid="stSidebar"] * { color: #94A3B8 !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #00D4C8 !important; font-size: 11px !important; font-weight: 600 !important;
        letter-spacing: 2px !important; text-transform: uppercase !important;
    }
    [data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
        color: #64748B !important; font-size: 10px !important; letter-spacing: 1px !important;
        text-transform: uppercase !important;
    }

    .main .block-container { padding: 1rem 1.5rem !important; max-width: 100% !important; }

    h1, h2, h3 { color: var(--text) !important; font-family: 'Rajdhani', sans-serif !important; }

    .dash-header {
        display: flex; align-items: center; gap: 14px;
        padding: 10px 0 14px;
        border-bottom: 1px solid var(--border);
        margin-bottom: 16px;
    }
    .dash-logo {
        font-family: 'Rajdhani', sans-serif;
        font-size: 20px; font-weight: 700;
        color: var(--teal); letter-spacing: 2px; text-transform: uppercase;
    }
    .dash-sub { font-size: 11px; color: var(--muted); letter-spacing: 1px; text-transform: uppercase; }
    .dash-live {
        margin-left: auto; display: flex; align-items: center; gap: 6px;
        font-size: 10px; color: var(--teal); letter-spacing: 1px; text-transform: uppercase;
    }
    .live-dot {
        width: 6px; height: 6px; border-radius: 50%; background: var(--teal);
        box-shadow: 0 0 6px var(--teal); animation: pulse 1.8s infinite;
    }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
    .dash-date { font-size: 11px; color: var(--dim); letter-spacing: 0.5px; }

    .kpi-row { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-bottom: 14px; }
    .kpi-card {
        background: var(--panel); border: 1px solid var(--border);
        border-radius: 10px; padding: 14px 14px 12px;
        position: relative; overflow: hidden;
    }
    .kpi-card::before {
        content: ''; position: absolute;
        top: 0; left: 0; right: 0; height: 2px;
    }
    .kpi-card.c-teal::before   { background: var(--teal);   box-shadow: 0 0 8px var(--teal); }
    .kpi-card.c-amber::before  { background: var(--amber);  box-shadow: 0 0 8px var(--amber); }
    .kpi-card.c-green::before  { background: var(--green);  box-shadow: 0 0 8px var(--green); }
    .kpi-card.c-red::before    { background: var(--red);    box-shadow: 0 0 8px var(--red); }
    .kpi-card.c-purple::before { background: var(--purple); box-shadow: 0 0 8px var(--purple); }

    .kpi-label { font-size: 9px; font-weight: 600; letter-spacing: 1.8px; text-transform: uppercase; color: var(--muted); margin-bottom: 8px; }
    .kpi-value { font-family: 'Rajdhani', sans-serif; font-size: 38px; font-weight: 700; line-height: 1; margin-bottom: 4px; }
    .kpi-card.c-teal   .kpi-value { color: var(--teal); }
    .kpi-card.c-amber  .kpi-value { color: var(--amber); }
    .kpi-card.c-green  .kpi-value { color: var(--green); }
    .kpi-card.c-red    .kpi-value { color: var(--red); }
    .kpi-card.c-purple .kpi-value { color: var(--purple); }
    .kpi-sub  { font-size: 10px; color: var(--muted); }
    .kpi-rate {
        position: absolute; top: 14px; right: 12px;
        font-size: 10px; font-weight: 600; padding: 2px 7px; border-radius: 20px;
    }
    .kpi-card.c-teal   .kpi-rate { background: rgba(0,212,200,0.12);  color: var(--teal); }
    .kpi-card.c-amber  .kpi-rate { background: rgba(245,158,11,0.12); color: var(--amber); }
    .kpi-card.c-green  .kpi-rate { background: rgba(16,185,129,0.12); color: var(--green); }
    .kpi-card.c-red    .kpi-rate { background: rgba(239,68,68,0.12);  color: var(--red); }
    .kpi-card.c-purple .kpi-rate { background: rgba(139,92,246,0.12); color: var(--purple); }

    .panel {
        background: var(--panel); border: 1px solid var(--border);
        border-radius: 10px; padding: 16px; margin-bottom: 12px;
    }
    .panel-title { font-family: 'Rajdhani', sans-serif; font-size: 13px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: var(--dim); margin-bottom: 4px; }
    .panel-sub   { font-size: 10px; color: var(--muted); margin-bottom: 14px; letter-spacing: 0.5px; }

    .plat-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin-bottom: 14px; }
    .plat-card { border-radius: 10px; padding: 16px 14px 12px; position: relative; overflow: hidden; border: 1px solid rgba(255,255,255,0.06); }
    .plat-card::after { content: ''; position: absolute; bottom: -20px; right: -20px; width: 60px; height: 60px; border-radius: 50%; background: rgba(255,255,255,0.05); }
    .plat-label { font-size: 9px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; opacity: 0.75; margin-bottom: 6px; color: white; }
    .plat-value { font-family: 'Rajdhani', sans-serif; font-size: 32px; font-weight: 700; color: white; line-height: 1; }
    .plat-sub   { font-size: 10px; opacity: 0.6; color: white; margin-top: 3px; }

    .plat-hero {
        border-radius: 10px; padding: 20px 24px;
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 14px; border: 1px solid rgba(255,255,255,0.07);
    }
    .plat-hero-lbl  { font-size: 10px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: rgba(255,255,255,0.65); margin-bottom: 6px; }
    .plat-hero-val  { font-family: 'Rajdhani', sans-serif; font-size: 56px; font-weight: 700; color: white; line-height: 1; }
    .plat-hero-sub  { font-size: 12px; color: rgba(255,255,255,0.55); margin-top: 4px; }
    .plat-hero-rate .plat-hero-lbl { text-align: right; }
    .plat-hero-rate .plat-hero-val { font-size: 44px; }

    .metric-grid-4 { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin-bottom: 14px; }
    .metric-mini { background: var(--panel2); border: 1px solid var(--border); border-radius: 10px; padding: 14px 12px; text-align: center; }
    .metric-mini-lbl { font-size: 9px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; color: var(--muted); margin-bottom: 6px; }
    .metric-mini-val { font-family: 'Rajdhani', sans-serif; font-size: 28px; font-weight: 700; line-height: 1; }

    .stSelectbox label { font-size: 10px !important; color: var(--muted) !important; font-weight: 600 !important; letter-spacing: 1.5px !important; text-transform: uppercase !important; }
    .stSelectbox > div > div { background: var(--panel2) !important; border-color: var(--border2) !important; color: var(--text) !important; border-radius: 8px !important; }

    hr { border-color: var(--border) !important; margin: 16px 0 !important; }
    .vega-embed { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ── Data ─────────────────────────────────────────────────────
GOOGLE_SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vTbn8mE8Z8QSRfb73Lk63htHUK31I59W5ZDaDTb81dtVK0Q61tczvnfGgGVQMYndidyxG8IdKuuVZ4o/"
    "pub?gid=551101663&single=true&output=csv"
)

def safe_sum_per_row(df, cols):
    existing = [c for c in cols if c in df.columns]
    if not existing:
        return 0
    return df[existing].sum(axis=1)

def safe_col_sum(df, col_name):
    return int(df[col_name].sum()) if col_name in df.columns else 0

@st.cache_data(ttl=5)
def load_data():
    df = pd.read_csv(GOOGLE_SHEET_CSV_URL)
    if "Date" not in df.columns:
        raise ValueError("Column 'Date' not found.")
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date"]).sort_values("Date")
    df["total_interactions"]   = safe_sum_per_row(df, ["Total Calls Received","WhatsApp Answered","Instagram Answered","TikTok Answered"])
    df["total_new_bookings"]   = safe_sum_per_row(df, ["New Bookings - Insta","New Bookings - Call","New Bookings - Whats","New Bookings - TikTok"])
    df["total_interested"]     = safe_sum_per_row(df, ["Interested - Insta","Interested - Whats","Interested - TikTok"])
    df["total_not_interested"] = safe_sum_per_row(df, ["Not Interested - Insta","Not Interested - Whats","Not Interested - TikTok"])
    df["total_asked_dates"]    = safe_sum_per_row(df, ["Asked About Dates - Insta","Asked About Dates - Whats","Asked About Dates - TikTok"])
    df["total_no_reply"]       = safe_sum_per_row(df, ["Didn't Answer - Insta","Didn't Answer - Whats","Didn't Answer - TikTok","Didn't Answer - Call"])
    return df

df = load_data()
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏥 AL-BASMA")
    st.markdown("---")
    st.markdown("**FILTERS**")
    quick_range = st.radio("Quick Range", ["Today","Last 7 days","This month","All time"], index=2)
    today = max_date
    if quick_range == "Today":
        default_start = default_end = today
    elif quick_range == "Last 7 days":
        default_start = today - timedelta(days=6); default_end = today
    elif quick_range == "This month":
        default_start = today.replace(day=1); default_end = today
    else:
        default_start = min_date; default_end = max_date
    start_date = st.date_input("Start date", value=default_start, min_value=min_date, max_value=max_date)
    end_date   = st.date_input("End date",   value=default_end,   min_value=min_date, max_value=max_date)
    if start_date > end_date:
        st.warning("Auto-corrected date range.")
        start_date, end_date = end_date, start_date
    st.markdown("---")
    st.markdown(f"<small style='color:#334155'>Data: {min_date} → {max_date}</small>", unsafe_allow_html=True)

mask = (df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date)
df_filtered = df.loc[mask].copy()
if df_filtered.empty:
    st.warning("No data in selected range.")
    st.stop()

# ── Metrics ──────────────────────────────────────────────────
total_interactions   = int(df_filtered["total_interactions"].sum())
total_new_bookings   = int(df_filtered["total_new_bookings"].sum())
total_interested     = int(df_filtered["total_interested"].sum())
total_not_interested = int(df_filtered["total_not_interested"].sum())
total_no_reply       = int(df_filtered["total_no_reply"].sum())
booking_rate = f"{total_new_bookings/total_interactions*100:.1f}%" if total_interactions else "—"

# ── Header ───────────────────────────────────────────────────
st.markdown(f"""
<div class="dash-header">
    <div>
        <div class="dash-logo">AL-Basma Clinic</div>
        <div class="dash-sub">Patient Engagement &amp; Booking Analytics</div>
    </div>
    <div class="dash-live"><div class="live-dot"></div>Live</div>
    <div class="dash-date">{start_date.strftime("%b %d")} – {end_date.strftime("%b %d, %Y")}</div>
</div>
""", unsafe_allow_html=True)

# ── KPI Row ──────────────────────────────────────────────────
st.markdown(f"""
<div class="kpi-row">
    <div class="kpi-card c-teal">
        <div class="kpi-rate">ALL CHANNELS</div>
        <div class="kpi-label">Total Interactions</div>
        <div class="kpi-value">{total_interactions:,}</div>
        <div class="kpi-sub">Insta · WhatsApp · TikTok · Calls</div>
    </div>
    <div class="kpi-card c-amber">
        <div class="kpi-rate">{booking_rate}</div>
        <div class="kpi-label">New Bookings</div>
        <div class="kpi-value">{total_new_bookings:,}</div>
        <div class="kpi-sub">Confirmed appointments</div>
    </div>
    <div class="kpi-card c-green">
        <div class="kpi-label">Interested</div>
        <div class="kpi-value">{total_interested:,}</div>
        <div class="kpi-sub">Warm potential clients</div>
    </div>
    <div class="kpi-card c-red">
        <div class="kpi-label">Not Interested</div>
        <div class="kpi-value">{total_not_interested:,}</div>
        <div class="kpi-sub">Declined offers</div>
    </div>
    <div class="kpi-card c-purple">
        <div class="kpi-label">No Response</div>
        <div class="kpi-value">{total_no_reply:,}</div>
        <div class="kpi-sub">Didn't answer</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
view = st.radio("", ["Overview", "Platforms", "Time Analysis"], horizontal=True)

# ── Dark Altair config ────────────────────────────────────────
DARK_CFG = {
    "background": "transparent",
    "view": {"stroke": "transparent"},
    "axis": {
        "domainColor": "#1E293B", "gridColor": "#1E293B",
        "labelColor": "#64748B", "tickColor": "transparent",
        "titleColor": "#64748B", "labelFontSize": 10,
    },
    "legend": {"labelColor": "#94A3B8", "titleColor": "#64748B", "labelFontSize": 10},
}

PLATFORM_COLS = {
    "Instagram": {"total":"Instagram Answered","bookings":"New Bookings - Insta","asked_dates":"Asked About Dates - Insta","interested":"Interested - Insta","not_interested":"Not Interested - Insta","no_reply":"Didn't Answer - Insta"},
    "WhatsApp":  {"total":"WhatsApp Answered","bookings":"New Bookings - Whats","asked_dates":"Asked About Dates - Whats","interested":"Interested - Whats","not_interested":"Not Interested - Whats","no_reply":"Didn't Answer - Whats"},
    "TikTok":    {"total":"TikTok Answered","bookings":"New Bookings - TikTok","asked_dates":"Asked About Dates - TikTok","interested":"Interested - TikTok","not_interested":"Not Interested - TikTok","no_reply":"Didn't Answer - TikTok"},
    "Calls":     {"total":"Total Calls Received","bookings":"New Bookings - Call","asked_dates":"Asked About Dates - Call","interested":"Interested - Call","not_interested":"Not Interested - Call","no_reply":"Didn't Answer - Call"},
}
PLATFORM_GRADIENTS = {
    "Instagram": "linear-gradient(135deg,#833ab4,#fd1d1d,#fcb045)",
    "WhatsApp":  "linear-gradient(135deg,#075E54,#25D366)",
    "TikTok":    "linear-gradient(135deg,#111,#EE1D52,#69C9D0)",
    "Calls":     "linear-gradient(135deg,#1D4ED8,#3B82F6)",
}
PLATFORM_COLORS = {"Instagram":"#C026D3","WhatsApp":"#10B981","TikTok":"#EE1D52","Calls":"#3B82F6"}

# ══════════════════════════════════════════
# OVERVIEW
# ══════════════════════════════════════════
if view == "Overview":
    col_trend, col_sent = st.columns([3, 2], gap="medium")

    with col_trend:
        st.markdown('<div class="panel"><div class="panel-title">Inquiry Trend</div><div class="panel-sub">Daily interactions vs bookings</div>', unsafe_allow_html=True)
        daily = df_filtered.groupby("Date")[["total_interactions","total_new_bookings"]].sum().reset_index()
        melted = daily.melt("Date", ["total_interactions","total_new_bookings"], var_name="Metric", value_name="Count")
        area = alt.Chart(daily).mark_area(opacity=0.08, color="#00D4C8").encode(x="Date:T", y="total_interactions:Q")
        line = alt.Chart(melted).mark_line(strokeWidth=2).encode(
            x=alt.X("Date:T", axis=alt.Axis(format="%b %d")),
            y="Count:Q",
            color=alt.Color("Metric:N", scale=alt.Scale(domain=["total_interactions","total_new_bookings"], range=["#00D4C8","#F59E0B"]), legend=alt.Legend(orient="top", title=None)),
            tooltip=["Date:T","Metric:N","Count:Q"],
        )
        st.altair_chart((area + line).properties(height=200).configure(**DARK_CFG), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_sent:
        st.markdown('<div class="panel"><div class="panel-title">Customer Sentiment</div><div class="panel-sub">Response distribution</div>', unsafe_allow_html=True)
        neg = int(df_filtered["total_not_interested"].sum())
        neu = int(df_filtered["total_asked_dates"].sum())
        pos = int(df_filtered["total_new_bookings"].sum() + df_filtered["total_interested"].sum())
        sent_df = pd.DataFrame({"Sentiment":["Positive","Neutral","Negative"],"Count":[pos,neu,neg]})
        donut = alt.Chart(sent_df).mark_arc(innerRadius=55, outerRadius=90, cornerRadius=3).encode(
            theta="Count:Q",
            color=alt.Color("Sentiment:N", scale=alt.Scale(domain=["Positive","Neutral","Negative"], range=["#10B981","#F59E0B","#EF4444"]), legend=alt.Legend(orient="bottom", title=None)),
            tooltip=["Sentiment:N","Count:Q"],
        )
        st.altair_chart(donut.properties(height=210).configure(**DARK_CFG), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    platform_cols_simple = {"Instagram":"Instagram Answered","WhatsApp":"WhatsApp Answered","TikTok":"TikTok Answered","Calls":"Total Calls Received"}
    book_cols = {"Instagram":"New Bookings - Insta","WhatsApp":"New Bookings - Whats","TikTok":"New Bookings - TikTok","Calls":"New Bookings - Call"}

    plat_html = '<div class="plat-grid">'
    for p, col in platform_cols_simple.items():
        val  = int(df_filtered[col].sum()) if col in df_filtered.columns else 0
        bval = int(df_filtered[book_cols[p]].sum()) if book_cols[p] in df_filtered.columns else 0
        rate = f"{bval/val*100:.0f}%" if val else "—"
        plat_html += f'<div class="plat-card" style="background:{PLATFORM_GRADIENTS[p]};"><div class="plat-label">{p}</div><div class="plat-value">{val:,}</div><div class="plat-sub">{bval:,} bookings · {rate} rate</div></div>'
    plat_html += '</div>'
    st.markdown(plat_html, unsafe_allow_html=True)

    col_b1, col_b2 = st.columns(2, gap="medium")
    with col_b1:
        st.markdown('<div class="panel"><div class="panel-title">Interactions by Platform</div><div class="panel-sub">All channels compared</div>', unsafe_allow_html=True)
        int_d = {p: df_filtered[c].sum() for p,c in platform_cols_simple.items() if c in df_filtered.columns}
        ib = alt.Chart(pd.DataFrame(list(int_d.items()), columns=["Platform","Count"])).mark_bar(cornerRadiusTopLeft=4,cornerRadiusTopRight=4).encode(
            x=alt.X("Platform:N",axis=alt.Axis(labelAngle=0)), y="Count:Q",
            color=alt.Color("Platform:N", scale=alt.Scale(domain=list(PLATFORM_COLORS.keys()),range=list(PLATFORM_COLORS.values())), legend=None),
            tooltip=["Platform:N","Count:Q"],
        )
        st.altair_chart(ib.properties(height=180).configure(**DARK_CFG), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b2:
        st.markdown('<div class="panel"><div class="panel-title">New Bookings by Platform</div><div class="panel-sub">Conversion by channel</div>', unsafe_allow_html=True)
        bk_d = {p: df_filtered[c].sum() for p,c in book_cols.items() if c in df_filtered.columns}
        bb = alt.Chart(pd.DataFrame(list(bk_d.items()), columns=["Platform","Count"])).mark_bar(cornerRadiusTopLeft=4,cornerRadiusTopRight=4).encode(
            x=alt.X("Platform:N",axis=alt.Axis(labelAngle=0)), y="Count:Q",
            color=alt.Color("Platform:N", scale=alt.Scale(domain=list(PLATFORM_COLORS.keys()),range=list(PLATFORM_COLORS.values())), legend=None),
            tooltip=["Platform:N","Count:Q"],
        )
        st.altair_chart(bb.properties(height=180).configure(**DARK_CFG), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════
# PLATFORMS
# ══════════════════════════════════════════
elif view == "Platforms":
    selected = st.selectbox("Platform:", ["Instagram","WhatsApp","TikTok","Calls"])
    cm = PLATFORM_COLS[selected]
    total_p = safe_col_sum(df_filtered, cm["total"])
    p_book  = safe_col_sum(df_filtered, cm["bookings"])
    p_asked = safe_col_sum(df_filtered, cm["asked_dates"])
    p_int   = safe_col_sum(df_filtered, cm["interested"])
    p_not   = safe_col_sum(df_filtered, cm["not_interested"])
    p_nr    = safe_col_sum(df_filtered, cm["no_reply"])
    p_rate  = f"{p_book/total_p*100:.1f}%" if total_p else "—"

    st.markdown(f"""
    <div class="plat-hero" style="background:{PLATFORM_GRADIENTS[selected]};">
        <div class="plat-hero-main">
            <div class="plat-hero-lbl">{selected} — Total Interactions</div>
            <div class="plat-hero-val">{total_p:,}</div>
            <div class="plat-hero-sub">Selected period</div>
        </div>
        <div class="plat-hero-rate">
            <div class="plat-hero-lbl">Booking Rate</div>
            <div class="plat-hero-val">{p_rate}</div>
            <div class="plat-hero-sub">{p_book:,} confirmed</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="metric-grid-4">
        <div class="metric-mini"><div class="metric-mini-lbl">Asked About Dates</div><div class="metric-mini-val" style="color:#F59E0B;">{p_asked:,}</div></div>
        <div class="metric-mini"><div class="metric-mini-lbl">Interested</div><div class="metric-mini-val" style="color:#10B981;">{p_int:,}</div></div>
        <div class="metric-mini"><div class="metric-mini-lbl">Not Interested</div><div class="metric-mini-val" style="color:#EF4444;">{p_not:,}</div></div>
        <div class="metric-mini"><div class="metric-mini-lbl">Didn't Answer</div><div class="metric-mini-val" style="color:#8B5CF6;">{p_nr:,}</div></div>
    </div>
    """, unsafe_allow_html=True)

    col_pie, col_bar = st.columns(2, gap="medium")
    with col_pie:
        st.markdown('<div class="panel"><div class="panel-title">Platform Distribution</div><div class="panel-sub">Share of interactions per channel</div>', unsafe_allow_html=True)
        plat_dist = {p: df_filtered[c].sum() for p,c in {"Instagram":"Instagram Answered","WhatsApp":"WhatsApp Answered","TikTok":"TikTok Answered","Calls":"Total Calls Received"}.items() if c in df_filtered.columns}
        pie = alt.Chart(pd.DataFrame(list(plat_dist.items()), columns=["Platform","Count"])).mark_arc(innerRadius=55,outerRadius=90,cornerRadius=3).encode(
            theta="Count:Q",
            color=alt.Color("Platform:N", scale=alt.Scale(domain=list(PLATFORM_COLORS.keys()),range=list(PLATFORM_COLORS.values())), legend=alt.Legend(orient="bottom",title=None)),
            tooltip=["Platform:N","Count:Q"],
        )
        st.altair_chart(pie.properties(height=230).configure(**DARK_CFG), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_bar:
        st.markdown(f'<div class="panel"><div class="panel-title">{selected} Breakdown</div><div class="panel-sub">Outcome by type</div>', unsafe_allow_html=True)
        sd = pd.DataFrame({"Metric":["Bookings","Asked Dates","Interested","Not Interested","No Reply"],"Count":[p_book,p_asked,p_int,p_not,p_nr],"Color":[PLATFORM_COLORS[selected],"#F59E0B","#10B981","#EF4444","#8B5CF6"]})
        sb = alt.Chart(sd).mark_bar(cornerRadiusTopLeft=4,cornerRadiusTopRight=4).encode(
            x=alt.X("Metric:N",axis=alt.Axis(labelAngle=-20)), y="Count:Q",
            color=alt.Color("Color:N",scale=None,legend=None),
            tooltip=["Metric:N","Count:Q"],
        )
        st.altair_chart(sb.properties(height=230).configure(**DARK_CFG), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    col_l, col_r = st.columns(2, gap="medium")
    with col_l:
        st.markdown('<div class="panel"><div class="panel-title">Interactions per Platform</div><div class="panel-sub">All channels</div>', unsafe_allow_html=True)
        int_d = {p: df_filtered[c].sum() for p,c in {"Instagram":"Instagram Answered","WhatsApp":"WhatsApp Answered","TikTok":"TikTok Answered","Calls":"Total Calls Received"}.items() if c in df_filtered.columns}
        ib2 = alt.Chart(pd.DataFrame(list(int_d.items()),columns=["Platform","Count"])).mark_bar(cornerRadiusTopLeft=4,cornerRadiusTopRight=4).encode(
            x=alt.X("Platform:N",axis=alt.Axis(labelAngle=0)),y="Count:Q",
            color=alt.Color("Platform:N",scale=alt.Scale(domain=list(PLATFORM_COLORS.keys()),range=list(PLATFORM_COLORS.values())),legend=None),
            tooltip=["Platform:N","Count:Q"],
        )
        st.altair_chart(ib2.properties(height=180).configure(**DARK_CFG), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="panel"><div class="panel-title">Bookings per Platform</div><div class="panel-sub">Conversion by channel</div>', unsafe_allow_html=True)
        bk_d = {p: df_filtered[c].sum() for p,c in {"Instagram":"New Bookings - Insta","WhatsApp":"New Bookings - Whats","TikTok":"New Bookings - TikTok","Calls":"New Bookings - Call"}.items() if c in df_filtered.columns}
        bb2 = alt.Chart(pd.DataFrame(list(bk_d.items()),columns=["Platform","Count"])).mark_bar(cornerRadiusTopLeft=4,cornerRadiusTopRight=4).encode(
            x=alt.X("Platform:N",axis=alt.Axis(labelAngle=0)),y="Count:Q",
            color=alt.Color("Platform:N",scale=alt.Scale(domain=list(PLATFORM_COLORS.keys()),range=list(PLATFORM_COLORS.values())),legend=None),
            tooltip=["Platform:N","Count:Q"],
        )
        st.altair_chart(bb2.properties(height=180).configure(**DARK_CFG), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════
# TIME ANALYSIS
# ══════════════════════════════════════════
else:
    weekly_platform = st.selectbox("Platform (weekly):", ["Instagram","WhatsApp","TikTok","Calls"], key="wp")
    wm = PLATFORM_COLS[weekly_platform]
    df_weeks = df_filtered.copy()
    df_weeks["week_start"] = df_weeks["Date"].dt.to_period("W").apply(lambda r: r.start_time.date())
    agg_cols = [c for c in [wm["total"], wm["bookings"]] if c in df_weeks.columns]

    if agg_cols:
        wagg = df_weeks.groupby("week_start")[agg_cols].sum().reset_index().sort_values("week_start")
        last4 = wagg.tail(4).copy()
        last4["Week"] = last4["week_start"].astype(str)
        col_w1, col_w2 = st.columns(2, gap="medium")
        with col_w1:
            st.markdown(f'<div class="panel"><div class="panel-title">Weekly Interactions — {weekly_platform}</div><div class="panel-sub">Last 4 weeks</div>', unsafe_allow_html=True)
            tc = wm["total"]
            if tc in last4.columns:
                wc = alt.Chart(last4[["Week",tc]].rename(columns={tc:"Count"})).mark_bar(cornerRadiusTopLeft=4,cornerRadiusTopRight=4,color=PLATFORM_COLORS[weekly_platform]).encode(
                    x=alt.X("Week:N",axis=alt.Axis(labelAngle=-20)),y="Count:Q",tooltip=["Week:N","Count:Q"])
                st.altair_chart(wc.properties(height=200).configure(**DARK_CFG), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col_w2:
            st.markdown(f'<div class="panel"><div class="panel-title">Weekly Bookings — {weekly_platform}</div><div class="panel-sub">Last 4 weeks</div>', unsafe_allow_html=True)
            bc2 = wm["bookings"]
            if bc2 in last4.columns:
                bwc = alt.Chart(last4[["Week",bc2]].rename(columns={bc2:"Count"})).mark_bar(cornerRadiusTopLeft=4,cornerRadiusTopRight=4,color="#F59E0B").encode(
                    x=alt.X("Week:N",axis=alt.Axis(labelAngle=-20)),y="Count:Q",tooltip=["Week:N","Count:Q"])
                st.altair_chart(bwc.properties(height=200).configure(**DARK_CFG), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No weekly data available for this platform.")

    st.markdown("---")

    daily_platform = st.selectbox("Platform (daily):", ["Instagram","WhatsApp","TikTok","Calls"], key="dp")
    dm = PLATFORM_COLS[daily_platform]
    df_days = df_filtered.copy().sort_values("Date")
    last7 = list(df_days["Date"].dt.date.unique()[-7:])
    df7 = df_days[df_days["Date"].dt.date.isin(last7)].copy()

    if df7.empty:
        st.info("No data for the last 7 days.")
    else:
        dcols = [c for c in [dm["total"], dm["bookings"]] if c in df7.columns]
        if dcols:
            dagg = df7.groupby(df7["Date"].dt.date)[dcols].sum().reset_index().rename(columns={"Date":"day"}).sort_values("day")
            dagg["Day"] = dagg["day"].astype(str)
            col_d1, col_d2 = st.columns(2, gap="medium")
            with col_d1:
                st.markdown(f'<div class="panel"><div class="panel-title">Daily Interactions — {daily_platform}</div><div class="panel-sub">Last 7 days</div>', unsafe_allow_html=True)
                tc2 = dm["total"]
                if tc2 in dagg.columns:
                    dc = alt.Chart(dagg[["Day",tc2]].rename(columns={tc2:"Count"})).mark_bar(cornerRadiusTopLeft=4,cornerRadiusTopRight=4,color=PLATFORM_COLORS[daily_platform]).encode(
                        x=alt.X("Day:N",axis=alt.Axis(labelAngle=-30)),y="Count:Q",tooltip=["Day:N","Count:Q"])
                    st.altair_chart(dc.properties(height=200).configure(**DARK_CFG), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with col_d2:
                st.markdown(f'<div class="panel"><div class="panel-title">Daily Bookings — {daily_platform}</div><div class="panel-sub">Last 7 days</div>', unsafe_allow_html=True)
                bc3 = dm["bookings"]
                if bc3 in dagg.columns:
                    bdc = alt.Chart(dagg[["Day",bc3]].rename(columns={bc3:"Count"})).mark_bar(cornerRadiusTopLeft=4,cornerRadiusTopRight=4,color="#F59E0B").encode(
                        x=alt.X("Day:N",axis=alt.Axis(labelAngle=-30)),y="Count:Q",tooltip=["Day:N","Count:Q"])
                    st.altair_chart(bdc.properties(height=200).configure(**DARK_CFG), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No data available.")
