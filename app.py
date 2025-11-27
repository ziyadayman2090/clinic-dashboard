import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# =========================
# إعداد الصفحة
# =========================
st.set_page_config(
    page_title="AL-basma Clinic Leads Dashboard",
    layout="wide",
)

# رابط Google Sheets كـ CSV
GOOGLE_SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vTbn8mE8Z8QSRfb73Lk63htHUK31I59"
    "W5ZDaDTb81dtVK0Q61tczvnfGgGVQMYndidyxG8IdKuuVZ4o/pub?gid=551101663&single=true&output=csv"
)

# =========================
# تحميل الداتا
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv(GOOGLE_SHEET_CSV_URL)

    # تحويل التاريخ
    if "Date" not in df.columns:
        st.error("⚠️ عمود 'Date' مش موجود في الشيت.")
        st.stop()

    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date"])
    df = df.sort_values("Date")

    return df


df_raw = load_data()

# لو مفيش داتا
if df_raw.empty:
    st.warning("مفيش بيانات في الشيت حالياً.")
    st.stop()

# =========================
# فلاتر في الـ sidebar
# =========================
st.sidebar.title("Filters")

min_date = df_raw["Date"].min().date()
max_date = df_raw["Date"].max().date()

quick_range = st.sidebar.selectbox(
    "Quick Range",
    ["Today", "Last 7 days", "This month", "All time"],
    index=3,  # All time
)

# قيم افتراضية للـ start / end حسب الـ quick_range
if quick_range == "Today":
    default_start = max_date
    default_end = max_date
elif quick_range == "Last 7 days":
    default_end = max_date
    default_start = max_date - timedelta(days=6)
elif quick_range == "This month":
    default_start = max_date.replace(day=1)
    default_end = max_date
else:  # All time
    default_start = min_date
    default_end = max_date

start_date = st.sidebar.date_input(
    "Start date",
    value=default_start,
    min_value=min_date,
    max_value=max_date,
)

end_date = st.sidebar.date_input(
    "End date",
    value=default_end,
    min_value=min_date,
    max_value=max_date,
)

if start_date > end_date:
    st.sidebar.error("❌ Start date لازم يكون قبل End date")
    st.stop()

# فلترة الداتا حسب التاريخ
mask = (df_raw["Date"].dt.date >= start_date) & (df_raw["Date"].dt.date <= end_date)
df = df_raw.loc[mask].copy()

if df.empty:
    st.warning("مفيش بيانات في الفترة اللي اخترتها.")
    st.stop()


# helper للتجميع بأمان
def safe_sum(col: str) -> int:
    return int(df[col].sum()) if col in df.columns else 0


# =========================
# العنوان
# =========================
st.title("📊 AL-basma Clinic Leads Dashboard")

st.caption(
    f"البيانات من **{start_date.strftime('%Y/%m/%d')}** "
    f"لحد **{end_date.strftime('%Y/%m/%d')}**"
)

# =========================
# KPIs (cards فوق)
# =========================
TOTAL_INTERACTIONS_COLS = [
    "Total Calls Received",
    "WhatsApp Answered",
    "Instagram Answered",
    "TikTok Answered",
]

NEW_BOOKING_COLS = [
    "New Bookings - Call",
    "New Bookings - Whats",
    "New Bookings - Insta",
    "New Bookings - TikTok",
]

INTERESTED_COLS = [
    "Interested - Insta",
    "Interested - Whats",
    "Interested - TikTok",
]

NOT_INTERESTED_COLS = [
    "Not Interested - Call",   # لو مش موجود هيتحسب 0 عادي
    "Not Interested - Whats",
    "Not Interested - Insta",
    "Not Interested - TikTok",
]

total_interactions = sum(safe_sum(c) for c in TOTAL_INTERACTIONS_COLS)
total_new_bookings = sum(safe_sum(c) for c in NEW_BOOKING_COLS)
total_interested = sum(safe_sum(c) for c in INTERESTED_COLS)
total_not_interested = sum(safe_sum(c) for c in NOT_INTERESTED_COLS)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Interactions", total_interactions)
kpi2.metric("New Bookings", total_new_bookings)
kpi3.metric("Interested", total_interested)
kpi4.metric("Not Interested", total_not_interested)

# =========================
# خط التريند (line chart)
# =========================
st.subheader("Inquiry Trends")

