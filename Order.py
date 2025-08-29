import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Konfigurasi halaman
st.set_page_config(
    page_title="Order & Delivery Monitoring Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS untuk styling
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    .metric-card {
        background: linear-gradient(135deg, #1E3A8A 0%, #0369A1 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        text-align: center;
        margin: 5px;
    }
    .metric-value {
        font-size: 2.2em;
        font-weight: bold;
        color: #FFFFFF;
        margin: 0;
    }
    .metric-label {
        font-size: 0.9em;
        color: rgba(255, 255, 255, 0.8);
        margin: 5px 0 0 0;
    }
    .section-header {
        font-size: 1.4em;
        font-weight: bold;
        color: #00FF88;
        margin: 20px 0 10px 0;
        padding: 8px 0;
        border-bottom: 2px solid #00FF88;
    }
    .stPlotlyChart {
        border-radius: 15px;
        background: linear-gradient(135deg, #1E2130 0%, #2D3250 100%);
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1E3A8A 0%, #0F172A 100%);
    }
    .stDataFrame {
        border-radius: 10px;
        background: linear-gradient(135deg, #1E2130 0%, #2D3250 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stButton>button {
        background: linear-gradient(135deg, #00FF88 0%, #00CC66 100%);
        color: #000;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: bold;
    }
    /* Data label styling */
    .data-label {
        font-size: 11px;
        font-weight: bold;
        fill: #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)

# Fungsi untuk membuat metric card
def create_metric_card(label, value, background="linear-gradient(135deg, #1E3A8A 0%, #0369A1 100%)"):
    return f"""
    <div class="metric-card" style="background: {background};">
        <p class="metric-value">{value}</p>
        <p class="metric-label">{label}</p>
    </div>
    """

# Fungsi untuk memproses data
@st.cache_data
def process_uploaded_file(uploaded_file, header_row=0):
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=header_row)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file, engine='openpyxl', header=header_row)
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

# Fungsi untuk menemukan kolom
def find_column(df, target_names):
    target_names = [str(name).lower().replace(' ', '').replace('_', '') for name in target_names]
    
    for col in df.columns:
        normalized_col = str(col).lower().replace(' ', '').replace('_', '')
        for target in target_names:
            if normalized_col == target:
                return col
    return None

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'col_mapping' not in st.session_state:
    st.session_state.col_mapping = {}

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 15px 0;'>
        <h2 style='color: #00FF88; margin: 0;'>📊 FILTERS</h2>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    # Upload File
    uploaded_file = st.file_uploader("📤 Upload Data File", type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file:
        df = process_uploaded_file(uploaded_file)
        if df is not None:
            st.session_state.df = df
            st.success("✅ Data loaded successfully!")
            
            # Auto-detect columns
            col_mapping = {
                'CreateDate': find_column(df, ['CreateDate', 'Create Date', 'TanggalBuat']),
                'DeliveryDate': find_column(df, ['Delivery Date', 'DeliveryDate', 'TanggalKirim']),
                'PlantName': find_column(df, ['Plant Name', 'PlantName', 'NamaPlant']),
                'Status': find_column(df, ['Status', 'OrderStatus']),
                'PaymentType': find_column(df, ['Payment Type', 'PaymentType', 'TipePembayaran']),
                'OrderQty': find_column(df, ['Order Qty', 'OrderQty', 'Quantity']),
                'ActualDelivery': find_column(df, ['Actual Delivery', 'ActualDelivery', 'DeliveredQty']),
                'OrderID': find_column(df, ['Order ID', 'OrderID']),
                'SiteNo': find_column(df, ['Site No', 'SiteNo']),
                'SiteName': find_column(df, ['Site Name', 'SiteName'])
            }
            st.session_state.col_mapping = col_mapping
            
            # Display detected columns
            st.info("🔍 Detected Columns:")
            for display_name, actual_col in col_mapping.items():
                if actual_col:
                    st.write(f"• {display_name}: `{actual_col}`")
            
            st.markdown("---")
            
            # Filters
            if col_mapping['CreateDate']:
                create_dates = pd.to_datetime(df[col_mapping['CreateDate']], errors='coerce').dropna()
                if not create_dates.empty:
                    min_date = create_dates.min()
                    max_date = create_dates.max()
                    create_date_range = st.date_input(
                        "📅 Create Date Range",
                        [min_date, max_date],
                        min_value=min_date,
                        max_value=max_date
                    )
            
            if col_mapping['DeliveryDate']:
                delivery_dates = pd.to_datetime(df[col_mapping['DeliveryDate']], errors='coerce').dropna()
                if not delivery_dates.empty:
                    min_date = delivery_dates.min()
                    max_date = delivery_dates.max()
                    delivery_date_range = st.date_input(
                        "🚚 Delivery Date Range",
                        [min_date, max_date],
                        min_value=min_date,
                        max_value=max_date
                    )
            
            if col_mapping['PlantName']:
                plant_options = df[col_mapping['PlantName']].unique()
                plant_options = [str(opt) for opt in plant_options if pd.notna(opt)]
                selected_plants = st.multiselect(
                    "🏭 Plant Name",
                    options=plant_options,
                    default=plant_options,
                    help="Select all plants or choose specific ones"
                )
                
                # Add "Select All" functionality
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Select All Plants", key="select_all_plants"):
                        selected_plants = plant_options
                with col2:
                    if st.button("Clear All", key="clear_all_plants"):
                        selected_plants = []
            
            if col_mapping['Status']:
                status_options = df[col_mapping['Status']].unique()
                status_options = [str(opt) for opt in status_options if pd.notna(opt)]
                selected_status = st.multiselect(
                    "📋 Status",
                    options=status_options,
                    default=status_options,
                    help="Select all statuses or choose specific ones"
                )
                
                # Add "Select All" functionality
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Select All Status", key="select_all_status"):
                        selected_status = status_options
                with col2:
                    if st.button("Clear All", key="clear_all_status"):
                        selected_status = []
            
            if col_mapping['PaymentType']:
                payment_options = df[col_mapping['PaymentType']].unique()
                payment_options = [str(opt) for opt in payment_options if pd.notna(opt)]
                selected_payment = st.multiselect(
                    "💳 Payment Type",
                    options=payment_options,
                    default=payment_options
                )
            
            # Store filter values in session state
            st.session_state.filters = {
                'create_date_range': create_date_range if 'create_date_range' in locals() else None,
                'delivery_date_range': delivery_date_range if 'delivery_date_range' in locals() else None,
                'selected_plants': selected_plants if 'selected_plants' in locals() else None,
                'selected_status': selected_status if 'selected_status' in locals() else None,
                'selected_payment': selected_payment if 'selected_payment' in locals() else None
            }

# Main Content
col1, col2 = st.columns([0.97, 0.03])
with col1:
    st.markdown("""
    <div style='text-align: center; padding: 15px 0;'>
        <h1 style='color: #00FF88; font-size: 2.2em; margin: 0;'>📊 Order & Delivery Monitoring Dashboard</h1>
    </div>
    """, unsafe_allow_html=True)
with col2:
    if st.button("☰"):
        st.session_state.sidebar_expanded = not st.session_state.get('sidebar_expanded', True)

st.markdown("---")

# Display data and visualizations
if st.session_state.df is not None and st.session_state.col_mapping:
    df = st.session_state.df
    col_mapping = st.session_state.col_mapping
    filters = st.session_state.get('filters', {})
    
    # Apply filters
    filtered_df = df.copy()
    
    if filters.get('create_date_range') and col_mapping['CreateDate']:
        mask = pd.to_datetime(filtered_df[col_mapping['CreateDate']], errors='coerce').between(
            pd.to_datetime(filters['create_date_range'][0]),
            pd.to_datetime(filters['create_date_range'][1])
        )
        filtered_df = filtered_df[mask]
    
    if filters.get('delivery_date_range') and col_mapping['DeliveryDate']:
        mask = pd.to_datetime(filtered_df[col_mapping['DeliveryDate']], errors='coerce').between(
            pd.to_datetime(filters['delivery_date_range'][0]),
            pd.to_datetime(filters['delivery_date_range'][1])
        )
        filtered_df = filtered_df[mask]
    
    if filters.get('selected_plants') and col_mapping['PlantName']:
        filtered_df = filtered_df[filtered_df[col_mapping['PlantName']].isin(filters['selected_plants'])]
    
    if filters.get('selected_status') and col_mapping['Status']:
        filtered_df = filtered_df[filtered_df[col_mapping['Status']].isin(filters['selected_status'])]
    
    if filters.get('selected_payment') and col_mapping['PaymentType']:
        filtered_df = filtered_df[filtered_df[col_mapping['PaymentType']].isin(filters['selected_payment'])]
    
    # Calculate metrics
    total_orders = len(filtered_df)
    
    if col_mapping['OrderQty']:
        total_qty = filtered_df[col_mapping['OrderQty']].sum()
    else:
        total_qty = total_orders
    
    if col_mapping['PaymentType']:
        cash_count = len(filtered_df[filtered_df[col_mapping['PaymentType']].astype(str).str.contains('Cash', case=False, na=False)])
        credit_count = len(filtered_df[filtered_df[col_mapping['PaymentType']].astype(str).str.contains('Credit', case=False, na=False)])
        cash_ratio = f"{cash_count}/{credit_count}"
    else:
        cash_ratio = "N/A"
    
    # Calculate Order vs Actual Delivery
    if col_mapping['OrderQty'] and col_mapping['ActualDelivery']:
        total_order_qty = filtered_df[col_mapping['OrderQty']].sum()
        total_actual_delivery = filtered_df[col_mapping['ActualDelivery']].sum()
        delivery_ratio = (total_actual_delivery / total_order_qty * 100) if total_order_qty > 0 else 0
        delivery_metric = f"{delivery_ratio:.1f}%"
    else:
        delivery_metric = "N/A"
        total_order_qty = 0
        total_actual_delivery = 0
    
    # Summary Cards (3 kotak saja)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(create_metric_card("TOTAL ORDERS", total_orders, "linear-gradient(135deg, #FF6B6B 0%, #C53030 100%)"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card("TOTAL ORDER QTY", f"{total_qty:.0f}", "linear-gradient(135deg, #4ECDC4 0%, #2C7A7B 100%)"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card("CASH vs CREDIT", cash_ratio, "linear-gradient(135deg, #45B7D1 0%, #2B6CB0 100%)"), unsafe_allow_html=True)
    
    # Charts
    st.markdown('<div class="section-header">📈 CHARTS & VISUALIZATIONS</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Status Order Bar Chart dengan data labels
        if col_mapping['Status']:
            status_counts = filtered_df[col_mapping['Status']].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            fig1 = px.bar(
                status_counts,
                x='Status',
                y='Count',
                title='📊 Orders by Status',
                color='Status',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            # Tambahkan data labels
            fig1.update_traces(
                texttemplate='%{y}', 
                textposition='outside',
                textfont=dict(size=12, color='white')
            )
            fig1.update_layout(
                showlegend=False, 
                height=400,
                uniformtext_minsize=8,
                uniformtext_mode='hide'
            )
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Order vs Actual Delivery Bar Chart
        if col_mapping['OrderQty'] and col_mapping['ActualDelivery']:
            comparison_data = pd.DataFrame({
                'Type': ['Order Quantity', 'Actual Delivery'],
                'Value': [total_order_qty, total_actual_delivery]
            })
            
            fig2 = px.bar(
                comparison_data,
                x='Type',
                y='Value',
                title='📦 Order vs Actual Delivery (Total Volume)',
                color='Type',
                color_discrete_sequence=['#4ECDC4', '#00FF88']
            )
            # Tambahkan data labels
            fig2.update_traces(
                texttemplate='%{y:,.0f}', 
                textposition='outside',
                textfont=dict(size=12, color='white')
            )
            fig2.update_layout(
                showlegend=False, 
                height=400,
                yaxis_title='Volume'
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Data for Order vs Actual Delivery not available")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Order Trend Line Chart dengan data labels
        if col_mapping['CreateDate']:
            try:
                filtered_df['CreateDate_parsed'] = pd.to_datetime(filtered_df[col_mapping['CreateDate']], errors='coerce')
                daily_orders = filtered_df.groupby(filtered_df['CreateDate_parsed'].dt.date).size().reset_index()
                daily_orders.columns = ['Date', 'Orders']
                fig3 = px.line(
                    daily_orders,
                    x='Date',
                    y='Orders',
                    title='📈 Daily Order Trend',
                    markers=True
                )
                # Tambahkan data labels
                fig3.update_traces(
                    texttemplate='%{y}',
                    textposition='top center',
                    textfont=dict(size=10, color='white')
                )
                fig3.update_layout(height=400)
                st.plotly_chart(fig3, use_container_width=True)
            except:
                st.warning("Could not create trend chart")
    
    with col2:
        # Plant Performance Bar Chart dengan data labels
        if col_mapping['PlantName'] and col_mapping['OrderQty']:
            plant_performance = filtered_df.groupby(col_mapping['PlantName'])[col_mapping['OrderQty']].sum().reset_index()
            plant_performance.columns = ['Plant', 'TotalQty']
            fig4 = px.bar(
                plant_performance,
                x='Plant',
                y='TotalQty',
                title='🏭 Order Quantity by Plant',
                color='Plant',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            # Tambahkan data labels
            fig4.update_traces(
                texttemplate='%{y:,.0f}',
                textposition='outside',
                textfont=dict(size=10, color='white')
            )
            fig4.update_layout(
                showlegend=False, 
                height=400,
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig4, use_container_width=True)
    
    # Data Table
    st.markdown('<div class="section-header">📋 DETAILED ORDER DATA</div>', unsafe_allow_html=True)
    
    # Select columns to display
    display_columns = []
    for col_key in ['OrderID', 'SiteNo', 'SiteName', 'DeliveryDate', 'PlantName', 'OrderQty', 'Status', 'CreateDate', 'PaymentType']:
        if col_mapping[col_key]:
            display_columns.append(col_mapping[col_key])
    
    if display_columns:
        st.dataframe(filtered_df[display_columns], use_container_width=True, height=400)
        
        # Download button
        csv = filtered_df[display_columns].to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name="filtered_orders.csv",
            mime="text/csv"
        )
    else:
        st.warning("No columns available for display")

else:
    # Placeholder before data upload
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(create_metric_card("TOTAL ORDERS", "0", "linear-gradient(135deg, #666 0%, #333 100%)"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card("TOTAL ORDER QTY", "0", "linear-gradient(135deg, #666 0%, #333 100%)"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card("CASH vs CREDIT", "0/0", "linear-gradient(135deg, #666 0%, #333 100%)"), unsafe_allow_html=True)
    
    st.info("""
    📤 **Please upload a data file to get started**
    
    Supported formats: CSV, Excel (.xlsx, .xls)
    
    Your file should contain columns like:
    - Order ID, Site No, Site Name
    - Delivery Date, Plant Name  
    - Order Qty, Actual Delivery, Status
    - CreateDate, Payment Type
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 15px 0;'>
    <p>🚀 Order & Delivery Monitoring System • Real-time Dashboard • Powered by Streamlit</p>
    <p>📅 Last Updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
</div>
""", unsafe_allow_html=True)
