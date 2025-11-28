
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta, date

# ======================
# Page Config
# ======================
st.set_page_config(page_title="AL-basma Clinic Leads Dashboard", page_icon="📊", layout="wide")

# ======================
# Google Sheet CSV URL
# ======================
GOOGLE_SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vTbn8mE8Z8QSRfb73Lk63htHUK31I59W5ZDaDTb81dtVK0Q61tczvnfGgGVQMYndidyxG8IdKuuVZ4o/"
    "pub?gid=551101663&single=true&output=csv"
)

# ======================
# Helper Functions
# ======================
def safe_sum_per_row(df, cols):
    existing = [c for c in cols if c in df.columns]
    if not existing:
        return 0
    return df[existing].sum(axis=1)

def safe_col_sum(df, col_name):
    return int(df[col_name].sum()) if col_name in df.columns else 0

@st.cache_data(ttl=5)
def load_data():
    df = pd.read_csv(GOOGLE_SHEET_CSV_URL)

    if "Date" not in df.columns:
        raise ValueError("Column 'Date' not found in sheet. تأكد إن أول عمود اسمه Date بالظبط.")

    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date"]).sort_values("Date")

    # Aggregate columns (ORIGINAL logic + fixed apostrophes)
    df["total_interactions"] = safe_sum_per_row(df, [
        "Total Calls Received", "WhatsApp Answered", "Instagram Answered", "TikTok Answered"
    ])
    df["total_new_bookings"] = safe_sum_per_row(df, [
        "New Bookings - Insta", "New Bookings - Call", "New Bookings - Whats", "New Bookings - TikTok"
    ])
    df["total_interested"] = safe_sum_per_row(df, [
        "Interested - Insta", "Interested - Whats", "Interested - TikTok"
    ])
    df["total_not_interested"] = safe_sum_per_row(df, [
        "Not Interested - Insta", "Not Interested - Whats", "Not Interested - TikTok"
    ])
    df["total_asked_dates"] = safe_sum_per_row(df, [
        "Asked About Dates - Insta", "Asked About Dates - Whats", "Asked About Dates - TikTok"
        # NOTE: Call asked-dates column may not exist; we keep platform KPI safe via safe_col_sum.
    ])
    df["total_no_reply"] = safe_sum_per_row(df, [
        "Didn’t Answer - Insta", "Didn’t Answer - Whats", "Didn’t Answer - TikTok"
        # NOTE: "Didn’t Answer - Call" might exist; platform KPI uses safe_col_sum.
    ])

    return df

# ======================
# Load Data
# ======================
df = load_data()
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

# ======================
# Sidebar Filters
# ======================
with st.sidebar:
    st.header("📅 Filters")

    quick_range = st.radio("Quick Range", ["Today", "Last 7 days", "This month", "All time"], index=2)
    today = max_date

    if quick_range == "Today":
        default_start, default_end = today, today
    elif quick_range == "Last 7 days":
        default_start, default_end = today - timedelta(days=6), today
    elif quick_range == "This month":
        default_start, default_end = today.replace(day=1), today
    else:
        default_start, default_end = min_date, max_date

    start_date = st.date_input("Start date", value=default_start, min_value=min_date, max_value=max_date)
    end_date = st.date_input("End date", value=default_end, min_value=min_date, max_value=max_date)

    # تصليح لو المستخدم اختار تاريخ غلط
    if start_date > end_date:
        st.warning("Start date بعد End date – تم تعديله تلقائيًا.")
        start_date, end_date = end_date, start_date

# Filter data
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

st.markdown("---")

# ======================
# تعريف خريطة المنصات
# ======================
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
    "Calls": {
        "total": "Total Calls Received",
        "bookings": "New Bookings - Call",
        "asked_dates": "Asked About Dates - Call",  # may not exist; safe_col_sum handles it
        "interested": "Interested - Call",          # may not exist; safe_col_sum handles it
        "not_interested": "Not Interested - Call",  # may not exist; safe_col_sum handles it
        "no_reply": "Didn’t Answer - Call",         # may not exist; safe_col_sum handles it
    },
}

def safe_col_sum(df, col_name):
    return int(df[col_name].sum()) if col_name in df.columns else 0

# ======================
# Tabs رئيسية
# ======================
tab_overview, tab_platforms, tab_time = st.tabs(["📈 Overview", "📱 Platforms", "⏱ Time Analysis"])

