# Dashboard-Order-Monitoring

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
import re

# Konfigurasi halaman
st.set_page_config(
    page_title="Order & Delivery Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fungsi untuk menemukan kolom dengan case-insensitive dan spasi-insensitive
def find_column(df, target_names):
    """
    Mencari kolom dalam dataframe berdasarkan nama target
    yang case-insensitive dan spasi-insensitive
    """
    target_names = [str(name).lower().replace(' ', '').replace('_', '') for name in target_names]
    
    for col in df.columns:
        normalized_col = str(col).lower().replace(' ', '').replace('_', '')
        for target in target_names:
            if normalized_col == target:
                return col
    return None

# Fungsi untuk memproses data yang diupload
@st.cache_data
def process_uploaded_file(uploaded_file):
    try:
        # Baca file yang diupload
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            try:
                df = pd.read_excel(uploaded_file, engine='openpyxl')
            except ImportError:
                st.error("Library openpyxl tidak terinstall. Silakan install dengan: pip install openpyxl")
                return None
        else:
            st.error("Format file tidak didukung. Silakan upload file CSV atau Excel.")
            return None
        
        # Normalisasi nama kolom
        df.columns = [str(col).strip() for col in df.columns]
        
        return df
        
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

# Sidebar dengan filter dan upload
with st.sidebar:
    st.title("📊 Filter Dashboard")
    
    # Upload File
    uploaded_file = st.file_uploader(
        "Upload File Data (CSV atau Excel)",
        type=['csv', 'xlsx', 'xls'],
        help="Upload file data order Anda"
    )
    
    if uploaded_file is not None:
        # Process uploaded file
        df = process_uploaded_file(uploaded_file)
        
        if df is not None:
            # Temukan kolom dengan smart detection
            create_date_col = find_column(df, ['CreateDate', 'Create Date', 'TanggalBuat', 'Tanggal Buat'])
            delivery_date_col = find_column(df, ['Delivery Date', 'DeliveryDate', 'TanggalKirim', 'Tanggal Kirim'])
            plant_name_col = find_column(df, ['Plant Name', 'PlantName', 'NamaPlant', 'Nama Plant'])
            status_col = find_column(df, ['Status', 'OrderStatus', 'StatusOrder'])
            payment_type_col = find_column(df, ['Payment Type', 'PaymentType', 'TipePembayaran', 'Tipe Pembayaran'])
            order_qty_col = find_column(df, ['Order Qty', 'OrderQty', 'Quantity', 'Qty'])
            order_id_col = find_column(df, ['Order ID', 'OrderID', 'IDOrder', 'Order No'])
            
            # Tampilkan mapping kolom yang terdeteksi
            st.info("🔍 Kolom yang terdeteksi:")
            col_mapping = {
                'Create Date': create_date_col,
                'Delivery Date': delivery_date_col,
                'Plant Name': plant_name_col,
                'Status': status_col,
                'Payment Type': payment_type_col,
                'Order Qty': order_qty_col,
                'Order ID': order_id_col
            }
            
            for display_name, actual_col in col_mapping.items():
                if actual_col:
                    st.write(f"{display_name}: `{actual_col}`")
                else:
                    st.warning(f"{display_name}: Tidak ditemukan")
            
            # Filter tanggal: Create Date
            if create_date_col:
                create_date_min = df[create_date_col].min()
                create_date_max = df[create_date_col].max()
                create_date_range = st.date_input(
                    "Create Date Range",
                    [create_date_min, create_date_max],
                    min_value=create_date_min,
                    max_value=create_date_max
                )
            
            # Filter tanggal: Delivery Date
            if delivery_date_col:
                delivery_date_min = df[delivery_date_col].min()
                delivery_date_max = df[delivery_date_col].max()
                delivery_date_range = st.date_input(
                    "Delivery Date Range",
                    [delivery_date_min, delivery_date_max],
                    min_value=delivery_date_min,
                    max_value=delivery_date_max
                )
            
            # Filter Plant Name
            if plant_name_col:
                plant_options = df[plant_name_col].unique()
                selected_plant = st.multiselect("Plant Name", plant_options, default=plant_options)
            
            # Filter Status
            if status_col:
                status_options = df[status_col].unique()
                selected_status = st.multiselect("Status", status_options, default=status_options)
            
            # Filter Payment Type
            if payment_type_col:
                payment_options = df[payment_type_col].unique()
                selected_payment = st.multiselect("Payment Type", payment_options, default=payment_options)
    else:
        st.info("Silakan upload file data untuk memulai")
        df = None

# Main content
st.title("📦 Order & Delivery Monitoring Dashboard")

if df is not None and uploaded_file is not None:
    # Terapkan filter ke dataframe
    filter_conditions = []
    
    if create_date_col and 'create_date_range' in locals():
        filter_conditions.append(
            df[create_date_col].between(pd.to_datetime(create_date_range[0]), pd.to_datetime(create_date_range[1]))
        )
    
    if delivery_date_col and 'delivery_date_range' in locals():
        filter_conditions.append(
            df[delivery_date_col].between(pd.to_datetime(delivery_date_range[0]), pd.to_datetime(delivery_date_range[1]))
        )
    
    if plant_name_col and 'selected_plant' in locals():
        filter_conditions.append(df[plant_name_col].isin(selected_plant))
    
    if status_col and 'selected_status' in locals():
        filter_conditions.append(df[status_col].isin(selected_status))
    
    if payment_type_col and 'selected_payment' in locals():
        filter_conditions.append(df[payment_type_col].isin(selected_payment))
    
    # Gabungkan semua kondisi filter
    if filter_conditions:
        mask = filter_conditions[0]
        for condition in filter_conditions[1:]:
            mask = mask & condition
        filtered_df = df[mask]
    else:
        filtered_df = df
    
    # Tampilkan summary cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Orders", len(filtered_df))
    
    with col2:
        if order_qty_col:
            total_qty = filtered_df[order_qty_col].sum()
            st.metric("Total Order Qty", int(total_qty))
        else:
            st.metric("Total Orders", len(filtered_df))
    
    with col3:
        if payment_type_col:
            cash_count = len(filtered_df[filtered_df[payment_type_col].astype(str).str.contains('Cash', case=False, na=False)])
            credit_count = len(filtered_df[filtered_df[payment_type_col].astype(str).str.contains('Credit', case=False, na=False)])
            st.metric("Cash vs Credit", f"{cash_count}:{credit_count}")
    
    with col4:
        st.metric("Filtered Data", len(filtered_df))
    
    # Grafik: Order by Status
    if status_col:
        fig_status = px.bar(filtered_df, x=status_col, title="Orders by Status")
        st.plotly_chart(fig_status, use_container_width=True)
    
    # Grafik: Payment Type
    if payment_type_col:
        fig_payment = px.pie(filtered_df, names=payment_type_col, title="Payment Type Distribution")
        st.plotly_chart(fig_payment, use_container_width=True)
    
    # Tampilkan tabel data
    st.subheader("Detail Data")
    st.dataframe(filtered_df)
    
    # Download button untuk data yang sudah difilter
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name="filtered_orders.csv",
        mime="text/csv"
    )
else:
    st.info("📤 Silakan upload file data melalui sidebar di sebelah kiri untuk memulai analisis.")
