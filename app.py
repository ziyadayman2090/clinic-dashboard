import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ==========================
# 1) إعداد الرابط بتاع الشيت
# ==========================
GOOGLE_SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vTbn8mE8Z8QSRfb73Lk63htHUK31I59W5ZDaDTb81dtVK0Q61tczvnfGgGVQMYndidyxG8IdKuuVZ4o"
    "/pub?gid=551101663&single=true&output=csv"
)

# ==========================
# 2) تحميل الداتا من الشيت
# ==========================
@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(GOOGLE_SHEET_CSV_URL)

    # نتأكد إن العمود اسمه بالظبط "Date" في الشيت
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date"])

    # نحول كل الأعمدة الرقمية لأرقام (لو في فراغات أو نصوص)
    for col in df.columns:
        if col != "Date":
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    return df


df = load_data()

# لو مفيش داتا خالص
if df.empty:
    st.error("No data loaded from Google Sheet. Please check the CSV URL or sharing settings.")
    st.stop()

# ====================================================
# 3) نحسب شوية أعمدة مجمعة عشان الرياحيت و الجرافيكس
# ====================================================
# إجمالي كل الإنترأكشنز (Calls + WhatsApp + Instagram + TikTok)
INTERACTION_COLS = [
    "Total Calls Received",
    "WhatsApp Answered",
    "Instagram Answered",
    "TikTok Answered",
]

# إجمالي الـ New Bookings
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
    "Not Interested - Insta",
    "Not Interested - Whats",
    "Not Interested - TikTok",
]

INCORRECT_AUDIENCE_COLS = [
    "Incorrect Audience - Insta",
    "Incorrect Audience - Whats",
    "Incorrect Audience - TikTok",
]

NO_REPLY_COLS = [
    "Didn’t Answer Back - Insta",
    "Didn’t Answer Back - Whats",
    "Didn’t Answer Back - TikTok",
]

# لو أسماء الأعمدة مختلفة عندك في الشيت عدل الأسماء فوق بس 👆

df["total_interactions"] = df[INTERACTION_COLS].sum(axis=1)
df["total_new_bookings"] = df[NEW_BOOKING_COLS].sum(axis=1)
df["total_interested"] = df[INTERESTED_COLS].sum(axis=1)
df["total_not_interested"] = df[NOT_INTERESTED_COLS].sum(axis=1)
df["total_incorrect_audience"] = df[INCORRECT_AUDIENCE_COLS].sum(axis=1)
df["total_no_reply"] = df[NO_REPLY_COLS].sum(axis=1)

# ====================================
# 4) إعداد صفحة Streamlit و الفلاتر
# ====================================
st.set_page_config(
    page_title="Clinic Leads Dashboard",
    layout="wide",
)

st.sidebar.title("Filters")

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()  # آخر يوم في الشيت هنعتبره "اليوم"
today = max_date

quick_range = st.sidebar.selectbox(
    "Quick Range",
    ["Today", "Last 7 days", "This month", "All time"],
    index=0,
)

# نحدد الافتراضي حسب الـ Quick Range
if quick_range == "Today":
    start_default = today
    end_default = today
elif quick_range == "Last 7 days":
    start_default = today - timedelta(days=6)
    end_default = today
elif quick_range == "This month":
    start_default = today.replace(day=1)
    end_default = today
else:  # All time
    start_default = min_date
    end_default = max_date

start_date = st.sidebar.date_input(
    "Start date",
    value=start_default,
    min_value=min_date,
    max_value=max_date,
)

end_date = st.sidebar.date_input(
    "End date",
    value=end_default,
    min_value=min_date,
    max_value=max_date,
)

# لو المستخدم اختار End قبل Start نعدّلهم
if end_date < start_date:
    st.sidebar.warning("End date is before start date. Dates have been swapped.")
    start_date, end_date = end_date, start_date

# نفلتر الداتا
mask = (df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date)
filtered = df.loc[mask].copy()

if filtered.empty:
    st.warning("No data available for the selected date range.")
    st.stop()

# ====================================
# 5) الـ Header و الكروت الأساسية
# ====================================

st.title("📊 Clinic Leads Dashboard")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Interactions", int(filtered["total_interactions"].sum()))

with col2:
    st.metric("New Bookings", int(filtered["total_new_bookings"].sum()))

with col3:
    st.metric("Interested", int(filtered["total_interested"].sum()))

with col4:
    st.metric("Not Interested", int(filtered["total_not_interested"].sum()))

st.markdown("---")

# ==============================
# 6) تريندز يومية (Line Chart)
# ==============================
st.subheader("📈 Inquiry Trends")

daily = (
    filtered.groupby("Date")[
        ["total_interactions", "total_new_bookings", "total_interested", "total_not_interested"]
    ]
    .sum()
    .reset_index()
)

daily = daily.sort_values("Date")

trend_df = daily.set_index("Date")

st.line_chart(trend_df)

# ===================================
# 7) Customer Sentiment Breakdown
# ===================================
st.subheader("😊 Customer Sentiment")

sentiment_totals = {
    "Positive (Bookings + Interested)": int(
        filtered["total_new_bookings"].sum() + filtered["total_interested"].sum()
    ),
    "Neutral (Asked Dates + No Reply)": int(
        filtered[["Asked About Dates - Insta",
                  "Asked About Dates - Whats",
                  "Asked About Dates - TikTok"]].sum().sum()
        + filtered["total_no_reply"].sum()
    ),
    "Negative (Not Interested + Wrong Audience)": int(
        filtered["total_not_interested"].sum()
        + filtered["total_incorrect_audience"].sum()
    ),
}

sentiment_df = pd.DataFrame(
    {"Sentiment": list(sentiment_totals.keys()), "Count": list(sentiment_totals.values())}
).set_index("Sentiment")

st.bar_chart(sentiment_df)

# ===================================
# 8) Platform Performance Breakdown
# ===================================
st.subheader("📱 Platform Breakdown")

platform_data = pd.DataFrame(
    {
        "Platform": ["Calls", "WhatsApp", "Instagram", "TikTok"],
        "Interactions": [
            int(filtered["Total Calls Received"].sum()),
            int(filtered["WhatsApp Answered"].sum()),
            int(filtered["Instagram Answered"].sum()),
            int(filtered["TikTok Answered"].sum()),
        ],
        "New Bookings": [
            int(filtered["New Bookings - Call"].sum()),
            int(filtered["New Bookings - Whats"].sum()),
            int(filtered["New Bookings - Insta"].sum()),
            int(filtered["New Bookings - TikTok"].sum()),
        ],
    }
)

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("**Interactions per platform**")
    st.bar_chart(
        platform_data.set_index("Platform")["Interactions"]
    )

with col_b:
    st.markdown("**New bookings per platform**")
    st.bar_chart(
        platform_data.set_index("Platform")["New Bookings"]
    )

# ===================================
# 9) جدول الداتا بعد الفلترة (اختياري)
# ===================================
with st.expander("Show raw filtered data"):
    st.dataframe(filtered.reset_index(drop=True))
