import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# =========================
# إعدادات أساسية
# =========================
st.set_page_config(
    page_title="AL-basma Clinic Dashboard",
    page_icon="💊",
    layout="wide",
)

# رابط الـ CSV من Google Sheets
GOOGLE_SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vTbn8mE8Z8QSRfb73Lk63htHUK31I59W5ZDaDTb81dtVK0Q61tczvnfGgGVQMYndidyxG8IdKuuVZ4o/"
    "pub?gid=551101663&single=true&output=csv"
)

# أسماء الأعمدة في الشيت (زي ما هي بالحرف)
COL_DATE = "Date"

COL_CALLS = "Total Calls Received"
COL_WHATS = "WhatsApp Answered"
COL_INSTA = "Instagram Answered"
COL_TIKTOK = "TikTok Answered"

COL_NB_INSTA = "New Bookings - Insta"
COL_NB_CALL = "New Bookings - Call"
COL_NB_WHATS = "New Bookings - Whats"
COL_NB_TIKTOK = "New Bookings - TikTok"

COL_AD_INSTA = "Asked About Dates - Insta"
COL_AD_WHATS = "Asked About Dates - Whats"
COL_AD_TIKTOK = "Asked About Dates - TikTok"

COL_INT_INSTA = "Interested - Insta"
COL_INT_WHATS = "Interested - Whats"
COL_INT_TIKTOK = "Interested - TikTok"

COL_NI_INSTA = "Not Interested - Insta"
COL_NI_WHATS = "Not Interested - Whats"
COL_NI_TIKTOK = "Not Interested - TikTok"

COL_DA_INSTA = "Didn’t Answer - Insta"
COL_DA_WHATS = "Didn’t Answer - Whats"
COL_DA_TIKTOK = "Didn’t Answer - TikTok"  # لو مش موجود هيتعامل على إنه 0

# =========================
# تحميل وتجهيز الداتا
# =========================
@st.cache_data(ttl=300)
def load_data() -> pd.DataFrame:
    df = pd.read_csv(GOOGLE_SHEET_CSV_URL)

    # نحول التاريخ
    df[COL_DATE] = pd.to_datetime(df[COL_DATE], errors="coerce", dayfirst=True)

    # نحول كل الأعمدة الرقمية لأرقام (لو فيها فراغات/نصوص تتحول 0)
    num_cols = [
        COL_CALLS, COL_WHATS, COL_INSTA, COL_TIKTOK,
        COL_NB_INSTA, COL_NB_CALL, COL_NB_WHATS, COL_NB_TIKTOK,
        COL_AD_INSTA, COL_AD_WHATS, COL_AD_TIKTOK,
        COL_INT_INSTA, COL_INT_WHATS, COL_INT_TIKTOK,
        COL_NI_INSTA, COL_NI_WHATS, COL_NI_TIKTOK,
        COL_DA_INSTA, COL_DA_WHATS
    ]
    # لو عمود تيك توك لم يضاف لسه مش مشكلة
    if COL_DA_TIKTOK in df.columns:
        num_cols.append(COL_DA_TIKTOK)

    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    # أعمدة إجمالية
    df["total_interactions"] = df[
        [c for c in [COL_CALLS, COL_WHATS, COL_INSTA, COL_TIKTOK] if c in df.columns]
    ].sum(axis=1)

    df["total_new_bookings"] = df[
        [c for c in [COL_NB_INSTA, COL_NB_CALL, COL_NB_WHATS, COL_NB_TIKTOK] if c in df.columns]
    ].sum(axis=1)

    df["total_interested"] = df[
        [c for c in [COL_INT_INSTA, COL_INT_WHATS, COL_INT_TIKTOK] if c in df.columns]
    ].sum(axis=1)

    df["total_not_interested"] = df[
        [c for c in [COL_NI_INSTA, COL_NI_WHATS, COL_NI_TIKTOK] if c in df.columns]
    ].sum(axis=1)

    df["total_asked_dates"] = df[
        [c for c in [COL_AD_INSTA, COL_AD_WHATS, COL_AD_TIKTOK] if c in df.columns]
    ].sum(axis=1)

    df["total_no_reply"] = df[
        [c for c in [COL_DA_INSTA, COL_DA_WHATS, COL_DA_TIKTOK] if c in df.columns]
    ].sum(axis=1)

    return df


df = load_data().copy()

# =========================
# فلاتر التاريخ في الـ Sidebar
# =========================
st.sidebar.header("Filters")

min_date = df[COL_DATE].min().date()
max_date = df[COL_DATE].max().date()

quick_range = st.sidebar.selectbox(
    "Quick Range",
    ["Today", "Last 7 days", "This month", "All time"],
    index=2,
)

today = datetime.now().date()

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
    "Start date", value=start_default, min_value=min_date, max_value=max_date
)
end_date = st.sidebar.date_input(
    "End date", value=end_default, min_value=min_date, max_value=max_date
)

if start_date > end_date:
    st.sidebar.error("⚠️ Start date must be before end date.")
    st.stop()

mask = (df[COL_DATE].dt.date >= start_date) & (df[COL_DATE].dt.date <= end_date)
filtered = df.loc[mask].copy()

# لو مفيش داتا للفترة
if filtered.empty:
    st.title("AL-basma Clinic – Leads Dashboard")
    st.warning("لا توجد بيانات في الفترة المختارة.")
    st.stop()

