# ======================
# Last 4 weeks per platform (بلاتفورم واحد × ٤ أسابيع)
# ======================
st.subheader("Last 4 weeks per platform")

weekly_platform = st.selectbox(
    "Choose platform (weekly view):",
    ["Instagram", "WhatsApp", "TikTok", "Calls"],
    index=0,
)

# نستخدم نفس الخريطة بتاعة PLATFORM_COLS اللي فوق
weekly_cols_map = PLATFORM_COLS[weekly_platform]

# نجهز بيانات الأسابيع
df_weeks = df_filtered.copy()
df_weeks["week_start"] = df_weeks["Date"].dt.to_period("W").apply(
    lambda r: r.start_time.date()
)

# نجمع على مستوى الأسبوع للتفاعل والحجوزات
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

    # آخر ٤ أسابيع
    last_4 = week_agg.tail(4).copy()
    last_4["Week"] = last_4["week_start"].astype(str)

    col_w1, col_w2 = st.columns(2)

    # -------- Interactions per week --------
    with col_w1:
        st.caption("Interactions per week")
        total_col = weekly_cols_map["total"]
        if total_col in last_4.columns:
            chart_df = last_4[["Week", total_col]].set_index("Week")
            st.bar_chart(chart_df)
        else:
            st.info("لا توجد بيانات للتفاعل الأسبوعي لهذا البلاتفورم.")

    # -------- New bookings per week --------
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
