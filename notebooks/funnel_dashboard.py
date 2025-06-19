# funnel_dashboard.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

# Configure the page
st.set_page_config(
    page_title="Funnel Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {padding: 2rem;}
    .metric-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .stPlotlyChart {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("📈 E-Commerce Funnel Analysis Dashboard")
st.markdown("""
Analyze user behavior through key conversion funnel stages to identify drop-off points and optimize performance.
""")

# Load data
@st.cache_data
def load_data():
    try:
        funnel_metrics = pd.read_csv('funnel_metrics.csv')
        device_analysis = pd.read_csv('device_analysis.csv')
        time_analysis = pd.read_csv('time_analysis.csv')
        traffic_analysis = pd.read_csv('traffic_analysis.csv')
        return funnel_metrics, device_analysis, time_analysis, traffic_analysis
    except FileNotFoundError as e:
        st.error(f"Data file not found: {e}")
        st.stop()

funnel_metrics, device_analysis, time_analysis, traffic_analysis = load_data()

# Sidebar filters
st.sidebar.header("Filters")
show_raw_data = st.sidebar.checkbox("Show raw data", False)
analysis_type = st.sidebar.radio(
    "Analysis Focus",
    ["Overview", "Device Breakdown", "Traffic Sources", "Time Analysis"]
)

# Main dashboard
if analysis_type == "Overview":
    # Overview metrics
    st.header("Funnel Overview")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Users", funnel_metrics['users'].iloc[0])
    with col2:
        st.metric("Final Conversion", f"{funnel_metrics['conversion_rate'].iloc[-1]*100:.1f}%")
    with col3:
        max_drop_idx = funnel_metrics['drop_off_pct'].idxmax()
        st.metric("Biggest Drop-off", 
                 f"{funnel_metrics.loc[max_drop_idx, 'event'].replace('_', ' ').title()} ({funnel_metrics.loc[max_drop_idx, 'drop_off_pct']}%)")

    # Funnel visualization
    st.subheader("Conversion Funnel")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.set_style("whitegrid")
    palette = sns.color_palette("Blues_d", len(funnel_metrics))

    ax = sns.barplot(
        x='event', 
        y='users', 
        data=funnel_metrics,
        palette=palette
    )

    # Format labels
    stage_labels = [s.replace('_', ' ').title() for s in funnel_metrics['event']]

    # Annotate conversion rates
    for i, row in enumerate(funnel_metrics.itertuples()):
        ax.text(
            i, 
            row.users + 20, 
            f"{row.conversion_rate*100:.1f}%", 
            ha='center',
            fontweight='bold',
            fontsize=11
        )
        
    # Annotate drop-offs
    for i in range(1, len(funnel_metrics)):
        prev = funnel_metrics.iloc[i-1]['users']
        curr = funnel_metrics.iloc[i]['users']
        drop_pct = funnel_metrics.iloc[i]['drop_off_pct']
        
        ax.text(
            i-0.5, 
            (prev + curr)/2, 
            f"▼ {drop_pct}%", 
            ha='center',
            color='red',
            fontsize=10,
            fontweight='bold'
        )

    plt.title('User Conversion Funnel', fontsize=16)
    plt.xlabel('Funnel Stage')
    plt.ylabel('Number of Users')
    plt.xticks(ticks=range(len(stage_labels)), labels=stage_labels, rotation=15)
    plt.ylim(0, funnel_metrics['users'].max() * 1.25)
    st.pyplot(fig)

elif analysis_type == "Device Breakdown":
    st.header("Device Performance Analysis")
    
    # Device conversion rates
    st.subheader("Conversion by Device Type")
    device_cols = [col for col in device_analysis.columns if '_conv' in col]
    device_conv = device_analysis[['event'] + device_cols].copy()
    device_conv.columns = ['event'] + [col.replace('_conv', '') for col in device_cols]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    device_conv.set_index('event').plot(kind='bar', ax=ax)
    plt.title('Conversion Rates by Device')
    plt.ylabel('Conversion Rate')
    plt.xticks(rotation=15)
    st.pyplot(fig)

elif analysis_type == "Traffic Sources":
    st.header("Traffic Source Analysis")
    
    # Traffic source conversion
    st.subheader("Conversion by Acquisition Channel")
    if not traffic_analysis.empty:
        traffic_pivot = traffic_analysis.pivot(
            index='event', 
            columns='traffic_source', 
            values='users'
        )
        
        fig, ax = plt.subplots(figsize=(12, 6))
        traffic_pivot.plot(kind='bar', ax=ax)
        plt.title('Conversion Rates by Traffic Source')
        plt.ylabel('Conversion Rate')
        plt.xticks(rotation=15)
        st.pyplot(fig)
    else:
        st.warning("No traffic source data available")

elif analysis_type == "Time Analysis":
    st.header("Time Between Stages Analysis")
    
    if not time_analysis.empty:
        st.subheader("Average Time Between Stages (minutes)")
        fig, ax = plt.subplots(figsize=(10, 5))
        time_analysis.set_index('event')['avg_time_min'].plot(kind='bar', ax=ax)
        plt.title('Time Between Funnel Stages')
        plt.ylabel('Minutes')
        plt.xticks(rotation=15)
        st.pyplot(fig)
    else:
        st.warning("No time analysis data available")

# Raw data view
if show_raw_data:
    st.header("Raw Data")
    st.subheader("Funnel Metrics")
    st.dataframe(funnel_metrics)
    
    st.subheader("Device Analysis")
    st.dataframe(device_analysis)
    
    if not traffic_analysis.empty:
        st.subheader("Traffic Analysis")
        st.dataframe(traffic_analysis)
    
    if not time_analysis.empty:
        st.subheader("Time Analysis")
        st.dataframe(time_analysis)

# Footer
st.markdown("---")
st.markdown("""
**Funnel Analysis Dashboard**  
Analyzing user behavior from landing to purchase.  
*Data updated: {}*  
""".format(pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")))