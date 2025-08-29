# Dashboard-Order-Monitoring

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Konfigurasi halaman
st.set_page_config(
    page_title="SCG Order Monitoring - Futuristic",
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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        text-align: center;
        margin: 10px;
    }
    .metric-value {
        font-size: 2.5em;
        font-weight: bold;
        color: #FFFFFF;
        margin: 0;
    }
    .metric-label {
        font-size: 1em;
        color: rgba(255, 255, 255, 0.8);
        margin: 0;
    }
    .section-header {
        font-size: 1.5em;
        font-weight: bold;
        color: #00FF88;
        margin-bottom: 15px;
        border-left: 4px solid #00FF88;
        padding-left: 10px;
    }
    .stPlotlyChart {
        border-radius: 15px;
        background-color: #1E2130;
        padding: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Fungsi untuk membuat metric card yang futuristik
def create_metric_card(label, value, background_color="#667eea"):
    return f"""
    <div class="metric-card" style="background: {background_color};">
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
    except:
        return None

# Sidebar
with st.sidebar:
    st.title("🚀 SCG Order Monitoring")
    st.markdown("---")
    
    uploaded_file = st.file_uploader("Upload Data File", type=['csv', 'xlsx'])
    
    if uploaded_file:
        df = process_uploaded_file(uploaded_file)
        if df is not None:
            st.success("✅ Data loaded successfully!")
            
            # Date filters
            if 'Delivery Date' in df.columns:
                delivery_dates = pd.to_datetime(df['Delivery Date'], errors='coerce').dropna()
                if not delivery_dates.empty:
                    min_date = delivery_dates.min()
                    max_date = delivery_dates.max()
                    date_range = st.date_input(
                        "Delivery Date Range",
                        [min_date, max_date],
                        min_value=min_date,
                        max_value=max_date
                    )

# Main Content
st.title("📊 DAILY DELIVERY MONITORING")
st.markdown("---")

# Display metrics in a futuristic way
if 'df' in locals() and df is not None:
    # Calculate metrics
    total_orders = len(df)
    total_volume = df['Order Qty'].sum() if 'Order Qty' in df.columns else total_orders
    delivered_volume = df[df['Status'] == 'Delivered']['Order Qty'].sum() if all(col in df.columns for col in ['Status', 'Order Qty']) else 0
    pending_orders = len(df[df['Status'] == 'Pending']) if 'Status' in df.columns else 0
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card("TOTAL ORDERS", total_orders, "#FF6B6B"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card("VOLUME ORDER", f"{total_volume:.0f}", "#4ECDC4"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card("VOL DELIVERED", f"{delivered_volume:.0f}", "#45B7D1"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card("PENDING ORDERS", pending_orders, "#F9A826"), unsafe_allow_html=True)

    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">STATUS ORDER(M3)</div>', unsafe_allow_html=True)
        if 'Status' in df.columns:
            status_counts = df['Status'].value_counts()
            fig1 = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Plasma
            )
            fig1.update_traces(textinfo='percent+label')
            fig1.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.markdown('<div class="section-header">VOLUME ORDER vs DELIVERED</div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            name='Volume Order',
            x=['Total'],
            y=[total_volume],
            marker_color='#4ECDC4'
        ))
        fig2.add_trace(go.Bar(
            name='Volume Delivered',
            x=['Total'],
            y=[delivered_volume],
            marker_color='#45B7D1'
        ))
        fig2.update_layout(barmode='group', height=300, showlegend=True)
        st.plotly_chart(fig2, use_container_width=True)

    # Plant Performance
    st.markdown('<div class="section-header">DELIVERY PERFORMANCE BY PLANT(M3)</div>', unsafe_allow_html=True)
    if 'Plant Name' in df.columns and 'Order Qty' in df.columns:
        plant_performance = df.groupby('Plant Name')['Order Qty'].sum().reset_index()
        fig3 = px.bar(
            plant_performance,
            x='Plant Name',
            y='Order Qty',
            color='Plant Name',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig3.update_layout(height=400)
        st.plotly_chart(fig3, use_container_width=True)

    # Data Table
    st.markdown('<div class="section-header">DETAIL DATA</div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True)

else:
    # Placeholder sebelum data diupload
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card("TOTAL ORDERS", "0", "#FF6B6B"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card("VOLUME ORDER", "0", "#4ECDC4"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card("VOL DELIVERED", "0", "#45B7D1"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card("PENDING ORDERS", "0", "#F9A826"), unsafe_allow_html=True)
    
    st.info("📤 Please upload a data file to get started")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>SCG Order Monitoring System • Real-time Dashboard</div>", unsafe_allow_html=True)