trend_df = pd.DataFrame(
    {
        "Date": df["Date"],
        "total_interactions": sum(
            [
                df.get("Total Calls Received", 0),
                df.get("WhatsApp Answered", 0),
                df.get("Instagram Answered", 0),
                df.get("TikTok Answered", 0),
            ]
        ),
        "total_new_bookings": sum(
            [
                df.get("New Bookings - Call", 0),
                df.get("New Bookings - Whats", 0),
                df.get("New Bookings - Insta", 0),
                df.get("New Bookings - TikTok", 0),
            ]
        ),
        "total_interested": df.get("Interested - Insta", 0)
        + df.get("Interested - Whats", 0)
        + df.get("Interested - TikTok", 0),
        "total_not_interested": df.get("Not Interested - Call", 0)
        + df.get("Not Interested - Whats", 0)
        + df.get("Not Interested - Insta", 0)
        + df.get("Not Interested - TikTok", 0),
    }
).set_index("Date")

st.line_chart(trend_df)

# =========================
# Customer Sentiment (الجديد)
# =========================
st.subheader("Customer Sentiment")

left_col, right_col = st.columns(2)

# 1) Not Interested per platform
with left_col:
    st.markdown("**Not Interested per platform**")
    ni_df = pd.DataFrame(
        {
            "Platform": ["Calls", "WhatsApp", "Instagram", "TikTok"],
            "Count": [
                safe_sum("Not Interested - Call"),
                safe_sum("Not Interested - Whats"),
                safe_sum("Not Interested - Insta"),
                safe_sum("Not Interested - TikTok"),
            ],
        }
    ).set_index("Platform")
    st.bar_chart(ni_df)

# 2) Didn't answer per platform
with right_col:
    st.markdown("**Didn't Answer per platform**")
    na_df = pd.DataFrame(
        {
            "Platform": ["Calls", "WhatsApp", "Instagram", "TikTok"],
            "Count": [
                safe_sum("Didn't Answer - Call"),
                safe_sum("Didn't Answer - Whats"),
                safe_sum("Didn't Answer - Insta"),
                safe_sum("Didn't Answer - TikTok"),
            ],
        }
    ).set_index("Platform")
    st.bar_chart(na_df)

# =========================
# Platform Breakdown
# =========================
st.subheader("Platform Breakdown")

col1, col2 = st.columns(2)

# Interactions per platform
with col1:
    st.markdown("**Interactions per platform**")
    interactions_df = pd.DataFrame(
        {
            "Platform": ["Calls", "WhatsApp", "Instagram", "TikTok"],
            "Count": [
                safe_sum("Total Calls Received"),
                safe_sum("WhatsApp Answered"),
                safe_sum("Instagram Answered"),
                safe_sum("TikTok Answered"),
            ],
        }
    ).set_index("Platform")
    st.bar_chart(interactions_df)

# New bookings per platform
with col2:
    st.markdown("**New bookings per platform**")
    bookings_df = pd.DataFrame(
        {
            "Platform": ["Calls", "WhatsApp", "Instagram", "TikTok"],
            "New Bookings": [
                safe_sum("New Bookings - Call"),
                safe_sum("New Bookings - Whats"),
                safe_sum("New Bookings - Insta"),
                safe_sum("New Bookings - TikTok"),
            ],
        }
    ).set_index("Platform")
    st.bar_chart(bookings_df)

# =========================
# جدول تفصيلي باليوم
# =========================
st.subheader("Daily Details")

columns_to_show = [
    "Date",
    "Total Calls Received",
    "WhatsApp Answered",
    "Instagram Answered",
    "TikTok Answered",
    "New Bookings - Call",
    "New Bookings - Whats",
    "New Bookings - Insta",
    "New Bookings - TikTok",
    "Asked About Dates - Insta",
    "Asked About Dates - Whats",
    "Asked About Dates - TikTok",
    "Interested - Insta",
    "Interested - Whats",
    "Interested - TikTok",
    "Not Interested - Call",
    "Not Interested - Whats",
    "Not Interested - Insta",
    "Not Interested - TikTok",
    "Incorrect Audience - Insta",
    "Incorrect Audience - Wt",
    "Incorrect Audience - TikTok",
    "Didn't Answer - Call",
    "Didn't Answer - Whats",
    "Didn't Answer - Insta",
    "Didn't Answer - TikTok",
]

cols_existing = [c for c in columns_to_show if c in df.columns]

st.dataframe(
    df[cols_existing].sort_values("Date"),
    use_container_width=True,
)

