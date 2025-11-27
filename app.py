import streamlit as st
import pandas as pd
import datetime as dt

GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTbn8mE8Z8QSRfb73Lk63htHUK31I59W5ZDaDTb81dtVK0Q61tczvnfGgGVQMYndidyxG8IdKuuVZ4o/pub?gid=551101663&single=true&output=csv"


@st.cache_data
def load_data():
    df = pd.read_csv(GOOGLE_SHEET_CSV_URL)

    # تأكد إن اسم العمود هو بالظبط Date زي في الشيت
    df["date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["date"])
    return df


df = load_data()

if df.empty:
    st.error("No data found in Google Sheet.")
    st.stop()

# نحسب أقل وأكبر تاريخ من الداتا
min_date = df["date"].min().date()
max_date = df["date"].max().date()

# سايدبار – Quick range
st.sidebar.header("Filters")
quick_range = st.sidebar.selectbox(
    "Quick Range",
    ["Today", "Last 7 days", "This month", "All"],
    index=0,
)

today = max_date  # آخر يوم في الشيت

if quick_range == "Today":
    start_default = today
    end_default = today
elif quick_range == "Last 7 days":
    start_default = max(today - dt.timedelta(days=6), min_date)
    end_default = today
elif quick_range == "This month":
    start_default = today.replace(day=1)
    end_default = today
else:  # All
    start_default = min_date
    end_default = max_date

# نضمن إن الديفولت جوه الرينج
start_default = max(min_date, min(start_default, max_date))
end_default = max(min_date, min(end_default, max_date))

# Date inputs
start_date = st.sidebar.date_input(
    "Start date",
    value=start_default,
    min_value=min_date,
    max_value=max_date,
)

end_date = st.sidebar.date_input(
    "End date",
    value=end_default,
    min_value=start_date,  # ماينفعش تختار نهاية قبل البداية
    max_value=max_date,
)

# نفلتر الداتا
mask = (df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)
df_filtered = df.loc[mask]


with st.sidebar:
    st.header("⚙️ Filters")

    quick = st.selectbox(
        "Quick Range",
        ["All", "Today", "Last 7 Days", "This Month"],
        index=1  # default Today
    )

    today = datetime.now().date()

    if quick == "Today":
        start_date = today
        end_date = today
    elif quick == "Last 7 Days":
        start_date = today - timedelta(days=6)
        end_date = today
    elif quick == "This Month":
        start_date = today.replace(day=1)
        end_date = today
    else:
        start_date = min_date.date()
        end_date = max_date.date()

    start_date = st.date_input("Start date", value=start_date, min_value=min_date.date(), max_value=max_date.date())
    end_date = st.date_input("End date", value=end_date, min_value=min_date.date(), max_value=max_date.date())

# فلترة الداتا
mask = (df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date)
fdf = df[mask].copy()

if fdf.empty:
    st.warning("No data in this date range.")
    st.stop()

# ========= أسماء الأعمدة المستخدمة =========
COLS = {
    "calls": "Total Calls Received",
    "wa_ans": "WhatsApp Answered",
    "ig_ans": "Instagram Answered",
    "tt_ans": "TikTok Answered",
    "nb_ig": "New Bookings - Insta",
    "nb_call": "New Bookings - Call",
    "nb_wa": "New Bookings - Whats",
    "nb_tt": "New Bookings - TikTok",
    "ask_ig": "Asked About Dates - Insta",
    "ask_wa": "Asked About Dates - Whats",
    "ask_tt": "Asked About Dates - TikTok",
    "int_ig": "Interested - Insta",
    "int_wa": "Interested - Whats",
    "int_tt": "Interested - TikTok",
    "not_ig": "Not Interested - Insta",
    "not_wa": "Not Interested - Whats",
    "not_tt": "Not Interested - TikTok",
    "inc_ig": "Incorrect Audience - Insta",
    "inc_wa": "Incorrect Audience - Whats",
    "inc_tt": "Incorrect Audience - TikTok",
    "noans_ig": "Didn’t Answer - Insta",
    "noans_wa": "Didn’t Answer - Whats",
    "noans_tt": "Didn’t Answer - TikTok",
}

# لو عمود ناقص نخليه 0
for c in COLS.values():
    if c not in fdf.columns:
        fdf[c] = 0

# ========= إجماليات الفترة =========
total_calls = int(fdf[COLS["calls"]].sum())
total_wa = int(fdf[COLS["wa_ans"]].sum())
total_ig = int(fdf[COLS["ig_ans"]].sum())
total_tt = int(fdf[COLS["tt_ans"]].sum())

total_new_bookings = int(
    fdf[COLS["nb_ig"]].sum()
    + fdf[COLS["nb_call"]].sum()
    + fdf[COLS["nb_wa"]].sum()
    + fdf[COLS["nb_tt"]].sum()
)

total_interested = int(
    fdf[COLS["int_ig"]].sum()
    + fdf[COLS["int_wa"]].sum()
    + fdf[COLS["int_tt"]].sum()
)

total_not_interested = int(
    fdf[COLS["not_ig"]].sum()
    + fdf[COLS["not_wa"]].sum()
    + fdf[COLS["not_tt"]].sum()
)

total_no_answer = int(
    fdf[COLS["noans_ig"]].sum()
    + fdf[COLS["noans_wa"]].sum()
    + fdf[COLS["noans_tt"]].sum()
)

# ========= كروت الملخص =========
st.subheader(f"Summary ({start_date.strftime('%d/%m/%Y')} → {end_date.strftime('%d/%m/%Y')})")

c1, c2, c3, c4 = st.columns(4)
c1.metric("📞 Total Calls", total_calls)
c2.metric("💬 WhatsApp Answered", total_wa)
c3.metric("📸 Instagram Answered", total_ig)
c4.metric("🎵 TikTok Answered", total_tt)

c5, c6, c7, c8 = st.columns(4)
c5.metric("✅ New Bookings (All)", total_new_bookings)
c6.metric("🤝 Interested", total_interested)
c7.metric("❌ Not Interested", total_not_interested)
c8.metric("🕒 Didn’t Answer", total_no_answer)

st.markdown("---")

# ========= Breakdown بالقنوات =========
st.subheader("New Bookings by Channel")

nb_breakdown = pd.DataFrame({
    "Channel": ["Instagram", "Calls", "WhatsApp", "TikTok"],
    "New Bookings": [
        int(fdf[COLS["nb_ig"]].sum()),
        int(fdf[COLS["nb_call"]].sum()),
        int(fdf[COLS["nb_wa"]].sum()),
        int(fdf[COLS["nb_tt"]].sum()),
    ]
})

col_a, col_b = st.columns(2)

with col_a:
    st.dataframe(nb_breakdown, use_container_width=True)
    st.bar_chart(nb_breakdown.set_index("Channel"))

with col_b:
    st.subheader("Status Distribution (All Channels)")
    status_totals = pd.DataFrame({
        "Status": ["Interested", "Not Interested", "Incorrect Audience", "Didn’t Answer"],
        "Count": [
            total_interested,
            total_not_interested,
            int(
                fdf[COLS["inc_ig"]].sum()
                + fdf[COLS["inc_wa"]].sum()
                + fdf[COLS["inc_tt"]].sum()
            ),
            total_no_answer
        ]
    })
    st.dataframe(status_totals, use_container_width=True)
    st.bar_chart(status_totals.set_index("Status"))

st.markdown("---")

# ========= Daily Trend =========
st.subheader("Daily Trend - New Bookings Total")

fdf["New Bookings Total"] = (
    fdf[COLS["nb_ig"]]
    + fdf[COLS["nb_call"]]
    + fdf[COLS["nb_wa"]]
    + fdf[COLS["nb_tt"]]
)

trend = fdf.groupby("Date")["New Bookings Total"].sum().reset_index()
trend = trend.set_index("Date")

st.line_chart(trend)

# ========= جدول التفاصيل =========
st.markdown("### Raw Daily Data")
show_cols = [
    "Date",
    COLS["calls"],
    COLS["wa_ans"],
    COLS["ig_ans"],
    COLS["tt_ans"],
    COLS["nb_ig"],
    COLS["nb_call"],
    COLS["nb_wa"],
    COLS["nb_tt"],
    COLS["int_ig"],
    COLS["int_wa"],
    COLS["int_tt"],
    COLS["not_ig"],
    COLS["not_wa"],
    COLS["not_tt"],
    COLS["noans_ig"],
    COLS["noans_wa"],
    COLS["noans_tt"],
]

st.dataframe(fdf[show_cols].sort_values("Date"), use_container_width=True)
