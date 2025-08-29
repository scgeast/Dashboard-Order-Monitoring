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

# Fungsi untuk menganalisis file dan menemukan header yang benar
def analyze_file_structure(uploaded_file):
    try:
        # Baca semua data tanpa header untuk inspeksi
        if uploaded_file.name.endswith('.csv'):
            raw_df = pd.read_csv(uploaded_file, header=None)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            raw_df = pd.read_excel(uploaded_file, engine='openpyxl', header=None)
        else:
            return None, "Format file tidak didukung"
        
        # Cari baris yang mengandung nama kolom yang kita cari
        target_keywords = ['delivery', 'plant', 'order', 'status', 'date', 'qty', 'payment']
        best_header_row = 0
        best_match_score = 0
        
        for i in range(min(10, len(raw_df))):  # Cek 10 baris pertama
            row_values = [str(val).lower() for val in raw_df.iloc[i].values]
            match_score = sum(1 for keyword in target_keywords if any(keyword in str(val) for val in row_values))
            
            if match_score > best_match_score:
                best_match_score = match_score
                best_header_row = i
        
        return raw_df, best_header_row
        
    except Exception as e:
        return None, f"Error analyzing file: {str(e)}"

# Fungsi untuk memproses data yang diupload
@st.cache_data
def process_uploaded_file(uploaded_file, header_row=1):
    try:
        # Baca file yang diupload dengan header row tertentu
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=header_row)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file, engine='openpyxl', header=header_row)
        else:
            st.error("Format file tidak didukung. Silakan upload file CSV atau Excel.")
            return None
        
        # Bersihkan nama kolom
        df.columns = [str(col).strip() for col in df.columns]
        
        # Hapus kolom yang seluruhnya kosong
        df = df.dropna(axis=1, how='all')
        
        # Hapus baris yang seluruhnya kosong
        df = df.dropna(how='all')
        
        # Reset index
        df = df.reset_index(drop=True)
        
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
        # Analisis struktur file
        raw_df, header_row = analyze_file_structure(uploaded_file)
        
        if raw_df is not None:
            st.info(f"📋 File terdeteksi memiliki {len(raw_df)} baris")
            st.info(f"🔍 Header terdeteksi di baris: {header_row}")
            
            # Tampilkan preview data mentah
            st.write("**Preview Data Mentah (5 baris pertama):**")
            st.dataframe(raw_df.head(5))
            
            # Pilihan manual header row
            selected_header_row = st.slider(
                "Pilih baris mana yang menjadi header:",
                min_value=0,
                max_value=min(10, len(raw_df)-1),
                value=header_row
            )
            
            # Process uploaded file dengan header row yang dipilih
            df = process_uploaded_file(uploaded_file, selected_header_row)
            
            if df is not None:
                # Tampilkan info kolom
                st.write("**Kolom yang tersedia:**")
                for i, col in enumerate(df.columns):
                    st.write(f"{i}. `{col}`")
                
                # Manual column mapping
                st.write("**🔧 Manual Column Mapping:**")
                
                col_mapping = {}
                column_types = {
                    'Delivery Date': ['delivery', 'date', 'tanggal', 'kirim'],
                    'Plant Name': ['plant', 'nama plant', 'lokasi'],
                    'Order Qty': ['order', 'qty', 'quantity', 'jumlah'],
                    'Status': ['status', 'orderstatus'],
                    'Payment Type': ['payment', 'type', 'pembayaran'],
                    'Order ID': ['order', 'id', 'no order']
                }
                
                for col_type, keywords in column_types.items():
                    options = [f"Tidak digunakan"] + [f"{col} ({i})" for i, col in enumerate(df.columns)]
                    selected = st.selectbox(
                        f"Pilih kolom untuk {col_type}",
                        options=options,
                        key=f"map_{col_type}"
                    )
                    if selected != "Tidak digunakan":
                        col_index = int(selected.split("(")[-1].replace(")", ""))
                        col_mapping[col_type] = df.columns[col_index]
                
                # Simpan mapping ke session state
                st.session_state.col_mapping = col_mapping
                
                # Lanjutkan dengan filter lainnya...
                # ... [kode filter lainnya tetap sama]

# Main content
st.title("📦 Order & Delivery Monitoring Dashboard")

if uploaded_file is not None and 'col_mapping' in st.session_state and st.session_state.col_mapping:
    col_mapping = st.session_state.col_mapping
    
    # Tampilkan summary cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Orders", len(df))
    
    with col2:
        if 'Order Qty' in col_mapping:
            total_qty = df[col_mapping['Order Qty']].sum()
            st.metric("Total Order Qty", int(total_qty))
        else:
            st.metric("Total Orders", len(df))
    
    with col3:
        if 'Payment Type' in col_mapping:
            cash_count = len(df[df[col_mapping['Payment Type']].astype(str).str.contains('Cash', case=False, na=False)])
            credit_count = len(df[df[col_mapping['Payment Type']].astype(str).str.contains('Credit', case=False, na=False)])
            st.metric("Cash vs Credit", f"{cash_count}:{credit_count}")
    
    with col4:
        st.metric("Data Points", len(df))
    
    # Tampilkan tabel data
    st.subheader("Detail Data")
    st.dataframe(df)
    
    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download Data as CSV",
        data=csv,
        file_name="orders_data.csv",
        mime="text/csv"
    )

else:
    st.info("📤 Silakan upload file data melalui sidebar di sebelah kiri untuk memulai analisis.")
    st.info("🔧 Setelah upload, Anda perlu melakukan manual mapping kolom di sidebar")