# ======================
# 1) OVERVIEW TAB
# ======================
with tab_overview:
    col_trend, col_sent = st.columns(2)

    with col_trend:
        st.subheader("Inquiry Trends")
        daily = (
            df_filtered.groupby("Date")[
                ["total_interactions", "total_interested", "total_new_bookings", "total_not_interested"]
            ]
            .sum()
            .reset_index()
        )

        # Multi-series (more insight)
        daily_melted = daily.melt(id_vars=["Date"], var_name="Metric", value_name="Value")
        trend_chart = alt.Chart(daily_melted).mark_line(point=True).encode(
            x="Date:T",
            y="Value:Q",
            color="Metric:N",
            tooltip=["Date", "Metric", "Value"]
        ).properties(width="container")

        st.altair_chart(trend_chart, use_container_width=True)

    with col_sent:
        st.subheader("Customer Sentiment")

        negative_total = int(df_filtered["total_not_interested"].sum())
        neutral_total = int(df_filtered["total_asked_dates"].sum())
        positive_total = int(df_filtered["total_new_bookings"].sum() + df_filtered["total_interested"].sum())

        sentiment_df = pd.DataFrame(
            {
                "Sentiment": ["Negative", "Neutral", "Positive"],
                "Count": [negative_total, neutral_total, positive_total],
            }
        )

        sentiment_chart = alt.Chart(sentiment_df).mark_bar().encode(
            x="Sentiment:N",
            y="Count:Q",
            color="Sentiment:N",
            tooltip=["Sentiment", "Count"]
        ).properties(width="container")

        st.altair_chart(sentiment_chart, use_container_width=True)

# ======================
# 2) PLATFORMS TAB
# ======================
with tab_platforms:
    st.subheader("Platform Breakdown (per platform)")

    platform = st.selectbox(
        "Choose the platform:",
        ["Instagram", "WhatsApp", "TikTok", "Calls"],
        index=0,
        key="platform_main_select"
    )

    cols_map = PLATFORM_COLS[platform]

    # ✅ Compute KPIs safely (handles missing columns)
    total_platform_interactions = safe_col_sum(df_filtered, cols_map["total"])
    platform_bookings = safe_col_sum(df_filtered, cols_map["bookings"])
    platform_asked_dates = safe_col_sum(df_filtered, cols_map["asked_dates"])
    platform_interested = safe_col_sum(df_filtered, cols_map["interested"])
    platform_not_interested = safe_col_sum(df_filtered, cols_map["not_interested"])
    platform_no_reply = safe_col_sum(df_filtered, cols_map["no_reply"])

    # KPIs للمنصة المختارة
    k1, k2, k3 = st.columns(3)
    k4, k5, k6 = st.columns(3)

    k1.metric("Total interactions", total_platform_interactions)
    k2.metric("New bookings", platform_bookings)
    k3.metric("Asked about dates", platform_asked_dates)

    k4.metric("Interested", platform_interested)
    k5.metric("Not interested", platform_not_interested)
    k6.metric("Didn't answer", platform_no_reply)

    # Summary bar chart (Altair)
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
    )

    summary_chart = alt.Chart(platform_summary).mark_bar().encode(
        x="Metric:N",
        y="Count:Q",
        color="Metric:N",
        tooltip=["Metric", "Count"]
    ).properties(width="container")

    st.altair_chart(summary_chart, use_container_width=True)

    st.markdown("---")
    st.subheader("Platforms overview")

    col_left, col_right = st.columns(2)

    with col_left:
        st.caption("Interactions per platform")

        # ✅ FIXED: use c["total"] (string), not the mapping dict
        interactions_cols = {
            p: df_filtered[c["total"]].sum()
            for p, c in PLATFORM_COLS.items()
            if c["total"] in df_filtered.columns
        }

        if interactions_cols:
            interactions_df = pd.DataFrame(
                list(interactions_cols.items()),
                columns=["Platform", "Count"]
            )
            chart = alt.Chart(interactions_df).mark_bar().encode(
                x="Platform:N",
                y="Count:Q",
                color="Platform:N",
                tooltip=["Platform", "Count"]
            ).properties(width="container")
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("لا توجد أعمدة تفاعل للمنصات في الشيت.")

    with col_right:
        st.caption("New bookings per platform")

        # ✅ FIXED: use c["bookings"] (string), not the mapping dict
        bookings_cols = {
            p: df_filtered[c["bookings"]].sum()
            for p, c in PLATFORM_COLS.items()
            if c["bookings"] in df_filtered.columns
        }

        if bookings_cols:
            bookings_df = pd.DataFrame(
                list(bookings_cols.items()),
                columns=["Platform", "Count"]
            )
            chart = alt.Chart(bookings_df).mark_bar().encode(
                x="Platform:N",
                y="Count:Q",
                color="Platform:N",
                tooltip=["Platform", "Count"]
            ).properties(width="container")
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("لا توجد أعمدة New Bookings للمنصات في الشيت.")

