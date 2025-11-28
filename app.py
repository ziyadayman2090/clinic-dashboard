
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta, date
import traceback

# ======================
# Page Config
# ======================
st.set_page_config(page_title="AL-basma Clinic Leads Dashboard", page_icon="📊", layout="wide")

# ======================
# Google Sheet CSV URL
# ======================
GOOGLE_SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vTbn8mE8Z8QSRfb73Lk63htHUK31I59W5ZDaDTb81dtVK0Q61tczvnfGgGVQMYndidyxG8IdKuuVZ4o/"
    "pub?gid=551101663&single=true&output=csv"
)

# ======================
# Helper Functions
# ======================
def safe_sum_per_row(df, cols):
    existing = [c for c in cols if c in df.columns]
    if not existing:
        return 0
    return df[existing].sum(axis=1)

def safe_col_sum(df, col_name):
    return int(df[col_name].sum()) if col_name in df.columns else 0

def safe_col_sum_any(df, names):
    """Handles multiple possible column names (apostrophe variants)."""
    if isinstance(names, (list, tuple)):
        existing = [n for n in names if n in df.columns]
        if not existing:
            return 0
        return int(df[existing].sum().sum())
    else:
        return int(df[names].sum()) if names in df.columns else 0

@st.cache_data(ttl=5)
def load_data():
    df = pd.read_csv(GOOGLE_SHEET_CSV_URL)

    if "Date" not in df.columns:
        raise ValueError("Column 'Date' not found in sheet.")

    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date"]).sort_values("Date")

    # Aggregate columns
    df["total_interactions"] = safe_sum_per_row(df, [
        "Total Calls Received", "WhatsApp Answered", "Instagram Answered", "TikTok Answered"
    ])
    df["total_new_bookings"] = safe_sum_per_row(df, [
        "New Bookings - Insta", "New Bookings - Call", "New Bookings - Whats", "New Bookings - TikTok"
    ])
    df["total_interested"] = safe_sum_per_row(df, [
        "Interested - Insta", "Interested - Whats", "Interested - TikTok", "Interested - Call"
    ])
    df["total_not_interested"] = safe_sum_per_row(df, [
        "Not Interested - Insta", "Not Interested - Whats", "Not Interested - TikTok", "Not Interested - Call"
    ])
    df["total_asked_dates"] = safe_sum_per_row(df, [
        "Asked About Dates - Insta", "Asked About Dates - Whats", "Asked About Dates - TikTok", "Asked About Dates - Call"
    ])
    df["total_no_reply"] = safe_sum_per_row(df, [
        "Didn’t Answer - Insta", "Didn’t Answer - Whats", "Didn’t Answer - TikTok", "Didn’t Answer - Call",
        "Didn't Answer - Insta", "Didn't Answer - Whats", "Didn't Answer - TikTok", "Didn't Answer - Call"
    ])

    return df

# ======================
# Load Data
# ======================
df = load_data()
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

# ======================
# Sidebar Filters
# ======================
with st.sidebar:
    st.header("📅 Filters")
    quick_range = st.radio("Quick Range", ["Today", "Last 7 days", "This month", "All time"], index=2)
    today = max_date

    if quick_range == "Today":
        default_start, default_end = today, today
    elif quick_range == "Last 7 days":
        default_start, default_end = today - timedelta(days=6), today
    elif quick_range == "This month":
        default_start, default_end = today.replace(day=1), today
    else:
        default_start, default_end = min_date, max_date

    start_date = st.date_input("Start date", value=default_start, min_value=min_date, max_value=max_date)
    end_date = st.date_input("End date", value=default_end, min_value=min_date, max_value=max_date)

    if start_date > end_date:
        st.warning("Start date بعد End date – تم تعديله تلقائيًا.")
        start_date, end_date = end_date, start_date

# Filter data
mask = (df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date)
df_filtered = df.loc[mask].copy()

if df_filtered.empty:
    st.warning("لا توجد بيانات في الفترة الزمنية المختارة.")
    st.stop()

# ======================
# Dashboard Title
# ======================
st.title("📊 AL-basma Clinic Leads Dashboard")

