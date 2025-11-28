import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta, date
# ======================
# إعدادات الصفحة
# ======================
st.set_page_config(
    page_title="AL-Basma Clinic Leads Dashboard",
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


@st.cache_data(ttl=5)
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

    quick_range = st.radio(
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
st.title("📊 AL-Basma Clinic Leads Dashboard")

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

row_1col1,row1_col2=st.columns(2)

with row1_col1:
    st.subheader("Inquiry Trends")
    daily = df_filtered.groupby("Date")[["total_interactions", "total_interested", "total_new_bookings", "total_not_interested"]].sum().reset_index()
    daily_melted = daily.melt(id_vars=["Date"], var_name="Metric", value_name="Value")
    
    trend_chart = alt.Chart(daily_melted).mark_line(point=True).encode(
        x="Date:T", y="Value:Q", color="Metric:N", tooltip=["Date", "Metric", "Value"]
    ).properties(width="container")
    st.altair_chart(trend_chart, use_container_width=True)


with row1_col2:
    st.subheader("Customer Sentiment")
    negative_total = int(df_filtered["total_not_interested"].sum())
    neutral_total = int(df_filtered["total_asked_dates"].sum())
    positive_total = int(df_filtered["total_new_bookings"].sum() + df_filtered["total_interested"].sum())
    sentiment_df = pd.DataFrame({"Sentiment": ["Negative", "Neutral", "Positive"], "Count": [negative_total, neutral_total, positive_total]})

    sentiment_chart = alt.Chart(sentiment_df).mark_bar().encode(
        x="Sentiment:N", y="Count:Q", color="Sentiment:N", tooltip=["Sentiment", "Count"]
    ).properties(width="container")
    st.altair_chart(sentiment_chart, use_container_width=True)
st.markdown("---")

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("Platform Breakdown")
    platform_cols = {"Instagram": "Instagram Answered", "WhatsApp": "WhatsApp Answered", "TikTok": "TikTok Answered", "Calls": "Total Calls Received"}
    platform_data = {p: df_filtered[c].sum() for p, c in platform_cols.items() if c in df_filtered.columns}

    platform_df = pd.DataFrame(list(platform_data.items()), columns=["Platform", "Count"])
    platform_chart = alt.Chart(platform_df).mark_bar().encode(
        x="Platform:N", y="Count:Q", color="Platform:N", tooltip=["Platform", "Count"]
    ).properties(width="container")
    st.altair_chart(platform_chart, use_container_width=True)

with row2_col2:
    st.subheader("Platform Share")
    pie_chart = alt.Chart(platform_df).mark_arc(innerRadius=50).encode(
        theta="Count:Q", color="Platform:N", tooltip=["Platform", "Count"]
    ).properties(width="container")
    st.altair_chart(pie_chart, use_container_width=True)
st.markdown("---")

row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    st.subheader("Last 4 Weeks")
    df_filtered["week_start"] = 
df_filtered["Date"].dt.to_period("W").apply(lambda r: r.start_time.date())
    weekly = df_filtered.groupby("week_start")[["total_interactions", "total_new_bookings"]].sum().reset_index()

    weekly_chart = alt.Chart(weekly.melt(id_vars=["week_start"], var_name="Metric", value_name="Value")).mark_bar().encode(
        x="week_start:T", y="Value:Q", color="Metric:N", tooltip=["week_start", "Metric", "Value"]
    ).properties(width="container")
    st.altair_chart(weekly_chart, use_container_width=True)

with row3_col2:
    st.subheader("Last 7 Days")
    last7 = df_filtered.sort_values("Date").tail(7)
    daily_chart = alt.Chart(last7.melt(id_vars=["Date"], var_name="Metric", value_name="Value")).mark_line(point=True).encode(
        x="Date:T", y="Value:Q", color="Metric:N", tooltip=["Date", "Metric", "Value"]
    ).properties(width="container")
    st.altair_chart(daily_chart, use_container_width=True)


# ======================
# تعريف خريطة المنصات (هنستخدمها في أكتر من حتة)
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
        "asked_dates": "Asked About Dates - Call",
        "interested": "Interested - Call",
        "not_interested": "Not Interested - Call",
        "no_reply": "Didn’t Answer - Call",
    },
}

