import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date

# ======================
# إعدادات الصفحة
# ======================
st.set_page_config(
    page_title="AL-basma Clinic Leads Dashboard",
    page_icon="📊",
    layout="wide",
)

# ======================
# رابط الـ CSV بتاع Google Sheets
# ======================
GOOGLE_SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vTbn8mE8Z8QSRfb73Lk63htHUK31I59W5ZDaDTb81dtVK0Q61tczvnfGgGVQMYndidyxG8IdKuuVZ4o/"
    "pub?gid=551101663&single=true&output=csv"
)

# ======================
# دالة مساعدة علشان لو في عمود ناقص
# ======================
def safe_sum_per_row(df, cols):
    existing = [c for c in cols if c in df.columns]
    if not existing:
        return 0
    return df[existing].sum(axis=1)


@st.cache_data
def load_data():
    df = pd.read_csv(GOOGLE_SHEET_CSV_URL)

    # نتأكد إن اسم العمود Date مكتوب صح
    if "Date" not in df.columns:
        raise ValueError("Column 'Date' not found in sheet. تأكد إن أول عمود اسمه Date بالظبط.")

    # نحول التاريخ
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date"]).sort_values("Date")

    # نعمل أعمدة إجمالية
    df["total_interactions"] = safe_sum_per_row(
        df,
        [
            "Total Calls Received",
            "WhatsApp Answered",
            "Instagram Answered",
            "TikTok Answered",
        ],
    )

    df["total_new_bookings"] = safe_sum_per_row(
        df,
        [
            "New Bookings - Insta",
            "New Bookings - Call",
            "New Bookings - Whats",
            "New Bookings - TikTok",
        ],
    )

    df["total_interested"] = safe_sum_per_row(
        df,
        [
            "Interested - Insta",
            "Interested - Whats",
            "Interested - TikTok",
        ],
    )

    df["total_not_interested"] = safe_sum_per_row(
        df,
        [
            "Not Interested - Insta",
            "Not Interested - Whats",
            "Not Interested - TikTok",
        ],
    )

    df["total_asked_dates"] = safe_sum_per_row(
        df,
        [
            "Asked About Dates - Insta",
            "Asked About Dates - Whats",
            "Asked About Dates - TikTok",
        ],
    )

    # خدو بالك: هنا بنستخدم الـ apostrophe اللي في الشيت "Didn’t"
    df["total_no_reply"] = safe_sum_per_row(
        df,
        [
            "Didn’t Answer - Insta",
            "Didn’t Answer - Whats",
            "Didn’t Answer - TikTok",
        ],
    )

    return df


# ======================
# تحميل الداتا
# ======================
df = load_data()
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

# ======================
# الـ Sidebar – فلاتر الزمن
# ======================
with st.sidebar:
    st.header("Filters")

    quick_range = st.selectbox(
        "Quick Range",
        ["Today", "Last 7 days", "This month", "All time"],
        index=2,
    )

    today = max_date

    if quick_range == "Today":
        default_start = today
        default_end = today
    elif quick_range == "Last 7 days":
        default_start = today - timedelta(days=6)
        default_end = today
    elif quick_range == "This month":
        default_start = today.replace(day=1)
        default_end = today
    else:  # All time
        default_start = min_date
        default_end = max_date

    start_date = st.date_input(
        "Start date",
        value=default_start,
        min_value=min_date,
        max_value=max_date,
    )
    end_date = st.date_input(
        "End date",
        value=default_end,
        min_value=min_date,
        max_value=max_date,
    )

    # تصليح لو المستخدم اختار تاريخ غلط
    if start_date > end_date:
        st.warning("Start date بعد End date – تم تعديله تلقائيًا.")
        start_date, end_date = end_date, start_date

# نفلتر الداتا
mask = (df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date)
df_filtered = df.loc[mask].copy()

if df_filtered.empty:
    st.warning("لا توجد بيانات في الفترة الزمنية المختارة.")
    st.stop()

# ======================
# العنوان
# ======================
st.title("📊 AL-basma Clinic Leads Dashboard")

# ======================
# KPIs فوق
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

# ======================
# Trend فوق
# ======================
daily = (
    df_filtered.groupby("Date")[
        ["total_interactions", "total_interested", "total_new_bookings", "total_not_interested"]
    ]
    .sum()
    .reset_index()
    .set_index("Date")
)

st.subheader("Inquiry Trends")
st.line_chart(daily)

# ======================
# Customer Sentiment (كل المنصات مع بعض)
# ======================
st.subheader("Customer Sentiment")

negative_total = int(df_filtered["total_not_interested"].sum())
neutral_total = int(df_filtered["total_asked_dates"].sum())
positive_total = int(df_filtered["total_new_bookings"].sum() + df_filtered["total_interested"].sum())

sentiment_df = pd.DataFrame(
    {
        "Sentiment": [
            "Negative (Not interested)",
            "Neutral (Asked about dates)",
            "Positive (Bookings + Interested)",
        ],
        "Count": [negative_total, neutral_total, positive_total],
    }
).set_index("Sentiment")

