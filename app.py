import pandas as pd
import streamlit as st
from datetime import datetime, date, timedelta

# ========================
# إعدادات عامة
# ========================
st.set_page_config(
    page_title="AL-basma Clinic Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 AL-basma Clinic Leads Dashboard")

# رابط الـ CSV من Google Sheets
GOOGLE_SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vTbn8mE8Z8QSRfb73Lk63htHUK31I59W5ZDaDTb81dtVK0Q61tczvnfGgGVQMYndidyxG8IdKuuVZ4o/"
    "pub?gid=551101663&single=true&output=csv"
)

# ========================
# تحميل البيانات
# ========================
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(GOOGLE_SHEET_CSV_URL)

    # تأكد إن اسم العمود "Date" زي ما في الشيت
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date"])
    df = df.sort_values("Date")

    return df


df = load_data()

# ========================
# فلاتر التاريخ
# ========================
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

st.sidebar.header("Filters")

quick_range = st.sidebar.selectbox(
    "Quick Range",
    ["Today", "Last 7 days", "This month", "All time"],
    index=2
)

# قيم ابتدائية للـ start / end حسب الـ quick range
if quick_range == "Today":
    default_start = max_date
    default_end = max_date
elif quick_range == "Last 7 days":
    default_end = max_date
    default_start = max_date - timedelta(days=6)
elif quick_range == "This month":
    default_start = date(max_date.year, max_date.month, 1)
    default_end = max_date
else:  # All time
    default_start = min_date
    default_end = max_date

start_date = st.sidebar.date_input("Start date", value=default_start, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End date", value=default_end, min_value=min_date, max_value=max_date)

# تأكد إن الـ start <= end
if start_date > end_date:
    st.sidebar.error("⚠️ Start date must be before end date")
    st.stop()

mask = (df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date)
filtered = df.loc[mask].copy()

if filtered.empty:
    st.warning("لا توجد بيانات في الفترة المختارة.")
    st.stop()

# ========================
# Helpers
# ========================
def safe_sum(col_name: str) -> int:
    """مجموع عمود لو موجود، 0 لو مش موجود."""
    if col_name in filtered.columns:
        return int(filtered[col_name].sum())
    return 0


def safe_row_sum(row: pd.Series, cols: list) -> float:
    return row[[c for c in cols if c in row.index]].sum()


# أسماء الأعمدة في الشيت (عدّلها لو مختلفة)
INTERACTION_COLS = [
    "Total Calls Received",
    "WhatsApp Answered",
    "Instagram Answered",
    "TikTok Answered",
]

NEW_BOOKING_COLS = [
    "New Bookings - Insta",
    "New Bookings - Call",
    "New Bookings - Whats",
    "New Bookings - TikTok",
]

INTERESTED_COLS = [
    "Interested - Insta",
    "Interested - Whats",
    "Interested - TikTok",
]

NOT_INTERESTED_COLS = [
    "Not Interested - Call",
    "Not Interested - Whats",
    "Not Interested - Insta",
    "Not Interested - TikTok",
]

DIDNT_ANSWER_COLS = [
    "Didn't Answer - Call",
    "Didn't Answer - Whats",
    "Didn't Answer - Insta",
    "Didn't Answer - TikTok",
]

# ========================
# KPIs أعلى الصفحة
# ========================
total_interactions = sum(safe_sum(c) for c in INTERACTION_COLS)
total_new_bookings = sum(safe_sum(c) for c in NEW_BOOKING_COLS)
total_interested = sum(safe_sum(c) for c in INTERESTED_COLS)
total_not_interested = sum(safe_sum(c) for c in NOT_INTERESTED_COLS)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric("Total Interactions", total_interactions)
kpi2.metric("New Bookings", total_new_bookings)
kpi3.metric("Interested", total_interested)
kpi4.metric("Not Interested", total_not_interested)

st.markdown("---")

# ========================
# Inquiry Trends (Line chart)
# ========================
trends = filtered.copy()

trends["total_interactions"] = trends.apply(
    lambda r: safe_row_sum(r, INTERACTION_COLS),
    axis=1,
)

trends["total_new_bookings"] = trends.apply(
    lambda r: safe_row_sum(r, NEW_BOOKING_COLS),
    axis=1,
)

trends["total_interested"] = trends.apply(
    lambda r: safe_row_sum(r, INTERESTED_COLS),
    axis=1,
)

trends["total_not_interested"] = trends.apply(
    lambda r: safe_row_sum(r, NOT_INTERESTED_COLS),
    axis=1,
)

trends_daily = (
    trends.groupby("Date")[["total_interactions", "total_interested",
                            "total_new_bookings", "total_not_interested"]]
    .sum()
)

st.subheader("Inquiry Trends")
st.line_chart(trends_daily)

st.markdown("---")

# ========================
# Customer Sentiment (الجديد)
# ========================
st.subheader("Customer Sentiment")

left_col, right_col = st.columns(2)

with left_col:
    st.markdown("**Not Interested per platform**")
    ni_df = pd.DataFrame({
        "Platform": ["Calls", "WhatsApp", "Instagram", "TikTok"],
        "Count": [
            safe_sum("Not Interested - Call"),
            safe_sum("Not Interested - Whats"),
            safe_sum("Not Interested - Insta"),
            safe_sum("Not Interested - TikTok"),
        ],
    }).set_index("Platform")
    st.bar_chart(ni_df)

with right_col:
    st.markdown("**Didn't answer per platform**")
    na_df = pd.DataFrame({
        "Platform": ["Calls", "WhatsApp", "Instagram", "TikTok"],
        "Count": [
            safe_sum("Didn't Answer - Call"),
            safe_sum("Didn't Answer - Whats"),
            safe_sum("Didn't Answer - Insta"),
            safe_sum("Didn't Answer - TikTok"),
        ],
    }).set_index("Platform")
    st.bar_chart(na_df)

st.markdown("---")

# ========================
# Platform Breakdown
# ========================
st.subheader("Platform Breakdown")

# Interactions per platform
platform_interactions = pd.DataFrame({
    "Platform": ["Calls", "WhatsApp", "Instagram", "TikTok"],
    "Interactions": [
        safe_sum("Total Calls Received"),
        safe_sum("WhatsApp Answered"),
        safe_sum("Instagram Answered"),
        safe_sum("TikTok Answered"),
    ],
}).set_index("Platform")

# New bookings per platform
platform_bookings = pd.DataFrame({
    "Platform": ["Calls", "WhatsApp", "Instagram", "TikTok"],
    "New Bookings": [
        safe_sum("New Bookings - Call"),
        safe_sum("New Bookings - Whats"),
        safe_sum("New Bookings - Insta"),
        safe_sum("New Bookings - TikTok"),
    ],
}).set_index("Platform")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("**Interactions per platform**")
    st.bar_chart(platform_interactions)

with col_b:
    st.markdown("**New bookings per platform**")
    st.bar_chart(platform_bookings)
