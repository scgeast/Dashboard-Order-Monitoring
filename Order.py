# Dashboard-Order-Monitoring

import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi halaman
st.set_page_config(
    page_title="Order & Delivery Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data (ganti dengan path data Anda)
@st.cache_data
def load_data():
    # Contoh: load dari CSV. Sesuaikan dengan sumber data Anda.
    df = pd.read_csv("data/sample_data.csv")
    # Bersihkan data: pisahkan kolom yang digabung (jika perlu)
    # Misalnya: pisahkan "Order Qty Status" menjadi "Order Qty" dan "Status"
    return df

df = load_data()

# Sidebar dengan filter
with st.sidebar:
    st.title("📊 Filter Dashboard")
    
    # Filter tanggal: Create Date
    create_date_min = df["CreateDate"].min()
    create_date_max = df["CreateDate"].max()
    create_date_range = st.date_input(
        "Create Date Range",
        [create_date_min, create_date_max],
        min_value=create_date_min,
        max_value=create_date_max
    )
    
    # Filter tanggal: Delivery Date
    delivery_date_min = df["Delivery Date"].min()
    delivery_date_max = df["Delivery Date"].max()
    delivery_date_range = st.date_input(
        "Delivery Date Range",
        [delivery_date_min, delivery_date_max],
        min_value=delivery_date_min,
        max_value=delivery_date_max
    )
    
    # Filter Plant Name
    plant_options = df["Plant Name"].unique()
    selected_plant = st.multiselect("Plant Name", plant_options, default=plant_options)
    
    # Filter Status
    status_options = df["Status"].unique()
    selected_status = st.multiselect("Status", status_options, default=status_options)
    
    # Filter Payment Type
    payment_options = df["Payment Type"].unique()
    selected_payment = st.multiselect("Payment Type", payment_options, default=payment_options)

# Terapkan filter ke dataframe
mask = (
    df["CreateDate"].between(create_date_range[0], create_date_range[1]) &
    df["Delivery Date"].between(delivery_date_range[0], delivery_date_range[1]) &
    df["Plant Name"].isin(selected_plant) &
    df["Status"].isin(selected_status) &
    df["Payment Type"].isin(selected_payment)
)
filtered_df = df[mask]

# Tampilkan summary cards
st.title("📦 Order & Delivery Monitoring Dashboard")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Orders", len(filtered_df))
with col2:
    st.metric("Total Order Qty", filtered_df["Order Qty"].sum())
with col3:
    cash_count = len(filtered_df[filtered_df["Payment Type"] == "Cash"])
    credit_count = len(filtered_df[filtered_df["Payment Type"] == "Credit"])
    st.metric("Cash vs Credit", f"{cash_count}:{credit_count}")
with col4:
    # Tampilkan status breakdown (opsional)
    st.write("**Status Breakdown**")
    st.write(filtered_df["Status"].value_counts())

# Grafik: Order by Status
fig_status = px.bar(filtered_df, x="Status", title="Orders by Status")
st.plotly_chart(fig_status, use_container_width=True)

# Grafik: Payment Type
fig_payment = px.pie(filtered_df, names="Payment Type", title="Payment Type Distribution")
st.plotly_chart(fig_payment, use_container_width=True)

# Tampilkan tabel data
st.subheader("Detail Data")
st.dataframe(filtered_df)
