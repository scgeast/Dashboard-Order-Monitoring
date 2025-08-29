# Dashboard-Order-Monitoring

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

# Konfigurasi halaman
st.set_page_config(
    page_title="Order & Delivery Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fungsi untuk memproses data yang diupload
@st.cache_data
def process_uploaded_file(uploaded_file):
    try:
        # Baca file yang diupload
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Format file tidak didukung. Silakan upload file CSV atau Excel.")
            return None
        
        # Bersihkan nama kolom (remove extra spaces, lowercase, etc.)
        df.columns = df.columns.str.strip().str.title()
        
        # Pastikan kolom-kolom penting ada
        required_columns = ['Order ID', 'Delivery Date', 'Plant Name', 'Status', 'CreateDate', 'Payment Type']
        for col in required_columns:
            if col not in df.columns:
                st.warning(f"Kolom '{col}' tidak ditemukan dalam data. Beberapa fitur mungkin tidak bekerja.")
        
        # Convert date columns jika ada
        date_columns = ['Delivery Date', 'CreateDate']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
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
            # Filter tanggal: Create Date
            if 'CreateDate' in df.columns:
                create_date_min = df["CreateDate"].min()
                create_date_max = df["CreateDate"].max()
                create_date_range = st.date_input(
                    "Create Date Range",
                    [create_date_min, create_date_max],
                    min_value=create_date_min,
                    max_value=create_date_max
                )
            
            # Filter tanggal: Delivery Date
            if 'Delivery Date' in df.columns:
                delivery_date_min = df["Delivery Date"].min()
                delivery_date_max = df["Delivery Date"].max()
                delivery_date_range = st.date_input(
                    "Delivery Date Range",
                    [delivery_date_min, delivery_date_max],
                    min_value=delivery_date_min,
                    max_value=delivery_date_max
                )
            
            # Filter Plant Name
            if 'Plant Name' in df.columns:
                plant_options = df["Plant Name"].unique()
                selected_plant = st.multiselect("Plant Name", plant_options, default=plant_options)
            
            # Filter Status
            if 'Status' in df.columns:
                status_options = df["Status"].unique()
                selected_status = st.multiselect("Status", status_options, default=status_options)
            
            # Filter Payment Type
            if 'Payment Type' in df.columns:
                payment_options = df["Payment Type"].unique()
                selected_payment = st.multiselect("Payment Type", payment_options, default=payment_options)
    else:
        st.info("Silakan upload file data untuk memulai")
        df = None

# Main content
st.title("📦 Order & Delivery Monitoring Dashboard")

if df is not None:
    # Terapkan filter ke dataframe
    mask = (
        df["CreateDate"].between(pd.to_datetime(create_date_range[0]), pd.to_datetime(create_date_range[1])) &
        df["Delivery Date"].between(pd.to_datetime(delivery_date_range[0]), pd.to_datetime(delivery_date_range[1])) &
        df["Plant Name"].isin(selected_plant) &
        df["Status"].isin(selected_status) &
        df["Payment Type"].isin(selected_payment)
    )
    filtered_df = df[mask]
    
    # Tampilkan summary cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Orders", len(filtered_df))
    with col2:
        if 'Order Qty' in filtered_df.columns:
            st.metric("Total Order Qty", filtered_df["Order Qty"].sum())
        else:
            st.metric("Total Orders", len(filtered_df))
    with col3:
        if 'Payment Type' in filtered_df.columns:
            cash_count = len(filtered_df[filtered_df["Payment Type"] == "Cash"])
            credit_count = len(filtered_df[filtered_df["Payment Type"] == "Credit"])
            st.metric("Cash vs Credit", f"{cash_count}:{credit_count}")
    with col4:
        st.metric("Filtered Data", len(filtered_df))
    
    # Grafik: Order by Status
    if 'Status' in filtered_df.columns:
        fig_status = px.bar(filtered_df, x="Status", title="Orders by Status")
        st.plotly_chart(fig_status, use_container_width=True)
    
    # Grafik: Payment Type
    if 'Payment Type' in filtered_df.columns:
        fig_payment = px.pie(filtered_df, names="Payment Type", title="Payment Type Distribution")
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
    
    # Contoh preview data format yang diharapkan
    st.subheader("📋 Format Data yang Diperlukan")
    sample_data = {
        'Order ID': [387249, 387677, 387678, 387690],
        'Site No': [156109, 157500, 157500, 157375],
        'Site Name': ['20406;CV', '14993;PT', '14993;PT', '21770;CV'],
        'Delivery Date': ['2025-08-29', '2025-08-29', '2025-08-29', '2025-08-29'],
        'Plant Name': ['Manukan', 'Manyar Gre', 'Manyar Gre', 'Manyar Gre'],
        'Order Qty': [131, 6, 12, 60],
        'Status': ['Confirmed', 'Pending Confirmation', 'On Booking', 'Delivered'],
        'CreateDate': ['2025-08-25', '2025-08-26', '2025-08-26', '2025-08-26'],
        'Payment Type': ['Cash', 'Credit', 'Cash', 'Credit']
    }
    sample_df = pd.DataFrame(sample_data)
    st.dataframe(sample_df)
    