# ======================
# KPIs
# ======================
total_interactions = int(df_filtered["total_interactions"].sum())
total_new_bookings = int(df_filtered["total_new_bookings"].sum())
total_interested = int(df_filtered["total_interested"].sum())
total_not_interested = int(df_filtered["total_not_interested"].sum())
total_no_reply = int(df_filtered["total_no_reply"].sum())

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Interactions", total_interactions)
c2.metric("New Bookings", total_new_bookings)
c3.metric("Interested", total_interested)
c4.metric("Not Interested", total_not_interested)
c5.metric("Didn't Answer", total_no_reply)

st.markdown("---")

# ======================
# Platform Column Map
# ======================
def no_reply_variants(platform):
    return [f"Didn’t Answer - {platform}", f"Didn't Answer - {platform}"]

PLATFORM_COLS = {
    "Instagram": {
        "total": "Instagram Answered",
        "bookings": "New Bookings - Insta",
        "asked_dates": "Asked About Dates - Insta",
        "interested": "Interested - Insta",
        "not_interested": "Not Interested - Insta",
        "no_reply": no_reply_variants("Insta"),
    },
    "WhatsApp": {
        "total": "WhatsApp Answered",
        "bookings": "New Bookings - Whats",
        "asked_dates": "Asked About Dates - Whats",
        "interested": "Interested - Whats",
        "not_interested": "Not Interested - Whats",
        "no_reply": no_reply_variants("Whats"),
    },
    "TikTok": {
        "total": "TikTok Answered",
        "bookings": "New Bookings - TikTok",
        "asked_dates": "Asked About Dates - TikTok",
        "interested": "Interested - TikTok",
        "not_interested": "Not Interested - TikTok",
        "no_reply": no_reply_variants("TikTok"),
    },
    "Calls": {
        "total": "Total Calls Received",
        "bookings": "New Bookings - Call",
        "asked_dates": "Asked About Dates - Call",
        "interested": "Interested - Call",
        "not_interested": "Not Interested - Call",
        "no_reply": no_reply_variants("Call"),
    },
}

# ======================
# Tabs
# ======================
tab_overview, tab_platforms, tab_time = st.tabs(["📈 Overview", "📱 Platforms", "⏱ Time Analysis"])

# ======================
# Overview Tab
# ======================
with tab_overview:
    col_trend, col_sent = st.columns(2)

    with col_trend:
        st.subheader("Inquiry Trends")
        daily = df_filtered.groupby("Date")[["total_interactions", "total_interested", "total_new_bookings", "total_not_interested"]].sum().reset_index()
        daily_melted = daily.melt(id_vars=["Date"], var_name="Metric", value_name="Value")
        trend_chart = alt.Chart(daily_melted).mark_line(point=True).encode(
            x="Date:T", y="Value:Q", color="Metric:N", tooltip=["Date", "Metric", "Value"]
        ).properties(width="container")
        st.altair_chart(trend_chart, use_container_width=True)

    with col_sent:
        st.subheader("Customer Sentiment")
        sentiment_df = pd.DataFrame({
            "Sentiment": ["Negative", "Neutral", "Positive"],
            "Count": [
                int(df_filtered["total_not_interested"].sum()),
                int(df_filtered["total_asked_dates"].sum()),
                int(df_filtered["total_new_bookings"].sum() + df_filtered["total_interested"].sum())
            ]
        })
        sentiment_chart = alt.Chart(sentiment_df).mark_bar().encode(
            x="Sentiment:N", y="Count:Q", color="Sentiment:N", tooltip=["Sentiment", "Count"]
        ).properties(width="container")
        st.altair_chart(sentiment_chart, use_container_width=True)

