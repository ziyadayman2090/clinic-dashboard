import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# =========================
#  Google Sheet CSV link
# =========================
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTbn8mE8Z8QSRfb73Lk63htHUK31I59W5ZDaDTb81dtVK0Q61tczvnfGgGVQMYndidyxG8IdKuuVZ4o/pub?gid=0&single=true&output=csv"

st.set_page_config(
    page_title="Clinic Dashboard",
    layout="wide"
)

# cache refresh every 5 seconds
@st.cache_data(ttl=5)
def load_data():
    df = pd.read_csv(SHEET_CSV_URL)

    # use "Date" column if exists, otherwise first column
    date_col = "Date" if "Date" in df.columns else df.columns[0]
    df["date"] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")

    return df


df = load_data().sort_values("date")

# =========================
#   Date ranges
# =========================
today = datetime.now().date()
week_start = today - timedelta(days=6)
month_start = today.replace(day=1)

df_today = df[df["date"].dt.date == today]
df_week = df[(df["date"].dt.date >= week_start) & (df["date"].dt.date <= today)]
df_month = df[(df["date"].dt.date >= month_start) & (df["date"].dt.date <= today)]


def sum_col(data, name):
    """safe sum: returns 0 if column doesn't exist."""
    return data[name].sum() if name in data.columns else 0


def calc_metrics(data):
    if data.empty:
        return {
            "total_interactions": 0,
            "total_calls": 0,
            "whatsapp_answered": 0,
            "instagram_answered": 0,
            "tiktok_answered": 0,
            "new_bookings_total": 0,
            "new_bookings_insta": 0,
            "new_bookings_call": 0,
            "new_bookings_whats": 0,
            "new_bookings_tiktok": 0,
            "asked_total": 0,
            "asked_in": 0,
            "asked_w": 0,
            "asked_tik": 0,
            "interested_total": 0,
            "interested_insta": 0,
            "interested_whats": 0,
            "interested_tik": 0,
        }

    total_calls = sum_col(data, "Total Calls Received")
    whatsapp_answered = sum_col(data, "WhatsApp Answered")
    instagram_answered = sum_col(data, "Instagram Answered")
    tiktok_answered = sum_col(data, "TikTok Answered")

    new_insta = sum_col(data, "New Bookings - Insta")
    new_call = sum_col(data, "New Bookings - Call")
    new_whats = sum_col(data, "New Bookings - Whats")
    new_tiktok = sum_col(data, "New Bookings - TikTok")

    asked_in = sum_col(data, "Asked About Dates - In")
    asked_w = sum_col(data, "Asked About Dates - W")
    asked_tik = sum_col(data, "Asked About Dates - Tik")

    int_insta = sum_col(data, "Interested - Insta")
    int_whats = sum_col(data, "Interested - Whats")
    int_tik = sum_col(data, "Interested - Tik")

    total_interactions = (
        total_calls + whatsapp_answered + instagram_answered + tiktok_answered
    )

    new_total = new_insta + new_call + new_whats + new_tiktok
    asked_total = asked_in + asked_w + asked_tik
    interested_total = int_insta + int_whats + int_tik

    return {
        "total_interactions": int(total_interactions),
        "total_calls": int(total_calls),
        "whatsapp_answered": int(whatsapp_answered),
        "instagram_answered": int(instagram_answered),
        "tiktok_answered": int(tiktok_answered),
        "new_bookings_total": int(new_total),
        "new_bookings_insta": int(new_insta),
        "new_bookings_call": int(new_call),
        "new_bookings_whats": int(new_whats),
        "new_bookings_tiktok": int(new_tiktok),
        "asked_total": int(asked_total),
        "asked_in": int(asked_in),
        "asked_w": int(asked_w),
        "asked_tik": int(asked_tik),
        "interested_total": int(interested_total),
        "interested_insta": int(int_insta),
        "interested_whats": int(int_whats),
        "interested_tik": int(int_tik),
    }


# metrics for each period
metrics_today = calc_metrics(df_today)
metrics_week = calc_metrics(df_week)
metrics_month = calc_metrics(df_month)

# =========================
#   SIDEBAR
# =========================
st.sidebar.title("📊 Clinic Dashboard")
st.sidebar.markdown("Dental Clinic — Daily / Weekly / Monthly")
st.sidebar.markdown("---")

period = st.sidebar.radio(
    "Select period:",
    ["Today", "Last 7 Days", "This Month"],
    index=0,
)

if period == "Today":
    use_df = df_today
    M = metrics_today
elif period == "Last 7 Days":
    use_df = df_week
    M = metrics_week
else:
    use_df = df_month
    M = metrics_month

# =========================
#   MAIN LAYOUT
# =========================
st.title("🦷 Clinic Performance Dashboard")

# ---- KPI cards ----
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Interactions", M["total_interactions"])
c2.metric("New Bookings (Total)", M["new_bookings_total"])
c3.metric("Asked About Dates", M["asked_total"])
c4.metric("Interested (Total)", M["interested_total"])

st.markdown("---")

left, right = st.columns([2.2, 1])

# =========================
#   LEFT COLUMN
# =========================
with left:
    st.subheader("📈 Inquiry Trends")

    trend_df = df.copy()

    # calculate per-row metrics using same column names as sheet
    def sc(name):
        return trend_df[name] if name in trend_df.columns else 0

    trend_df["total_interactions"] = (
        sc("Total Calls Received")
        + sc("WhatsApp Answered")
        + sc("Instagram Answered")
        + sc("TikTok Answered")
    )

    trend_df["new_bookings_total"] = (
        sc("New Bookings - Insta")
        + sc("New Bookings - Call")
        + sc("New Bookings - Whats")
        + sc("New Bookings - TikTok")
    )

    trend_df = trend_df.set_index("date")

    st.line_chart(trend_df[["total_interactions", "new_bookings_total"]])

    st.subheader("🔻 Conversion Funnel")

    if not use_df.empty:
        F = M  # just alias

        funnel_df = pd.DataFrame(
            {
                "Stage": [
                    "Total Interactions",
                    "Asked About Dates",
                    "Interested",
                    "New Bookings",
                ],
                "Value": [
                    F["total_interactions"],
                    F["asked_total"],
                    F["interested_total"],
                    F["new_bookings_total"],
                ],
            }
        ).set_index("Stage")

        st.bar_chart(funnel_df)
    else:
        st.info("No data for the selected period.")

# =========================
#   RIGHT COLUMN
# =========================
with right:
    st.subheader("😊 Customer Interest (Counts)")

    interest_df = pd.DataFrame(
        {
            "Type": ["Interested", "Not Interested / Others"],
            "Value": [
                M["interested_total"],
                max(M["total_interactions"] - M["interested_total"], 0),
            ],
        }
    ).set_index("Type")

    st.bar_chart(interest_df)

    st.subheader("📱 Channels Breakdown")

    channels_df = pd.DataFrame(
        {
            "Channel": ["Calls", "WhatsApp", "Instagram", "TikTok"],
            "Count": [
                M["total_calls"],
                M["whatsapp_answered"],
                M["instagram_answered"],
                M["tiktok_answered"],
            ],
        }
    ).set_index("Channel")

    st.bar_chart(channels_df)

# =========================
#   RAW DATA
# =========================
st.markdown("---")
st.subheader("📄 Latest 20 rows from sheet")
st.dataframe(df.tail(20))

