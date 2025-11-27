import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# رابط CSV بتاع Google Sheets
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTbn8mE8Z8QSRfb73Lk63htHUK31I59W5ZDaDTb81dtVK0Q61tczvnfGgGVQMYndidyxG8IdKuuVZ4o/pub?gid=0&single=true&output=csv"

st.set_page_config(
    page_title="Clinic Performance Dashboard",
    layout="wide"
)

@st.cache_data(ttl=60)
def load_data():
    # نقرأ الشيت
    df = pd.read_csv(SHEET_CSV_URL)

    # أول عمود هو التاريخ حتى لو اسمه مختلف (Date أو أي حاجة)
    first_col = df.columns[0]
    df["date"] = pd.to_datetime(df[first_col], dayfirst=True, errors="coerce")

    return df

# نرتب حسب التاريخ
df = load_data().sort_values("date")

# تعريف تواريخ اليوم / اسبوع / شهر
today = datetime.now().date()
week_start = today - timedelta(days=6)
month_start = today.replace(day=1)

df_today = df[df["date"].dt.date == today]
df_week = df[(df["date"].dt.date >= week_start) & (df["date"].dt.date <= today)]
df_month = df[(df["date"].dt.date >= month_start) & (df["date"].dt.date <= today)]

def calc_totals(data):
    # لو مفيش بيانات
    if data.empty:
        return 0, 0, 0, 0

    # نحاول نستخدم الأعمدة لو موجودة، ولو مش موجودة نخليها 0
    def col_sum(name):
        return data[name].sum() if name in data.columns else 0

    total_interactions = (
        col_sum("total_calls") +
        col_sum("whatsapp_answered") +
        col_sum("instagram_answered") +
        col_sum("tiktok_answered")
    )

    total_new = (
        col_sum("new_insta") +
        col_sum("new_call") +
        col_sum("new_whatsapp") +
        col_sum("new_tiktok")
    )

    total_interested = (
        col_sum("interested_insta") +
        col_sum("interested_whatsapp") +
        col_sum("interested_tiktok")
    )

    total_not = (
        col_sum("not_insta") +
        col_sum("not_whatsapp") +
        col_sum("not_tiktok")
    )

    return int(total_interactions), int(total_new), int(total_interested), int(total_not)

today_int, today_new, today_intst, today_not = calc_totals(df_today)
week_int, week_new, week_intst, week_not = calc_totals(df_week)
month_int, month_new, month_intst, month_not = calc_totals(df_month)

# Sidebar
st.sidebar.title("📊 Clinic Dashboard")
st.sidebar.markdown("**Dental Clinic – Daily, Weekly, Monthly**")
st.sidebar.markdown("---")

period = st.sidebar.radio(
    "اختر الفترة",
    ["اليوم", "آخر 7 أيام", "الشهر الحالي"],
    index=0
)

if period == "اليوم":
    use_df = df_today
    p_int, p_new, p_intst, p_not = today_int, today_new, today_intst, today_not
elif period == "آخر 7 أيام":
    use_df = df_week
    p_int, p_new, p_intst, p_not = week_int, week_new, week_intst, week_not
else:
    use_df = df_month
    p_int, p_new, p_intst, p_not = month_int, month_new, month_intst, month_not

st.title("🦷 Clinic Performance Dashboard")

# الكروت الرئيسية
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Interactions", p_int)
k2.metric("New Bookings", p_new)
k3.metric("Interested", p_intst)
k4.metric("Not Interested", p_not)

st.markdown("---")

left_col, right_col = st.columns([2.2, 1])

with left_col:
    st.subheader("📈 Inquiry Trends")

    trend_df = df.copy()
    # لو الأعمدة مش موجودة هنحط قيم 0
    def col_or_zero(name):
        return trend_df[name] if name in trend_df.columns else 0

    trend_df["total_interactions"] = (
        col_or_zero("total_calls") +
        col_or_zero("whatsapp_answered") +
        col_or_zero("instagram_answered") +
        col_or_zero("tiktok_answered")
    )
    trend_df["total_new_bookings"] = (
        col_or_zero("new_insta") +
        col_or_zero("new_call") +
        col_or_zero("new_whatsapp") +
        col_or_zero("new_tiktok")
    )
    trend_df = trend_df.set_index("date")

    st.line_chart(trend_df[["total_interactions", "total_new_bookings"]])

    st.subheader("🔻 Sales / Inquiry Funnel")

    if not use_df.empty:
        def ucol(name):
            return use_df[name].sum() if name in use_df.columns else 0

        leads = (
            ucol("total_calls") +
            ucol("whatsapp_answered") +
            ucol("instagram_answered") +
            ucol("tiktok_answered")
        )
        interested = p_intst
        bookings = p_new
        no_reply = (
            ucol("noreply_insta") +
            ucol("noreply_whatsapp") +
            ucol("noreply_tiktok")
        )

        funnel_df = pd.DataFrame({
            "Stage": ["Leads", "Interested", "Bookings", "No Reply"],
            "Value": [leads, interested, bookings, no_reply]
        }).set_index("Stage")

        st.bar_chart(funnel_df)
    else:
        st.info("لا توجد بيانات للفترة المحددة.")

with right_col:
    st.subheader("😊 Customer Sentiment")

    total_sent = p_intst + p_not
    pos = (p_intst / total_sent * 100) if total_sent > 0 else 0
    neg = (p_not / total_sent * 100) if total_sent > 0 else 0

    sent_df = pd.DataFrame({
        "Type": ["Positive (Interested)", "Negative (Not Interested)"],
        "Value": [pos, neg]
    }).set_index("Type")

    st.bar_chart(sent_df)

    st.subheader("📱 Platform Snapshot")

    if not use_df.empty:
        def ucol(name):
            return use_df[name].sum() if name in use_df.columns else 0

        plat_df = pd.DataFrame({
            "Platform": ["Calls", "WhatsApp", "Instagram", "TikTok"],
            "Count": [
                ucol("total_calls"),
                ucol("whatsapp_answered"),
                ucol("instagram_answered"),
                ucol("tiktok_answered")
            ]
        }).set_index("Platform")

        st.bar_chart(plat_df)
    else:
        st.info("لا توجد بيانات.")

st.markdown("---")
st.subheader("📄 آخر 20 صف من البيانات")
st.dataframe(df.tail(20))

