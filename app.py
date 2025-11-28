import streamlit as st
import pandas as pd
import altair as alt

# Modern CSS styling for the entire dashboard
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

# Your main dashboard code with integrated styling
def main():
    st.title("AL-Basma Clinic Leads Dashboard")
    
    # Main KPI Metrics with Modern Card Design
    st.subheader("📊 Overview Metrics")
    
    # Calculate your metrics (replace with your actual calculations)
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
    
    # Tab system
    tab_overview, tab_platforms, tab_time = st.tabs(["📈 Overview", "📱 Platforms", "🕐 Time Analysis"])
    
    with tab_overview:
        # Your existing overview content
        row1_col1, row1_col2 = st.columns(2)
        
        with row1_col1:
            st.subheader("Inquiry Trends")
            # Your trend chart code here...
            
        with row1_col2:
            st.subheader("Customer Sentiment")
            # Your sentiment chart code here...
    
    with tab_platforms:
        st.subheader("Platform Breakdown (per platform)")
        
        # Platform selection
        selected_platform = st.selectbox(
            "Select Platform:",
            ["Instagram", "WhatsApp", "TikTok", "Calls"],
            key="platform_breakdown"
        )
        
        # Platform column mapping
        PLATFORM_COLS_DETAILED = {
            "Instagram": {
                "interactions": "Instagram Answered",
                "bookings": "New Bookings - Insta",
                "asked_dates": "Asked About Dates - Insta",
                "interested": "Interested - Insta",
                "not_interested": "Not Interested - Insta",
                "no_reply": "Didn't Answer - Insta"
            },
            "WhatsApp": {
                "interactions": "WhatsApp Answered",
                "bookings": "New Bookings - Whats",
                "asked_dates": "Asked About Dates - Whats",
                "interested": "Interested - Whats",
                "not_interested": "Not Interested - Whats",
                "no_reply": "Didn't Answer - Whats"
            },
            "TikTok": {
                "interactions": "TikTok Answered",
                "bookings": "New Bookings - TikTok",
                "asked_dates": "Asked About Dates - TikTok",
                "interested": "Interested - TikTok",
                "not_interested": "Not Interested - TikTok",
                "no_reply": "Didn't Answer - TikTok"
            },
            "Calls": {
                "interactions": "Total Calls Received",
                "bookings": "New Bookings - Call",
                "asked_dates": "Asked About Dates - Call",
                "interested": "Interested - Call",
                "not_interested": "Not Interested - Call",
                "no_reply": "Didn't Answer - Call"
            }
        }
        
        # Calculate platform-specific metrics
        platform_cols = PLATFORM_COLS_DETAILED[selected_platform]
        total_platform_interactions = int(df_filtered[platform_cols["interactions"]].sum()) if platform_cols["interactions"] in df_filtered.columns else 0
        platform_bookings = int(df_filtered[platform_cols["bookings"]].sum()) if platform_cols["bookings"] in df_filtered.columns else 0
        platform_asked_dates = int(df_filtered[platform_cols["asked_dates"]].sum()) if platform_cols["asked_dates"] in df_filtered.columns else 0
        platform_interested = int(df_filtered[platform_cols["interested"]].sum()) if platform_cols["interested"] in df_filtered.columns else 0
        platform_not_interested = int(df_filtered[platform_cols["not_interested"]].sum()) if platform_cols["not_interested"] in df_filtered.columns else 0
        platform_no_reply = int(df_filtered[platform_cols["no_reply"]].sum()) if platform_cols["no_reply"] in df_filtered.columns else 0
        
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
        
        # Your existing platform charts
        st.markdown("---")
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("Platform Distribution")
            # Your pie chart code here...
            
        with col_right:
            st.subheader("Performance Summary")
            # Your bar chart code here...
    
    with tab_time:
        st.subheader("Time-based Analysis")
        # Your existing time analysis code here...
        
        # You can also use the gradient cards for time-based metrics
        # Example for weekly view:
        st.subheader("Weekly Performance")
        
        # Calculate some time-based metrics
        weekly_interactions = 250  # Replace with actual calculation
        weekly_bookings = 25       # Replace with actual calculation
        weekly_conversion = (weekly_bookings / weekly_interactions * 100) if weekly_interactions > 0 else 0
        
        time_metrics = [
            {"title": "WEEKLY INTERACTIONS", "value": weekly_interactions, "gradient": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"},
            {"title": "WEEKLY BOOKINGS", "value": weekly_bookings, "gradient": "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)"},
            {"title": "CONVERSION RATE", "value": f"{weekly_conversion:.1f}%", "gradient": "linear-gradient(135deg, #fa709a 0%, #fee140 100%)"}
        ]
        
        time_cols = st.columns(3)
        for i, (col, metric) in enumerate(zip(time_cols, time_metrics)):
            with col:
                st.markdown(f"""
                <div class="gradient-card" style="background: {metric['gradient']};">
                    <div class="gradient-title">{metric['title']}</div>
                    <div class="gradient-value">{metric['value']}</div>
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()


        