# =========================
# العنوان و الـ KPIs
# =========================
st.title("📊 AL-basma Clinic – Leads Dashboard")

total_interactions = int(filtered["total_interactions"].sum())
total_new_bookings = int(filtered["total_new_bookings"].sum())
total_interested = int(filtered["total_interested"].sum())
total_not_interested = int(filtered["total_not_interested"].sum())

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Interactions", total_interactions)
kpi2.metric("New Bookings (All channels)", total_new_bookings)
kpi3.metric("Interested (All channels)", total_interested)
kpi4.metric("Not Interested (All channels)", total_not_interested)

st.markdown("---")

# =========================
# خط الإنتر أكشن على الأيام
# =========================
st.subheader("📈 Inquiry Trends")

trend_df = (
    filtered.sort_values(COL_DATE)
    .set_index(COL_DATE)[["total_interactions",
                          "total_interested",
                          "total_new_bookings",
                          "total_not_interested"]]
)

st.line_chart(trend_df)

st.markdown("---")

# =========================
# Customer Sentiment (إجمالي)
# =========================
st.subheader("😊 Customer Sentiment")

sent_negative = int(filtered["total_not_interested"].sum())
sent_neutral = int(filtered["total_asked_dates"].sum())
sent_positive = int(filtered["total_interested"].sum() +
                    filtered["total_new_bookings"].sum())

sent_df = pd.DataFrame(
    {
        "Sentiment": [
            "Negative (Not interested)",
            "Neutral (Asked dates)",
            "Positive (Interested / Booking)",
        ],
        "Count": [sent_negative, sent_neutral, sent_positive],
    }
)

st.bar_chart(sent_df.set_index("Sentiment"))

st.markdown("---")

# =========================
# Platform Breakdown
# =========================
st.subheader("📱 Platform Breakdown")

def safe_sum(frame: pd.DataFrame, col: str) -> int:
    return int(frame[col].sum()) if col in frame.columns else 0

platform_data = {
    "Calls": {
        "interactions": safe_sum(filtered, COL_CALLS),
        "bookings": safe_sum(filtered, COL_NB_CALL),
        "asked_dates": safe_sum(filtered, "Asked About Dates - Call"),  # لو مش موجود = 0
        "interested": safe_sum(filtered, "Interested - Call"),
        "not_interested": safe_sum(filtered, "Not Interested - Call"),
        "no_reply": safe_sum(filtered, "Didn’t Answer - Call"),
    },
    "WhatsApp": {
        "interactions": safe_sum(filtered, COL_WHATS),
        "bookings": safe_sum(filtered, COL_NB_WHATS),
        "asked_dates": safe_sum(filtered, COL_AD_WHATS),
        "interested": safe_sum(filtered, COL_INT_WHATS),
        "not_interested": safe_sum(filtered, COL_NI_WHATS),
        "no_reply": safe_sum(filtered, COL_DA_WHATS),
    },
    "Instagram": {
        "interactions": safe_sum(filtered, COL_INSTA),
        "bookings": safe_sum(filtered, COL_NB_INSTA),
        "asked_dates": safe_sum(filtered, COL_AD_INSTA),
        "interested": safe_sum(filtered, COL_INT_INSTA),
        "not_interested": safe_sum(filtered, COL_NI_INSTA),
        "no_reply": safe_sum(filtered, COL_DA_INSTA),
    },
    "TikTok": {
        "interactions": safe_sum(filtered, COL_TIKTOK),
        "bookings": safe_sum(filtered, COL_NB_TIKTOK),
        "asked_dates": safe_sum(filtered, COL_AD_TIKTOK),
        "interested": safe_sum(filtered, COL_INT_TIKTOK),
        "not_interested": safe_sum(filtered, COL_NI_TIKTOK),
        "no_reply": safe_sum(filtered, COL_DA_TIKTOK),
    },
}

# ---- 1) Interactions per platform
interactions_df = pd.DataFrame(
    {
        "Platform": list(platform_data.keys()),
        "Interactions": [v["interactions"] for v in platform_data.values()],
    }
).set_index("Platform")

st.caption("Interactions per platform")
st.bar_chart(interactions_df)

# ---- 2) New bookings per platform
bookings_df = pd.DataFrame(
    {
        "Platform": list(platform_data.keys()),
        "New bookings": [v["bookings"] for v in platform_data.values()],
    }
).set_index("Platform")

st.caption("New bookings per platform")
st.bar_chart(bookings_df)

st.markdown("---")

# =========================
# Platform Explorer (تفصيل منصة واحدة)
# =========================
st.subheader("🔍 Platform Explorer")

platform = st.selectbox(
    "اختر المنصّة:",
    ["Instagram", "WhatsApp", "TikTok", "Calls"],
    index=0,
)

selected = platform_data[platform]

m1, m2, m3 = st.columns(3)
m4, m5, m6 = st.columns(3)

m1.metric(f"{platform} – Answered", selected["interactions"])
m2.metric(f"{platform} – New bookings", selected["bookings"])
m3.metric(f"{platform} – Asked about dates", selected["asked_dates"])

m4.metric(f"{platform} – Interested", selected["interested"])
m5.metric(f"{platform} – Not interested", selected["not_interested"])
m6.metric(f"{platform} – Didn’t answer", selected["no_reply"])

st.markdown("---")

st.caption(
    "Dashboard connected live to Google Sheets. "
    "Any new data you add in the sheet will appear here automatically بعد دقائق قليلة."
)