# ======================
# 3) TIME ANALYSIS TAB
# ======================
with tab_time:
    # ---------- Last 4 weeks per platform ----------
    st.subheader("Last 4 weeks (weekly view)")

    weekly_platform = st.selectbox(
        "Choose platform (weekly view):",
        ["Instagram", "WhatsApp", "TikTok", "Calls"],
        index=0,
        key="weekly_platform",
    )

    weekly_cols_map = PLATFORM_COLS[weekly_platform]

    df_weeks = df_filtered.copy()
    df_weeks["week_start"] = df_weeks["Date"].dt.to_period("W").apply(lambda r: r.start_time.date())

    agg_cols = []
    if weekly_cols_map["total"] in df_weeks.columns:
        agg_cols.append(weekly_cols_map["total"])
    if weekly_cols_map["bookings"] in df_weeks.columns:
        agg_cols.append(weekly_cols_map["bookings"])

    if agg_cols:
        week_agg = (
            df_weeks.groupby("week_start")[agg_cols]
            .sum()
            .reset_index()
            .sort_values("week_start")
        )

        last_4 = week_agg.tail(4).copy()
        last_4["Week"] = last_4["week_start"].astype(str)

        col_w1, col_w2 = st.columns(2)

        with col_w1:
            st.caption("Interactions per week")
            total_col = weekly_cols_map["total"]
            if total_col in last_4.columns:
                chart_df = last_4.rename(columns={total_col: "Value"})
                chart = alt.Chart(chart_df).mark_bar().encode(
                    x=alt.X("Week:N", sort=None),
                    y="Value:Q",
                    tooltip=["Week", "Value"]
                ).properties(width="container")
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("لا توجد بيانات للتفاعل الأسبوعي لهذا البلاتفورم.")

        with col_w2:
            st.caption("New bookings per week")
            book_col = weekly_cols_map["bookings"]
            if book_col in last_4.columns:
                chart_df = last_4.rename(columns={book_col: "Value"})
                chart = alt.Chart(chart_df).mark_bar().encode(
                    x=alt.X("Week:N", sort=None),
                    y="Value:Q",
                    tooltip=["Week", "Value"]
                ).properties(width="container")
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("لا توجد بيانات للحجوزات الأسبوعية لهذا البلاتفورم.")
    else:
        st.info("لا توجد أعمدة كافية لحساب بيانات الأسابيع لهذا البلاتفورم.")

    st.markdown("---")

    # ---------- Last 7 days per platform ----------
    st.subheader("Last 7 days (daily view)")

    daily_platform = st.selectbox(
        "Choose platform (last 7 days – daily view):",
        ["Instagram", "WhatsApp", "TikTok", "Calls"],
        index=0,
        key="last7_platform",
    )

    daily_cols_map = PLATFORM_COLS[daily_platform]

    df_days = df_filtered.copy().sort_values("Date")
    unique_days = df_days["Date"].dt.date.unique()
    last_7_days = list(unique_days[-7:])

    df_last7 = df_days[df_days["Date"].dt.date.isin(last_7_days)].copy()

    if df_last7.empty:
        st.info("لا توجد بيانات لآخر ٧ أيام لهذا البلاتفورم.")
    else:
        agg_cols = []
        if daily_cols_map["total"] in df_last7.columns:
            agg_cols.append(daily_cols_map["total"])
        if daily_cols_map["bookings"] in df_last7.columns:
            agg_cols.append(daily_cols_map["bookings"])

        if agg_cols:
            day_agg = (
                df_last7.groupby(df_last7["Date"].dt.date)[agg_cols]
                .sum()
                .reset_index()
                .rename(columns={"Date": "day"})
                .sort_values("day")
            )

            day_agg["Day"] = day_agg["day"].astype(str)

            col_d1, col_d2 = st.columns(2)

            with col_d1:
                st.caption("Interactions per day (last 7 days)")
                total_col = daily_cols_map["total"]
                if total_col in day_agg.columns:
                    chart_df = day_agg.rename(columns={total_col: "Value"})
                    chart = alt.Chart(chart_df).mark_line(point=True).encode(
                        x=alt.X("Day:N", sort=None),
                        y="Value:Q",
                        tooltip=["Day", "Value"]
                    ).properties(width="container")
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.info("لا توجد بيانات للتفاعل اليومي لهذا البلاتفورم.")

            with col_d2:
                st.caption("New bookings per day (last 7 days)")
                book_col = daily_cols_map["bookings"]
                if book_col in day_agg.columns:
                    chart_df = day_agg.rename(columns={book_col: "Value"})
                    chart = alt.Chart(chart_df).mark_line(point=True).encode(
                        x=alt.X("Day:N", sort=None),
                        y="Value:Q",
                        tooltip=["Day", "Value"]
                    ).properties(width="container")
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.info("لا توجد بيانات للحجوزات اليومية لهذا البلاتفورم.")
        