st.bar_chart(sentiment_df)

# ======================
# Platform Breakdown – per platform (Instagram / WhatsApp / TikTok)
# ======================
st.subheader("Platform Breakdown (per platform)")

platform = st.selectbox(
    "اختر المنصّة:",
    ["Instagram", "WhatsApp", "TikTok"],
    index=0,
)

PLATFORM_COLS = {
    "Instagram": {
        "total": "Instagram Answered",
        "bookings": "New Bookings - Insta",
        "asked_dates": "Asked About Dates - Insta",
        "interested": "Interested - Insta",
        "not_interested": "Not Interested - Insta",
        "no_reply": "Didn’t Answer - Insta",
    },
    "WhatsApp": {
        "total": "WhatsApp Answered",
        "bookings": "New Bookings - Whats",
        "asked_dates": "Asked About Dates - Whats",
        "interested": "Interested - Whats",
        "not_interested": "Not Interested - Whats",
        "no_reply": "Didn’t Answer - Whats",
    },
    "TikTok": {
        "total": "TikTok Answered",
        "bookings": "New Bookings - TikTok",
        "asked_dates": "Asked About Dates - TikTok",
        "interested": "Interested - TikTok",
        "not_interested": "Not Interested - TikTok",
        "no_reply": "Didn’t Answer - TikTok",
    },
}

cols_map = PLATFORM_COLS[platform]

def safe_col_sum(df, col_name):
    return int(df[col_name].sum()) if col_name in df.columns else 0

total_platform_interactions = safe_col_sum(df_filtered, cols_map["total"])
platform_bookings = safe_col_sum(df_filtered, cols_map["bookings"])
platform_asked_dates = safe_col_sum(df_filtered, cols_map["asked_dates"])
platform_interested = safe_col_sum(df_filtered, cols_map["interested"])
platform_not_interested = safe_col_sum(df_filtered, cols_map["not_interested"])
platform_no_reply = safe_col_sum(df_filtered, cols_map["no_reply"])

k1, k2, k3 = st.columns(3)
k4, k5, k6 = st.columns(3)

k1.metric("Total interactions", total_platform_interactions)
k2.metric("New bookings", platform_bookings)
k3.metric("Asked about dates", platform_asked_dates)

k4.metric("Interested", platform_interested)
k5.metric("Not interested", platform_not_interested)
k6.metric("Didn't answer", platform_no_reply)

platform_summary = pd.DataFrame(
    {
        "Metric": [
            "Total",
            "New bookings",
            "Asked dates",
            "Interested",
            "Not interested",
            "Didn't answer",
        ],
        "Count": [
            total_platform_interactions,
            platform_bookings,
            platform_asked_dates,
            platform_interested,
            platform_not_interested,
            platform_no_reply,
        ],
    }
).set_index("Metric")

st.bar_chart(platform_summary)

# ======================
# Interactions per platform (كلها مع بعض)
# ======================
st.subheader("Interactions per platform")

interactions_cols = {}

if "Instagram Answered" in df_filtered.columns:
    interactions_cols["Instagram"] = df_filtered["Instagram Answered"].sum()
if "WhatsApp Answered" in df_filtered.columns:
    interactions_cols["WhatsApp"] = df_filtered["WhatsApp Answered"].sum()
if "TikTok Answered" in df_filtered.columns:
    interactions_cols["TikTok"] = df_filtered["TikTok Answered"].sum()
if "Total Calls Received" in df_filtered.columns:
    interactions_cols["Calls"] = df_filtered["Total Calls Received"].sum()

if interactions_cols:
    interactions_df = (
        pd.DataFrame(list(interactions_cols.items()), columns=["Platform", "Count"])
        .set_index("Platform")
    )
    st.bar_chart(interactions_df)
else:
    st.info("لا توجد أعمدة تفاعل للمنصات في الشيت.")

# ======================
# New bookings per platform
# ======================
st.subheader("New bookings per platform")

bookings_cols = {}

if "New Bookings - Insta" in df_filtered.columns:
    bookings_cols["Instagram"] = df_filtered["New Bookings - Insta"].sum()
if "New Bookings - Whats" in df_filtered.columns:
    bookings_cols["WhatsApp"] = df_filtered["New Bookings - Whats"].sum()
if "New Bookings - TikTok" in df_filtered.columns:
    bookings_cols["TikTok"] = df_filtered["New Bookings - TikTok"].sum()
if "New Bookings - Call" in df_filtered.columns:
    bookings_cols["Calls"] = df_filtered["New Bookings - Call"].sum()

if bookings_cols:
    bookings_df = (
        pd.DataFrame(list(bookings_cols.items()), columns=["Platform", "Count"])
        .set_index("Platform")
    )
    st.bar_chart(bookings_df)
else:
    st.info("لا توجد أعمدة New Bookings للمنصات في الشيت.")
