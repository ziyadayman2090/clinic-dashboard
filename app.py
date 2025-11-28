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

# Debug function to check column names
def debug_columns(df):
    st.write("### 🔍 Debug - Available Columns:")
    all_cols = list(df.columns)
    st.write(f"Total columns: {len(all_cols)}")
    
    # Check for variations of "Didn't Answer"
    didnt_answer_variations = [col for col in all_cols if "didn" in col.lower() or "answer" in col.lower()]
    st.write("Columns related to 'Didn't Answer':", didnt_answer_variations)
    
    # Check for other important columns
    important_cols = ["total_interactions", "total_new_bookings", "total_interested", "total_not_interested", "total_no_reply"]
    st.write("Calculated columns:", [col for col in important_cols if col in df.columns])
    
    return didnt_answer_variations

@st.cache_data(ttl=5)
def load_data():
    df = pd.read_csv(GOOGLE_SHEET_CSV_URL)

    # نتأكد إن اسم العمود Date مكتوب صح
    if "Date" not in df.columns:
        raise ValueError("Column 'Date' not found in sheet. تأكد إن أول عمود اسمه Date بالظبط.")

    # نحول التاريخ
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date"]).sort_values("Date")

    # Debug: Check what "Didn't Answer" columns exist
    didnt_answer_cols = [col for col in df.columns if "didn" in col.lower() or "answer" in col.lower()]
    
    # Use the correct "Didn't Answer" column name
    didnt_answer_insta = "Didn't Answer - Insta"
    didnt_answer_whats = "Didn't Answer - Whats" 
    didnt_answer_tiktok = "Didn't Answer - TikTok"
    
    # If the columns don't exist, try to find the correct ones
    if didnt_answer_insta not in df.columns and didnt_answer_cols:
        # Try to find the correct column names
        for col in didnt_answer_cols:
            if 'insta' in col.lower():
                didnt_answer_insta = col
            elif 'whats' in col.lower():
                didnt_answer_whats = col
            elif 'tiktok' in col.lower():
                didnt_answer_tiktok = col

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
    df["total_no_reply"] = safe_sum_per_row(
        df,
        [
            didnt_answer_insta,
            didnt_answer_whats,
            didnt_answer_tiktok,
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
# Debug: Check column names
# ======================
with st.expander("🔍 Debug Column Names"):
    debug_columns(df_filtered)

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

# Debug the "Didn't Answer" calculation
with st.expander("🔍 Debug Didn't Answer Calculation"):
    st.write("total_no_reply value:", total_no_reply)
    if "total_no_reply" in df_filtered.columns:
        st.write("total_no_reply column sample:", df_filtered["total_no_reply"].head())
        st.write("total_no_reply sum:", df_filtered["total_no_reply"].sum())
    
    # Check individual "Didn't Answer" columns
    didnt_answer_cols = [col for col in df_filtered.columns if "didn" in col.lower() or "answer" in col.lower()]
    for col in didnt_answer_cols:
        st.write(f"{col} sum: {df_filtered[col].sum()}")

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

# Rest of your code remains the same...
# [Keep all your existing tab code from the previous version]

        




