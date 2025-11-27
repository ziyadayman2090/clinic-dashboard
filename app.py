import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Google Sheet CSV link
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTbn8mE8Z8QSRfb73Lk63htHUK31I59W5ZDaDTb81dtVK0Q61tczvnfGgGVQMYndidyxG8IdKuuVZ4o/pub?gid=0&single=true&output=csv"

st.set_page_config(
    page_title="Clinic Dashboard",
    layout="wide"
)

@st.cache_data(ttl=5)
def load_data():
    df = pd.read_csv(SHEET_CSV_URL)
    
    # first column is the date no matter the name
    first_col = df.columns[0]
    df["date"] = pd.to_datetime(df[first_col], dayfirst=True, errors="coerce")
    return df

df = load_data().sort_values("date")

# Date ranges
today = datetime.now().date()
week_start = today - timedelta(days=6)
month_start = today.replace(day=1)

df_today = df[df["date"].dt.date == today]
df_week = df[(df["date"].dt.date >= week_start) & (df["date"].dt.date <= today)]
df_month = df[(df["date"].dt.date >= month_start) & (df["date"].dt.date <= today)]

def calc_totals(data):
    if data.empty:
        return 0, 0, 0, 0
    
    def col(name):
        return data[name].sum() if name in data.columns else 0
    
    total_interactions = (
        col("total_calls") + col("whatsapp_answered") +
        col("instagram_answered") + col("tiktok_answered")
    )
    total_new = (
        col("new_insta") + col("new_call") +
        col("new_whatsapp") + col("new_tiktok")
    )
    interested = (
        col("interested_insta") + col("interested_whatsapp") + col("interested_tiktok")
    )
    not_interested = (
        col("not_insta") + col("not_whatsapp") + col("not_tiktok")
    )
    
    return int(total_interactions), int(total_new), int(interested), int(not_interested)

# Compute totals
today_int, today_new, today_ints, today_not = calc_totals(df_today)
week_int, week_new, week_ints, week_not = calc_totals(df_week)
month_int, month_new, month_ints, month_not = calc_totals(df_month)

# Sidebar
st.sidebar.title("📊 Clinic Dashboard")
st.sidebar.markdown("Daily • Weekly • Monthly")
st.sidebar.markdown("---")

period = st.sidebar.radio(
    "Select Period:",
    ["Today", "Last 7 Days", "This Month"],
    index=0
)

if period == "Today":
    use_df = df_today
    P_INT, P_NEW, P_INS, P_NOT = today_int, today_new, today_ints, today_not

elif period == "Last 7 Days":
    use_df = df_week
    P_INT, P_NEW, P_INS, P_NOT = week_int, week_new, week_ints, week_not

else:
    use_df = df_month
    P_INT, P_NEW, P_INS, P_NOT = month_int, month_new, month_ints, month_not

# Main Title
st.title("🦷 Clinic Performance Dashboard")

# Main KPIs
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Interactions", P_INT)
k2.metric("New Bookings", P_NEW)
k3.metric("Interested", P_INS)
k4.metric("Not Interested", P_NOT)

st.markdown("---")

# Layout
left_col, right_col = st.columns([2.2, 1])

with left_col:
    st.subheader("📈 Inquiry Trends")

    trend_df = df.copy()

    def safe_col(name):
        return trend_df[name] if name in trend_df.columns else 0

    trend_df["total_interactions"] = (
        safe_col("total_calls") + safe_col("whatsapp_answered") +
        safe_col("instagram_answered") + safe_col("tiktok_answered")
    )

    trend_df["new_bookings"] = (
        safe_col("new_insta") + safe_col("new_call") +
        safe_col("new_whatsapp") + safe_col("new_tiktok")
    )

    trend_df = trend_df.set_index("date")
    st.line_chart(trend_df[["total_interactions", "new_bookings"]])

    st.subheader("🔻 Conversion Funnel")

    if not use_df.empty:
        def U(name):
            return use_df[name].sum() if name in use_df.columns else 0

        leads = (
            U("total_calls") + U("whatsapp_answered") +
            U("instagram_answered") + U("tiktok_answered")
        )
        interested = P_INS
        bookings = P_NEW
        no_reply = (
            U("noreply_insta") + U("noreply_whatsapp") + U("noreply_tiktok")
        )

        funnel_df = pd.DataFrame({
            "Stage": ["Leads", "Interested", "Bookings", "No Reply"],
            "Value": [leads, interested, bookings, no_reply]
        }).set_index("Stage")

        st.bar_chart(funnel_df)

with right_col:
    st.subheader("😊 Customer Sentiment")

    total_sent = P_INS + P_NOT
    positive = (P_INS / total_sent * 100) if total_sent > 0 else 0
    negative = (P_NOT / total_sent * 100) if total_sent > 0 else 0

    sent_df = pd.DataFrame({
        "Type": ["Positive", "Negative"],
        "Value": [positive, negative]
    }).set_index("Type")

    st.bar_chart(sent_df)

    st.subheader("📱 Platforms Breakdown")

    if not use_df.empty:
        def U(name):
            return use_df[name].sum() if name in use_df.columns else 0
        
        plat_df = pd.DataFrame({
            "Platform": ["Calls", "WhatsApp", "Instagram", "TikTok"],
            "Count": [
                U("total_calls"),
                U("whatsapp_answered"),
                U("instagram_answered"),
                U("tiktok_answered")
            ]
        }).set_index("Platform")

        st.bar_chart(plat_df)

st.markdown("---")

st.subheader("📄 Latest 20 Rows")
st.dataframe(df.tail(20))

