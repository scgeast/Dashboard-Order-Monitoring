import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Konfigurasi halaman
st.set_page_config(
    page_title="SCG Daily Delivery Monitoring",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS untuk styling futuristik
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    .metric-card {
        background: linear-gradient(135deg, #1E3A8A 0%, #0369A1 100%);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        text-align: center;
        margin: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .metric-value {
        font-size: 2.8em;
        font-weight: bold;
        color: #FFFFFF;
        margin: 0;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }
    .metric-label {
        font-size: 1.1em;
        color: rgba(255, 255, 255, 0.9);
        margin: 5px 0 0 0;
        font-weight: 500;
    }
    .section-header {
        font-size: 1.6em;
        font-weight: bold;
        color: #00FF88;
        margin: 25px 0 15px 0;
        padding: 10px 0;
        border-bottom: 2px solid #00FF88;
    }
    .stPlotlyChart {
        border-radius: 20px;
        background: linear-gradient(135deg, #1E2130 0%, #2D3250 100%);
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1E3A8A 0%, #0F172A 100%);
    }
    .stDataFrame {
        border-radius: 15px;
        background: linear-gradient(135deg, #1E2130 0%, #2D3250 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stButton>button {
        background: linear-gradient(135deg, #00FF88 0%, #00CC66 100%);
        color: #000;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Fungsi untuk membuat metric card futuristik
def create_metric_card(label, value, background="linear-gradient(135deg, #1E3A8A 0%, #0369A1 100%)"):
    return f"""
    <div class="metric-card" style="background: {background};">
        <p class="metric-value">{value}</p>
        <p class="metric-label">{label}</p>
    </div>
    """

# Fungsi untuk memproses data
@st.cache_data
def process_uploaded_file(uploaded_file):
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            return None
        
        # Bersihkan data
        df.columns = [str(col).strip() for col in df.columns]
        df = df.dropna(axis=1, how='all')
        df = df.dropna(how='all')
        
        return df
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 20px 0;'>
        <h1 style='color: #00FF88; margin: 0;'>🚀 SCG</h1>
        <p style='color: #FFFFFF; margin: 0;'>Delivery Monitoring</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    uploaded_file = st.file_uploader("📤 Upload Data File", type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file:
        df = process_uploaded_file(uploaded_file)
        if df is not None:
            st.success("✅ Data loaded successfully!")
            st.session_state.df = df

# Main Content
st.markdown("""
<div style='text-align: center; padding: 20px 0;'>
    <h1 style='color: #00FF88; font-size: 2.5em; margin: 0;'>📊 DAILY DELIVERY MONITORING</h1>
    <p style='color: #FFFFFF; margin: 0;'>Real-time Order Tracking System</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Display metrics
if 'df' in st.session_state and st.session_state.df is not None:
    df = st.session_state.df
    
    # Calculate metrics - dengan error handling
    total_orders = len(df)
    
    # Volume calculations dengan error handling
    if 'Order Qty' in df.columns:
        total_volume = df['Order Qty'].sum()
    else:
        total_volume = total_orders  # Fallback jika kolom tidak ada
    
    # Delivered volume
    if all(col in df.columns for col in ['Status', 'Order Qty']):
        delivered_volume = df[df['Status'].str.contains('Delivered', case=False, na=False)]['Order Qty'].sum()
    else:
        delivered_volume = 0
    
    # Pending orders
    if 'Status' in df.columns:
        pending_orders = len(df[df['Status'].str.contains('Pending', case=False, na=False)])
    else:
        pending_orders = 0
    
    # Canceled volume
    if all(col in df.columns for col in ['Status', 'Order Qty']):
        canceled_volume = df[df['Status'].str.contains('Cancel', case=False, na=False)]['Order Qty'].sum()
    else:
        canceled_volume = 0
    
    # Remaining volume
    remaining_volume = total_volume - delivered_volume - canceled_volume

    # Metrics Row 1
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card("TOTAL ORDERS", total_orders, "linear-gradient(135deg, #FF6B6B 0%, #C53030 100%)"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card("VOLUME ORDER", f"{total_volume:.0f}", "linear-gradient(135deg, #4ECDC4 0%, #2C7A7B 100%)"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card("VOL DELIVERED", f"{delivered_volume:.0f}", "linear-gradient(135deg, #45B7D1 0%, #2B6CB0 100%)"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card("VOLUME CANCEL", f"{canceled_volume:.0f}", "linear-gradient(135deg, #F9A826 0%, #D69E2E 100%)"), unsafe_allow_html=True)

    # Metrics Row 2
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card("VOLUME REMAINING", f"{remaining_volume:.0f}", "linear-gradient(135deg, #A3BFFA 0%, #667EEA 100%)"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card("PENDING ORDERS", pending_orders, "linear-gradient(135deg, #F687B3 0%, #D53F8C 100%)"), unsafe_allow_html=True)
    
    with col3:
        delivery_ratio = (delivered_volume / total_volume * 100) if total_volume > 0 else 0
        st.markdown(create_metric_card("DELIVERY RATIO", f"{delivery_ratio:.1f}%", "linear-gradient(135deg, #68D391 0%, #38A169 100%)"), unsafe_allow_html=True)
    
    with col4:
        avg_order_size = (total_volume / total_orders) if total_orders > 0 else 0
        st.markdown(create_metric_card("AVG ORDER SIZE", f"{avg_order_size:.1f}", "linear-gradient(135deg, #FBBF24 0%, #D97706 100%)"), unsafe_allow_html=True)

    # Charts Section
    st.markdown('<div class="section-header">📈 PERFORMANCE DASHBOARD</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Status Order Chart
        st.markdown('<div style="color: #00FF88; font-size: 1.3em; margin-bottom: 15px;">🔄 STATUS ORDER (M3)</div>', unsafe_allow_html=True)
        if 'Status' in df.columns:
            status_data = {
                'DELIVERED': delivered_volume,
                'PENDING': remaining_volume,
                'CANCELED': canceled_volume
            }
            fig1 = px.pie(
                values=list(status_data.values()),
                names=list(status_data.keys()),
                hole=0.5,
                color_discrete_sequence=['#00FF88', '#FF6B6B', '#F9A826']
            )
            fig1.update_traces(textinfo='percent+label+value')
            fig1.update_layout(showlegend=True, height=400, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Volume Comparison Chart
        st.markdown('<div style="color: #00FF88; font-size: 1.3em; margin-bottom: 15px;">📊 VOLUME ORDER vs DELIVERED</div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            name='Volume Order',
            x=['Total Volume'],
            y=[total_volume],
            marker_color='#4ECDC4',
            width=0.4
        ))
        fig2.add_trace(go.Bar(
            name='Volume Delivered',
            x=['Total Volume'],
            y=[delivered_volume],
            marker_color='#00FF88',
            width=0.4
        ))
        fig2.update_layout(
            barmode='group', 
            height=400, 
            showlegend=True,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Plant Performance Section
    st.markdown('<div class="section-header">🏭 DELIVERY PERFORMANCE BY PLANT (M3)</div>', unsafe_allow_html=True)
    
    if 'Plant Name' in df.columns and 'Order Qty' in df.columns:
        plant_performance = df.groupby('Plant Name')['Order Qty'].sum().reset_index()
        fig3 = px.bar(
            plant_performance,
            x='Plant Name',
            y='Order Qty',
            color='Plant Name',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig3.update_layout(
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig3, use_container_width=True)

    # Data Table Section
    st.markdown('<div class="section-header">📋 DETAIL ORDER DATA</div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, height=400)

else:
    # Placeholder sebelum data diupload
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card("TOTAL ORDERS", "0", "linear-gradient(135deg, #666 0%, #333 100%)"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card("VOLUME ORDER", "0", "linear-gradient(135deg, #666 0%, #333 100%)"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card("VOL DELIVERED", "0", "linear-gradient(135deg, #666 0%, #333 100%)"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card("PENDING ORDERS", "0", "linear-gradient(135deg, #666 0%, #333 100%)"), unsafe_allow_html=True)
    
    st.info("""
    📤 **Please upload a data file to get started**
    
    Supported formats: CSV, Excel (.xlsx, .xls)
    
    Your file should contain columns like:
    - Order ID
    - Plant Name  
    - Order Qty
    - Status
    - Delivery Date
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px 0;'>
    <p>🚀 SCG Delivery Monitoring System • Real-time Dashboard • Powered by Streamlit</p>
    <p>📅 Last Updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
</div>
""", unsafe_allow_html=True)
