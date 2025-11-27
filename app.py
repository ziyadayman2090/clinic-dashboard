import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="AL-basma Clinic Leads Dashboard",
    layout="wide",
)

st.caption("🔥per-platform sentiment")

# حط هنا لينك الـ CSV بتاع Google Sheet (زي ما انت بعتهولي)
GOOGLE_SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vTbn8mE8Z8QSRfb73Lk63htHUK31I59W5ZDaDTb81dtVK0Q61tczvnfGgGVQMYndidyxG8IdKuuVZ4o"
    "/pub?gid=551101663&single=true&output=csv"
)

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data(ttl=60 * 5)  # cache 5 minutes
def load_data() -> pd.DataFrame:
    df = pd.read_csv(GOOGLE_SHEET_CSV_URL)

    # نضمن إن اسم العمود مكتوب "Date"
    # ولو في مسافات أو حروف زيادة ننضفها
    df.columns = [c.strip() for c in df.columns]

    if "Date" not in df.columns:
        raise ValueError("Column 'Date' not found in sheet")

    # نحول التاريخ لـ datetime
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date"])

    # نرتب حسب التاريخ
    df = df.sort_values("Date")

    # نضيف شوية totals جاهزة
    def col(name):
        return df[name] if name in df.columns else 0

    df["total_interactions"] = (
        col("Total Calls Received")
        + col("WhatsApp Answered")
        + col("Instagram Answered")
        + col("TikTok Answered")
    )

    df["total_new_bookings"] = (
        col("New Bookings - Insta")
        + col("New Bookings - Call")
        + col("New Bookings - Whats")
        + col("New Bookings - TikTok")
    )

    df["total_interested"] = (
        col("Interested - Insta")
        + col("Interested - Whats")
        + col("Interested - TikTok")
    )

    df["total_not_interested"] = (
        col("Not Interested - Insta")
        + col("Not Interested - Whats")
        + col("Not Interested - TikTok")
    )

    return df


df = load_data()

# =========================================================
# FILTERS (SIDEBAR)
# =========================================================
st.sidebar.header("Filters")

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

quick_range = st.sidebar.selectbox(
    "Quick Range",
    options=["Today", "Last 7 days", "This month", "All time"],
    index=3,
)

today = max_date  # باعتبار آخر يوم في الشيت هو "اليوم"

if quick_range == "Today":
    default_start = today
    default_end = today
elif quick_range == "Last 7 days":
    default_start = today - timedelta(days=6)
    default_end = today
elif quick_range == "This month":
    default_start = date(today.year, today.month, 1)
    default_end = today
else:  # All time
    default_start = min_date
    default_end = max_date

start_date = st.sidebar.date_input("Start date", value=default_start, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End date", value=default_end, min_value=min_date, max_value=max_date)

if start_date > end_date:
    st.sidebar.error("Start date must be before end date")
    st.stop()

mask = (df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date)
filtered_df = df.loc[mask].copy()

if filtered_df.empty:
    st.warning("لا يوجد بيانات في الفترة المختارة.")
    st.stop()

# =========================================================
# TITLE
# =========================================================
st.title("📊 AL-basma Clinic – Leads Dashboard")

st.write(
    f"Showing data from **{start_date.strftime('%Y-%m-%d')}** to "
    f"**{end_date.strftime('%Y-%m-%d')}**"
)

# =========================================================
# TOP LINE CHART – INQUIRY TRENDS
# =========================================================
daily = (
    filtered_df.groupby("Date")[["total_interactions", "total_interested", "total_new_bookings", "total_not_interested"]]
    .sum()
    .reset_index()
)

st.subheader("Inquiry Trends")
trend_df = daily.set_index("Date")
st.line_chart(trend_df)

# =========================================================
# CUSTOMER SENTIMENT (متقسمة per platform)
# =========================================================
st.subheader("Customer Sentiment")

def col_sum(df_in: pd.DataFrame, name: str) -> int:
    return int(df_in[name].sum()) if name in df_in.columns else 0

left_col, right_col = st.columns(2)

# ---------- Not Interested per platform ----------
with left_col:
    st.markdown("**Not Interested per platform**")

    ni_calls = col_sum(filtered_df, "Not Interested - Call")
    ni_whats = col_sum(filtered_df, "Not Interested - Whats")
    ni_insta = col_sum(filtered_df, "Not Interested - Insta")
    ni_tiktok = col_sum(filtered_df, "Not Interested - TikTok")

    ni_df = pd.DataFrame(
        {
            "Platform": ["Calls", "WhatsApp", "Instagram", "TikTok"],
            "Count": [ni_calls, ni_whats, ni_insta, ni_tiktok],
        }
    ).set_index("Platform")

    st.bar_chart(ni_df)

# ---------- Didn't Answer per platform ----------
with right_col:
    st.markdown("**Didn't Answer per platform**")

    na_calls = col_sum(filtered_df, "Didn’t Answer - Call")
    na_whats = col_sum(filtered_df, "Didn’t Answer - Whats")
    na_insta = col_sum(filtered_df, "Didn’t Answer - Insta")
    na_tiktok = col_sum(filtered_df, "Didn’t Answer - TikTok")

    na_df = pd.DataFrame(
        {
            "Platform": ["Calls", "WhatsApp", "Instagram", "TikTok"],
            "Count": [na_calls, na_whats, na_insta, na_tiktok],
        }
    ).set_index("Platform")

    st.bar_chart(na_df)

# =========================================================
# PLATFORM BREAKDOWN
# =========================================================
st.subheader("Platform Breakdown")

pb_left, pb_right = st.columns(2)

with pb_left:
    st.markdown("**Interactions per platform**")

    interactions_df = pd.DataFrame(
        {
            "Platform": ["Calls", "WhatsApp", "Instagram", "TikTok"],
            "Interactions": [
                col_sum(filtered_df, "Total Calls Received"),
                col_sum(filtered_df, "WhatsApp Answered"),
                col_sum(filtered_df, "Instagram Answered"),
                col_sum(filtered_df, "TikTok Answered"),
            ],
        }
    ).set_index("Platform")

    st.bar_chart(interactions_df)

with pb_right:
    st.markdown("**New bookings per platform**")

    bookings_df = pd.DataFrame(
        {
            "Platform": ["Calls", "WhatsApp", "Instagram", "TikTok"],
            "New Bookings": [
                col_sum(filtered_df, "New Bookings - Call"),
                col_sum(filtered_df, "New Bookings - Whats"),
                col_sum(filtered_df, "New Bookings - Insta"),
                col_sum(filtered_df, "New Bookings - TikTok"),
            ],
        }
    ).set_index("Platform")

    st.bar_chart(bookings_df)

# =========================================================
# RAW DATA (اختياري)
# =========================================================
with st.expander("Show raw data"):
    st.dataframe(filtered_df.reset_index(drop=True))

