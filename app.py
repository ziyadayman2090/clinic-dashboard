import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta, date

# ======================
# Modern CSS Styling
# ======================
st.markdown("""
<style>
    /* Modern card design with gradients */
    .modern-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #f0f0f0;
        text-align: center;
        transition: transform 0.2s ease;
        margin: 5px;
        position: relative;
        overflow: hidden;
    }
    .modern-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .modern-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.12);
    }
    .card-icon {
        font-size: 28px;
        margin-bottom: 12px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .card-title {
        font-size: 12px;
        font-weight: 700;
        color: #666;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .card-value {
        font-size: 32px;
        font-weight: 800;
        color: #2c3e50;
        margin: 0;
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .card-subtitle {
        font-size: 11px;
        color: #888;
        margin-top: 5px;
        font-weight: 500;
    }
    
    /* Gradient background cards for platform metrics */
    .gradient-card {
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        margin: 5px;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: relative;
        overflow: hidden;
    }
    .gradient-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.1);
        z-index: 1;
    }
    .gradient-title {
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 8px;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
        position: relative;
        z-index: 2;
    }
    .gradient-value {
        font-size: 36px;
        font-weight: 800;
        margin: 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        position: relative;
        z-index: 2;
    }
    
    /* General dashboard styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f8f9fa;
        border-radius: 8px 8px 0px 0px;
        gap: 8px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

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

def safe_col_sum(df, col_name):
    return int(df[col_name].sum()) if col_name in df.columns else 0

def find_platform_columns(df, platform_name):
    """Dynamically find the correct column names for each platform"""
    platform_lower = platform_name.lower()
    
    # Define possible column patterns for each metric type
    patterns = {
        "total": ["answered", "received", "total"],
        "bookings": ["new bookings", "bookings"],
        "asked_dates": ["asked about dates", "asked dates"],
        "interested": ["interested"],
        "not_interested": ["not interested"],
        "no_reply": ["didn't answer", "didnt answer", "no reply", "no answer"]
    }
    
    found_cols = {}
    
    for metric_type, pattern_list in patterns.items():
        # Look for columns that match the platform and metric pattern
        matching_cols = []
        for col in df.columns:
            col_lower = col.lower()
            # Check if column contains platform name and one of the metric patterns
            if (platform_lower in col_lower or 
                (platform_lower == "calls" and "call" in col_lower)):
                
                for pattern in pattern_list:
                    if pattern in col_lower:
                        matching_cols.append(col)
                        break
        
        # Use the first matching column found, or use the predefined one
        if matching_cols:
            found_cols[metric_type] = matching_cols[0]
        else:
            # Fallback to predefined column name
            predefined_col = PLATFORM_COLS[platform_name][metric_type]
            found_cols[metric_type] = predefined_col if predefined_col in df.columns else None
    
    return found_cols

@st.cache_data(ttl=5)
def load_data():
    df = pd.read_csv(GOOGLE_SHEET_CSV_URL)

    # نتأكد إن اسم العمود Date مكتوب صح
    if "Date" not in df.columns:
        raise ValueError("Column 'Date' not found in sheet. تأكد إن أول عمود اسمه Date بالظبط.")

    # نحول التاريخ
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date"]).sort_values("Date")

    # Find the correct "Didn't Answer" column names
    didnt_answer_cols = [col for col in df.columns if "didn" in col.lower() or "answer" in col.lower()]
    
    # Try different variations of "Didn't Answer" column names
    possible_didnt_answer_columns = [
        ["Didn't Answer - Insta", "Didn't Answer - Whats", "Didn't Answer - TikTok"],
        ["Didn’t Answer - Insta", "Didn’t Answer - Whats", "Didn’t Answer - TikTok"],
        ["Didnt Answer - Insta", "Didnt Answer - Whats", "Didnt Answer - TikTok"],
        ["Didn't Answer- Insta", "Didn't Answer- Whats", "Didn't Answer- TikTok"],
    ]
    
    # Find which set of columns actually exists
    selected_columns = None
    for column_set in possible_didnt_answer_columns:
        if all(col in df.columns for col in column_set):
            selected_columns = column_set
            break
    
    # If no exact match found, use whatever columns we can find
    if selected_columns is None and didnt_answer_cols:
        selected_columns = []
        for platform in ["Insta", "Whats", "TikTok"]:
            platform_cols = [col for col in didnt_answer_cols if platform.lower() in col.lower()]
            if platform_cols:
                selected_columns.append(platform_cols[0])
            else:
                selected_columns.append(None)
    
    # If still no columns found, use empty list
    if selected_columns is None:
        selected_columns = [None, None, None]

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

    # استخدام الأسماء الصحيحة لأعمدة "Didn't Answer"
    valid_didnt_answer_cols = [col for col in selected_columns if col is not None and col in df.columns]
    df["total_no_reply"] = safe_sum_per_row(df, valid_didnt_answer_cols)

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
# Modern KPI Cards
# ======================
st.subheader("📊 Overview Metrics")

# Calculate your metrics with safe checks
total_interactions = int(df_filtered["total_interactions"].sum()) if "total_interactions" in df_filtered.columns else 0
total_new_bookings = int(df_filtered["total_new_bookings"].sum()) if "total_new_bookings" in df_filtered.columns else 0
total_interested = int(df_filtered["total_interested"].sum()) if "total_interested" in df_filtered.columns else 0
total_not_interested = int(df_filtered["total_not_interested"].sum()) if "total_not_interested" in df_filtered.columns else 0
total_no_reply = int(df_filtered["total_no_reply"].sum()) if "total_no_reply" in df_filtered.columns else 0

# Modern cards with icons
metrics_data = [
    {"icon": "💬", "title": "TOTAL INTERACTIONS", "value": total_interactions, "subtitle": "customer engagements"},
    {"icon": "✅", "title": "NEW BOOKINGS", "value": total_new_bookings, "subtitle": "confirmed appointments"},
    {"icon": "🎯", "title": "INTERESTED", "value": total_interested, "subtitle": "potential clients"},
    {"icon": "❌", "title": "NOT INTERESTED", "value": total_not_interested, "subtitle": "declined offers"},
    {"icon": "⏸️", "title": "DIDN'T ANSWER", "value": total_no_reply, "subtitle": "no response"}
]

# Create columns for main metrics
cols = st.columns(5)
for i, (col, metric) in enumerate(zip(cols, metrics_data)):
    with col:
        st.markdown(f"""
        <div class="modern-card">
            <div class="card-icon">{metric['icon']}</div>
            <div class="card-title">{metric['title']}</div>
            <div class="card-value">{metric['value']:,}</div>
            <div class="card-subtitle">{metric['subtitle']}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

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
# تعريف خريطة المنصات (هنستخدمها في أكتر من حتة)
# ======================
PLATFORM_COLS = {
    "Instagram": {
        "total": "Instagram Answered",
        "bookings": "New Bookings - Insta",
        "asked_dates": "Asked About Dates - Insta",
        "interested": "Interested - Insta",
        "not_interested": "Not Interested - Insta",
        "no_reply": "Didn't Answer - Insta",
    },
    "WhatsApp": {
        "total": "WhatsApp Answered",
        "bookings": "New Bookings - Whats",
        "asked_dates": "Asked About Dates - Whats",
        "interested": "Interested - Whats",
        "not_interested": "Not Interested - Whats",
        "no_reply": "Didn't Answer - Whats",
    },
    "TikTok": {
        "total": "TikTok Answered",
        "bookings": "New Bookings - TikTok",
        "asked_dates": "Asked About Dates - TikTok",
        "interested": "Interested - TikTok",
        "not_interested": "Not Interested - TikTok",
        "no_reply": "Didn't Answer - TikTok",
    },
    "Calls": {
        "total": "Total Calls Received",
        "bookings": "New Bookings - Call",
        "asked_dates": "total_asked_dates",       
        "interested": "total_interested",           
        "not_interested": "total_not_interested",  
        "no_reply": "total_no_reply",
    },
}



# ======================
# 2) PLATFORMS TAB
# ======================
with tab_platforms:
    st.subheader("Platform Breakdown (per platform)")

    selected_platform = st.selectbox(
        "Select Platform:",
        ["Instagram", "WhatsApp", "TikTok", "Calls"],
        key="platform_breakdown_select"
    )

    platform_cols = PLATFORM_COLS[selected_platform]

    # Calculate metrics
    total_platform_interactions = safe_col_sum(df_filtered, platform_cols["total"])
    platform_bookings = safe_col_sum(df_filtered, platform_cols["bookings"])
    platform_asked_dates = safe_col_sum(df_filtered, platform_cols["asked_dates"])
    platform_interested = safe_col_sum(df_filtered, platform_cols["interested"])
    platform_not_interested = safe_col_sum(df_filtered, platform_cols["not_interested"])
    
    answered_interactions = (platform_bookings + platform_asked_dates + 
                           platform_interested + platform_not_interested)
    platform_no_reply = max(0, total_platform_interactions - answered_interactions)

    # Platform metrics with gradient cards
    st.subheader(f"📊 {selected_platform} Performance")
    
    platform_metrics = [
        {"title": "TOTAL INTERACTIONS", "value": total_platform_interactions, "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"},
        {"title": "NEW BOOKINGS", "value": platform_bookings, "gradient": "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)"},
        {"title": "ASKED ABOUT DATES", "value": platform_asked_dates, "gradient": "linear-gradient(135deg, #fc466b 0%, #3f5efb 100%)"},
        {"title": "INTERESTED", "value": platform_interested, "gradient": "linear-gradient(135deg, #fdbb2d 0%, #22c1c3 100%)"},
        {"title": "NOT INTERESTED", "value": platform_not_interested, "gradient": "linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)"},
        {"title": "DIDN'T ANSWER", "value": platform_no_reply, "gradient": "linear-gradient(135deg, #8A2387 0%, #E94057 50%, #F27121 100%)"}
    ]
    
    # Create two rows of platform metrics
    row1 = st.columns(3)
    row2 = st.columns(3)
    
    all_cols = row1 + row2
    
    for i, (col, metric) in enumerate(zip(all_cols, platform_metrics)):
        with col:
            st.markdown(f"""
            <div class="gradient-card" style="background: {metric['gradient']};">
                <div class="gradient-title">{metric['title']}</div>
                <div class="gradient-value">{metric['value']}</div>
            </div>
            """, unsafe_allow_html=True)

    # Platform pie chart
    st.markdown("---")
    st.subheader("Platform Distribution")
    
    platform_cols_simple = {
        "Instagram": "Instagram Answered",
        "WhatsApp": "WhatsApp Answered",
        "TikTok": "TikTok Answered",
        "Calls": "Total Calls Received"
    }

    platform_data = {p: df_filtered[c].sum() for p, c in platform_cols_simple.items() if c in df_filtered.columns}
    pie_df = pd.DataFrame(list(platform_data.items()), columns=["Platform", "Count"])
    pie_chart = alt.Chart(pie_df).mark_arc(innerRadius=50).encode(
        theta="Count:Q", color="Platform:N", tooltip=["Platform", "Count"]
    )
    st.altair_chart(pie_chart, use_container_width=True)

    # Platform summary chart
    st.subheader("Performance Summary")
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

    # Platform overview charts
    st.markdown("---")
    st.subheader("Platforms Overview")

    col_left, col_right = st.columns(2)

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
        key="weekly_platform_select"
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
        key="last7_platform_select"
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
#CSS IS WORKING AND CALLS HAVE BEEN CALCULATED
#CSS IS WORKING AND CALLS HAVE BEEN CALCULATED