# ======================
# Platforms Tab
# ======================
with tab_platforms:
    st.subheader("Platform Breakdown (per platform)")
    platform = st.selectbox("Choose the platform:", ["Instagram", "WhatsApp", "TikTok", "Calls"], index=0)

    cols_map = PLATFORM_COLS[platform]

    # Safe KPI calculations
    total_platform_interactions = safe_col_sum(df_filtered, cols_map["total"])
    platform_bookings = safe_col_sum(df_filtered, cols_map["bookings"])
    platform_asked_dates = safe_col_sum(df_filtered, cols_map["asked_dates"])
    platform_interested = safe_col_sum(df_filtered, cols_map["interested"])
    platform_not_interested = safe_col_sum(df_filtered, cols_map["not_interested"])
    platform_no_reply = safe_col_sum_any(df_filtered, cols_map["no_reply"])

    k1, k2, k3 = st.columns(3)
    k4, k5, k6 = st.columns(3)
    k1.metric("Total interactions", total_platform_interactions)
    k2.metric("New bookings", platform_bookings)
    k3.metric("Asked about dates", platform_asked_dates)
    k4.metric("Interested", platform_interested)
    k5.metric("Not interested", platform_not_interested)
    k6.metric("Didn't answer", platform_no_reply)

    st.markdown("---")
    st.subheader("Platforms overview")
    col_left, col_right = st.columns(2)

    with col_left:
        st.caption("Interactions per platform")
        interactions_cols = {
            p: df_filtered[c["total"]].sum()
            for p, c in PLATFORM_COLS.items() if c["total"] in df_filtered.columns
        }
        if interactions_cols:
            df_chart = pd.DataFrame(list(interactions_cols.items()), columns=["Platform", "Count"])
            st.altair_chart(alt.Chart(df_chart).mark_bar().encode(x="Platform:N", y="Count:Q", color="Platform:N"), use_container_width=True)
        else:
            st.info("لا توجد أعمدة تفاعل للمنصات في الشيت.")

    with col_right:
        st.caption("New bookings per platform")
        bookings_cols = {
            p: df_filtered[c["bookings"]].sum()
            for p, c in PLATFORM_COLS.items() if c["bookings"] in df_filtered.columns
        }
        if bookings_cols:
            df_chart = pd.DataFrame(list(bookings_cols.items()), columns=["Platform", "Count"])
            st.altair_chart(alt.Chart(df_chart).mark_bar().encode(x="Platform:N", y="Count:Q", color="Platform:N"), use_container_width=True)
        else:
            st.info("لا توجد أعمدة New Bookings للمنصات في الشيت.")

# ======================
# Time Analysis Tab
# ======================
with tab_time:
    st.subheader("Last 4 weeks (weekly view)")
    weekly_platform = st.selectbox("Choose platform:", ["Instagram", "WhatsApp", "TikTok", "Calls"], index=0, key="weekly_platform")
    weekly_cols_map = PLATFORM_COLS[weekly_platform]

    df_weeks = df_filtered.copy()
    df_weeks["week_start"] = df_weeks["Date"].dt.to_period("W").apply(lambda r: r.start_time.date())

    agg_cols = [c for c in [weekly_cols_map["total"], weekly_cols_map["bookings"]] if c in df_weeks.columns]
    if agg_cols:
        week_agg = df_weeks.groupby("week_start")[agg_cols].sum().reset_index().sort_values("week_start")
        last_4 = week_agg.tail(4)
        last_4["Week"] = last_4["week_start"].astype(str)
        st.altair_chart(alt.Chart(last_4.melt(id_vars=["Week"], var_name="Metric", value_name="Value")).mark_bar().encode(x="Week:N", y="Value:Q", color="Metric:N"), use_container_width=True)
    else:
        st.info("لا توجد بيانات لهذا البلاتفورم.")

    st.markdown("---")
    st.subheader("Last 7 days (daily view)")
    daily_platform = st.selectbox("Choose platform:", ["Instagram", "WhatsApp", "TikTok", "Calls"], index=0, key="daily_platform")
    daily_cols_map = PLATFORM_COLS[daily_platform]

    df_days = df_filtered.copy().sort_values("Date")
    last_7_days = df_days["Date"].dt.date.unique()[-7:]
    df_last7 = df_days[df_days["Date"].dt.date.isin(last_7_days)]

    agg_cols = [c for c in [daily_cols_map["total"], daily_cols_map["bookings"]] if c in df_last7.columns]
    if agg_cols:
        day_agg = df_last7.groupby(df_last7["Date"].dt.date)[agg_cols].sum().reset_index()
        day_agg["Day"] = day_agg["Date"].astype(str)
        st.altair_chart(alt.Chart(day_agg.melt(id_vars=["Day"], var_name="Metric", value_name="Value")).mark_line(point=True).encode(x="Day:N", y="Value:Q", color="Metric:N"), use_container_width=True)
    else:
        st.info("لا توجد بيانات لهذا البلاتفورم.")


        