def safe_col_sum(df, col_name):
    return int(df[col_name].sum()) if col_name in df.columns else 0

# ======================
# Tabs رئيسية عشان تنظيم الصفحة
# ======================
tab_overview, tab_platforms, tab_time = st.tabs(
    ["📈 Overview", "📱 Platforms", "⏱ Time analysis"]
)

# ======================
# 1) OVERVIEW TAB
# ======================
with tab_overview:
    # --- Daily trend + Sentiment جنب بعض ---
    col_trend, col_sent = st.columns(2)

    
with col_trend:
    st.subheader("Inquiry Trends")
    daily = (
        df_filtered.groupby("Date")[
            ["total_interactions", "total_interested",
             "total_new_bookings", "total_not_interested"]
        ]
        .sum()
        .reset_index()
    )

    # Altair chart
    trend_chart = alt.Chart(daily).mark_line(point=True).encode(
        x="Date:T",
        y="total_interactions:Q",
        tooltip=["Date", "total_interactions"]
    ).properties(width="container")

    st.altair_chart(trend_chart, use_container_width=True)

        

    
with col_sent:
    st.subheader("Customer Sentiment")

    # Compute totals once
    negative_total = int(df_filtered["total_not_interested"].sum())
    neutral_total = int(df_filtered["total_asked_dates"].sum())
    positive_total = int(
        df_filtered["total_new_bookings"].sum()
        + df_filtered["total_interested"].sum()
    )

    # Build DataFrame for Altair
    sentiment_df = pd.DataFrame(
        {
            "Sentiment": [
                "Negative (Not interested)",
                "Neutral (Asked about dates)",
                "Positive (Bookings + Interested)",
            ],
            "Count": [negative_total, neutral_total, positive_total],
        }
    )

    # Altair bar chart
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

    
platform_cols = {
        "Instagram": "Instagram Answered",
        "WhatsApp": "WhatsApp Answered",
        "TikTok": "TikTok Answered",
        "Calls": "Total Calls Received"
    }


   
platform_data = {p: df_filtered[c].sum() for p, c in platform_cols.items() if c in df_filtered.columns}
pie_df = pd.DataFrame(list(platform_data.items()), columns=["Platform", "Count"])
pie_chart = alt.Chart(pie_df).mark_arc(innerRadius=50).encode(
        theta="Count:Q", color="Platform:N", tooltip=["Platform", "Count"]
)
    st.altair_chart(pie_chart, use_container_width=True)



    # KPIs للمنصة المختارة
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

    st.markdown("---")
    st.subheader("Platforms overview")

    col_left, col_right = st.columns(2)

    # ------ Interactions per platform ------
    with col_left:
        st.caption("Interactions per platform")

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

    # ------ New bookings per platform ------
    with col_right:
        st.caption("New bookings per platform")

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
    df_weeks["week_start"] = df_weeks["Date"].dt.to_period("W").apply(
        lambda r: r.start_time.date()
    )

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
                chart_df = last_4[["Week", total_col]].set_index("Week")
                st.bar_chart(chart_df)
            else:
                st.info("لا توجد بيانات للتفاعل الأسبوعي لهذا البلاتفورم.")

        with col_w2:
            st.caption("New bookings per week")
            book_col = weekly_cols_map["bookings"]
            if book_col in last_4.columns:
                chart_df = last_4[["Week", book_col]].set_index("Week")
                st.bar_chart(chart_df)
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
                    chart_df = day_agg[["Day", total_col]].set_index("Day")
                    st.bar_chart(chart_df)
                else:
                    st.info("لا توجد بيانات للتفاعل اليومي لهذا البلاتفورم.")

            with col_d2:
                st.caption("New bookings per day (last 7 days)")
                book_col = daily_cols_map["bookings"]
                if book_col in day_agg.columns:
                    chart_df = day_agg[["Day", book_col]].set_index("Day")
                    st.bar_chart(chart_df)
                else:
                    st.info("لا توجد بيانات للحجوزات اليومية لهذا البلاتفورم.")
        else:
            st.info("لا توجد أعمدة كافية لحساب بيانات آخر ٧ أيام لهذا البلاتفورم.")
