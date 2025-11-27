import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# =========================
# إعدادات عامة
# =========================
st.set_page_config(
    page_title="AL-basma Clinic Dashboard",
    page_icon="🦷",
    layout="wide",
)

# حط هنا لينك الـ CSV بتاع الشيت بتاعك
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTbn8mE8Z8QSRfb73Lk63htHUK31I59W5ZDaDTb81dtVK0Q61tczvnfGgGVQMYndidyxG8IdKuuVZ4o/pub?gid=551101663&single=true&output=csv"

# =========================
# تحميل البيانات
# =========================
@st.cache_data(ttl=300)
def load_data() -> pd.DataFrame:
    df = pd.read_csv(GOOGLE_SHEET_CSV_URL)

    # توحيد اسم العمود بتاع التاريخ
    if "Date" in df.columns:
        date_col = "Date"
    elif "date" in df.columns:
        date_col = "date"
    else:
        raise ValueError("لم أجد عمود للتاريخ (Date) في الشيت")

    df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")
    df = df.dropna(subset=[date_col])
    df = df.sort_values(date_col)
    df = df.rename(columns={date_col: "date"})

    # لو في أرقام فاضية نخليها 0
    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].fillna(0)

    # أعمدة ممكن تكون موجودة (هنستخدمها في الكالكوليشن)
    def col(name):
        return name if name in df.columns else None

    # إجمالي الإنترآكشن per day
    total_interaction_cols = [
        col("Total Calls Received"),
        col("WhatsApp Answered"),
        col("Instagram Answered"),
        col("TikTok Answered"),
    ]
    total_interaction_cols = [c for c in total_interaction_cols if c is not None]
    if total_interaction_cols:
        df["total_interactions"] = df[total_interaction_cols].sum(axis=1)
    else:
        df["total_interactions"] = 0

    # إجمالي new bookings
    new_booking_cols = [
        col("New Bookings - Insta"),
        col("New Bookings - Call"),
        col("New Bookings - Whats"),
        col("New Bookings - TikTok"),
    ]
    new_booking_cols = [c for c in new_booking_cols if c is not None]
    if new_booking_cols:
        df["total_new_bookings"] = df[new_booking_cols].sum(axis=1)
    else:
        df["total_new_bookings"] = 0

    # interested
    interested_cols = [
        col("Interested - Insta"),
        col("Interested - Whats"),
        col("Interested - TikTok"),
    ]
    interested_cols = [c for c in interested_cols if c is not None]
    if interested_cols:
        df["total_interested"] = df[interested_cols].sum(axis=1)
    else:
        df["total_interested"] = 0

    # not interested (كل البلاتفورمز)
    not_interested_cols = [
        col("Not Interested - Call"),
        col("Not Interested - Whats"),
        col("Not Interested - Insta"),
        col("Not Interested - TikTok"),
    ]
    not_interested_cols = [c for c in not_interested_cols if c is not None]
    if not_interested_cols:
        df["total_not_interested"] = df[not_interested_cols].sum(axis=1)
    else:
        df["total_not_interested"] = 0

    return df


df = load_data()

# =========================
# الفلاتر (السايد بار)
# =========================
st.sidebar.title("Filters")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

quick_range = st.sidebar.selectbox(
    "Quick Range",
    ["Today", "Last 7 days", "This month", "All time"],
)

today = datetime.now().date()

if quick_range == "Today":
    default_start = today
elif quick_range == "Last 7 days":
    default_start = today - timedelta(days=6)
elif quick_range == "This month":
    default_start = today.replace(day=1)
else:  # All time
    default_start = min_date

start_date = st.sidebar.date_input("Start date", value=default_start, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End date", value=max_date, min_value=min_date, max_value=max_date)

if start_date > end_date:
    st.sidebar.error("⚠️ تاريخ البداية أكبر من تاريخ النهاية، عدّل التواريخ.")
    st.stop()

mask = (df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)
filtered = df.loc[mask].copy()

# =========================
# العنوان
# =========================
st.title("🦷 AL-basma Clinic Leads Dashboard")

st.caption(
    f"الفترة من **{start_date}** إلى **{end_date}** — عدد الأيام: **{(end_date - start_date).days + 1}**"
)

# =========================
# KPIs
# =========================
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric("Total Interactions", int(filtered["total_interactions"].sum()))

with kpi2:
    st.metric("New Bookings", int(filtered["total_new_bookings"].sum()))

with kpi3:
    st.metric("Interested", int(filtered["total_interested"].sum()))

with kpi4:
    st.metric("Not Interested", int(filtered["total_not_interested"].sum()))

st.markdown("---")

# =========================
# Inquiry Trends
# =========================
st.subheader("📈 Inquiry Trends")

trend_cols = ["date", "total_interactions", "total_new_bookings", "total_interested", "total_not_interested"]
trend_data = filtered[trend_cols].set_index("date")

st.line_chart(trend_data)

st.markdown("---")

# =========================
# Not Interested & Didn't Answer per Platform
# =========================
col_left, col_right = st.columns(2)

# تعريف الأعمدة (هنا مهم اسم العمود يبقى زي الشيت بالظبط)
NOT_INTERESTED_PLATFORM_COLS = {
    "Calls": "Not Interested - Call",
    "WhatsApp": "Not Interested - Whats",
    "Instagram": "Not Interested - Insta",
    "TikTok": "Not Interested - TikTok",
}

NO_REPLY_PLATFORM_COLS = {
    "Calls": "Didn’t Answer - Call",
    "WhatsApp": "Didn’t Answer - Whats",
    "Instagram": "Didn’t Answer - Insta",
    "TikTok": "Didn’t Answer - TikTok",
}

# نستخدم بس الأعمدة اللي فعلاً موجودة في الشيت عشان ميبقاش فيه Error
ni_data = []
for label, col_name in NOT_INTERESTED_PLATFORM_COLS.items():
    if col_name in filtered.columns:
        ni_data.append({"Platform": label, "Count": int(filtered[col_name].sum())})

nr_data = []
for label, col_name in NO_REPLY_PLATFORM_COLS.items():
    if col_name in filtered.columns:
        nr_data.append({"Platform": label, "Count": int(filtered[col_name].sum())})

with col_left:
    st.subheader("🙅‍♂️ Not Interested per Platform")
    if ni_data:
        ni_df = pd.DataFrame(ni_data).set_index("Platform")
        st.bar_chart(ni_df)
    else:
        st.info("لا يوجد أعمدة Not Interested للمنصات في الشيت أو الأسماء مختلفة.")

with col_right:
    st.subheader("📵 Didn't Answer per Platform")
    if nr_data:
        nr_df = pd.DataFrame(nr_data).set_index("Platform")
        st.bar_chart(nr_df)
    else:
        st.info("لا يوجد أعمدة Didn't Answer للمنصات في الشيت أو الأسماء مختلفة.")

# =========================
# Platform breakdown (مثال بسيط)
# =========================
st.markdown("---")
st.subheader("📊 Platform Breakdown (All Interactions)")

platform_cols = {
    "Calls": "Total Calls Received",
    "WhatsApp": "WhatsApp Answered",
    "Instagram": "Instagram Answered",
    "TikTok": "TikTok Answered",
}

platform_data = []
for label, col_name in platform_cols.items():
    if col_name in filtered.columns:
        platform_data.append({"Platform": label, "Interactions": int(filtered[col_name].sum())})

if platform_data:
    plat_df = pd.DataFrame(platform_data).set_index("Platform")
    st.bar_chart(plat_df)
else:
    st.info("مش لاقي أعمدة إجمالي الإنترآكشن لكل بلاتفورم.")
