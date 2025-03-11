import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
sns.set_theme(style='dark')

# Load Data
all_df = pd.read_csv('all_df.csv')

def change_dtype_object_to_datetime(df, column_name):
  for i in column_name:
    df[i] = pd.to_datetime(df[i]).dt.floor('D')

  return df

change_dtype_object_to_datetime(all_df, ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date', 'shipping_limit_date', 'order_purchase_month'])

min_date = all_df["order_purchase_timestamp"].min().date()
max_date = all_df["order_purchase_timestamp"].max().date()

# Sidebar Navigation
st.title("Dashboard E-commerce")

with st.sidebar:
    st.markdown("Dibuat oleh:")
    st.markdown("""
    Hardianto Tandi Seno (https://github.com/hardiantots)
    """)

    selected_page = st.selectbox(
        "Pilih Analisis:",
        [
            "Demografi Pelanggan Berdasarkan Lokasi",
            "Wilayah dengan Pendapatan Tertinggi",
            "Tren Penjualan Bulanan 2 Tahun Terakhir",
            "Kontribusi Kategori Produk terhadap Total Pendapatan",
            "Wilayah dengan Rata-rata Keterlambatan Tertinggi",
            "RFM Analisis"
        ]
    )

    start_date, end_date = st.date_input(
        label='Pilih Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

customers_data = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & (all_df["order_purchase_timestamp"] <= str(end_date))]

# Mengeksplorasi banyaknya orderan berdasarkan order status
customers_per_state = customers_data.groupby('customer_state')['customer_unique_id'].nunique().reset_index()
orders_per_state = customers_data.groupby('customer_state')['order_id'].nunique().reset_index()
customers_per_city = customers_data.groupby('customer_city')['customer_unique_id'].nunique().reset_index()

# Mengeksplorasi wilayah dengan pendapatan penjualan tertinggi
revenue_per_state = customers_data.groupby('customer_state')['payment_value'].sum().reset_index()
revenue_per_city = customers_data.groupby('customer_city')['payment_value'].sum().reset_index()

# Mengeksplorasi besaran orderan yang didapatkan setiap bulannya
monthly_sales = customers_data.groupby('order_purchase_month')['order_id'].nunique().reset_index()
monthly_revenue = customers_data.groupby('order_purchase_month')['payment_value'].sum().reset_index()

# Mengeksplorasi terkait dengan kategori barang dalam penjualan di e-commerce
total_order_by_category = customers_data.groupby('product_category_name_english')['order_id'].nunique().reset_index()

cost_freight = customers_data.groupby('product_category_name_english')['freight_value'].sum().reset_index()

customers_data['real_revenue'] = customers_data['price'] - customers_data['freight_value']
category_revenue = customers_data.groupby('product_category_name_english')['real_revenue'].sum().reset_index()

# Mengeksplorasi waktu rata-rata keterlambatan berdasarkan wilayah
customer_orders_with_sales_category_df_cleaned_notna = customers_data[customers_data['order_delivered_customer_date'].notna()]

customer_orders_with_sales_category_df_cleaned_notna['delivery_delay'] = (customer_orders_with_sales_category_df_cleaned_notna['order_estimated_delivery_date'] - customer_orders_with_sales_category_df_cleaned_notna['order_delivered_customer_date']).dt.days
late_delivery_per_state = customer_orders_with_sales_category_df_cleaned_notna.groupby('customer_state')['delivery_delay'].mean().reset_index()

late_delivery_per_city = customer_orders_with_sales_category_df_cleaned_notna.groupby('customer_city')['delivery_delay'].mean().reset_index()

# Konversi tanggal ke tipe datetime dan mendapatkan tanggal pembelian terakhir 
customers_data['order_purchase_timestamp'] = pd.to_datetime(customers_data['order_purchase_timestamp'])
latest_date = customers_data['order_purchase_timestamp'].max()

# Hitung RFM metrics
rfm_df = customers_data.groupby('customer_unique_id').agg({
    'order_purchase_timestamp': lambda x: (latest_date - x.max()).days,
    'order_id': 'count',
    'payment_value': 'sum'
  }).reset_index()

# Rename kolom agar lebih jelas
rfm_df.rename(columns={
    'order_purchase_timestamp': 'Recency',
    'order_id': 'Frequency',
    'payment_value': 'Monetary'
}, inplace=True)

def function_bar(df, x, y, xlabel, ylabel, title, colors):
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(
        data=df,
        x=x, 
        y=y,
        ax=ax,
        palette=colors)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    st.pyplot(fig)

def function_line(df, x, y, xlabel, ylabel, title, xticks):
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(
        data=df,
        x=x, 
        y=y,
        marker='o', 
        linewidth=2, 
        color='royalblue'
    )
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticklabels(xticks)
    st.pyplot(fig)

# Page 1: Demografi Pelanggan
if selected_page == "Demografi Pelanggan Berdasarkan Lokasi":
    st.header("Demografi Pelanggan Berdasarkan Lokasi Geografis")

    # Visualisasi 1: Pelanggan unik per negara bagian
    function_bar(customers_per_state.sort_values(by='customer_unique_id', ascending=False).head(5), "customer_state", "customer_unique_id","State", "Number of Customers",
             "Number of Customers by State", colors = ["#33FF57", "#D2D2D2", "#D2D2D2", "#D2D2D2", "#D2D2D2"])

    # Visualisasi 2: Jumlah pesanan per negara bagian
    function_bar(orders_per_state.sort_values(by='order_id', ascending=False).head(5), "customer_state", "order_id", "State", "Number of Orders",
                "Number of Orders by State", colors = ["#33FF57", "#D2D2D2", "#D2D2D2", "#D2D2D2", "#D2D2D2"])

    # Visualisasi 3: Sebaran pelanggan per kota
    function_bar(customers_per_city.sort_values(by='customer_unique_id', ascending=False).head(5), "customer_unique_id", "customer_city", "Number of Customers",
             "City", "Top 5 Cities with Most Customers", colors = ["#33FF57", "#D2D2D2", "#D2D2D2", "#D2D2D2", "#D2D2D2"])


# Page 2: Wilayah dengan Pendapatan Tertinggi
elif selected_page == "Wilayah dengan Pendapatan Tertinggi":
    st.header("Wilayah dengan Pendapatan Penjualan Tertinggi")

    # Visualisasi 1: Total pendapatan per negara bagian
    function_bar(revenue_per_state.sort_values(by='payment_value', ascending=False).head(5), "customer_state", "payment_value", "State",
             "Total Sales Revenue (million)", "Top 5 Total Sales Revenue by State", colors = ["#F4A261", "#D2D2D2", "#D2D2D2", "#D2D2D2", "#D2D2D2"])

    # Visualisasi 2: Total pendapatan per kota
    function_bar(revenue_per_city.sort_values(by='payment_value', ascending=False).head(5), "payment_value", "customer_city", "Total Sales Revenue (million)",
             "City", "Top 5 Cities with Highest Sales Revenue", colors = ["#F4A261", "#D2D2D2", "#D2D2D2", "#D2D2D2", "#D2D2D2"])


# Page 3: Tren Penjualan Bulanan 2 Tahun Terakhir
elif selected_page == "Tren Penjualan Bulanan 2 Tahun Terakhir":
    st.header("Tren Penjualan Bulanan 2 Tahun Terakhir")
    # Definisikan data untuk monthly sales 2 tahun terakhir (2018 dan 2017)
    monthly_sales_2018 = monthly_sales[monthly_sales['order_purchase_month'].dt.year == 2018]
    monthly_sales_2017 = monthly_sales[monthly_sales['order_purchase_month'].dt.year == 2017]

    monthly_sales_2018['order_purchase_month'] = pd.to_datetime(monthly_sales_2018['order_purchase_month'], format='%Y-%m').dt.strftime('%b')
    monthly_sales_2017['order_purchase_month'] = pd.to_datetime(monthly_sales_2017['order_purchase_month'], format='%Y-%m').dt.strftime('%b')

    monthly_revenue_2018 = monthly_revenue[monthly_revenue['order_purchase_month'].dt.year == 2018]
    monthly_revenue_2017 = monthly_revenue[monthly_revenue['order_purchase_month'].dt.year == 2017]

    monthly_revenue_2018['order_purchase_month'] = pd.to_datetime(monthly_revenue_2018['order_purchase_month'], format='%Y-%m').dt.strftime('%b')
    monthly_revenue_2017['order_purchase_month'] = pd.to_datetime(monthly_revenue_2017['order_purchase_month'], format='%Y-%m').dt.strftime('%b')


    # Visualisasi 1: Tahun 2018
    column_1, column_2 = st.columns(2)
    with column_1:
        function_line(monthly_sales_2018, 'order_purchase_month', 'order_id', "Month (2018)", "Number of Orders", "Monthly Order Volume in 2018",
                monthly_sales_2018['order_purchase_month'])
        
        function_line(monthly_revenue_2018, 'order_purchase_month', 'payment_value', "Month (2018)", "Revenue (million)", "Monthly Revenue in 2018",
                monthly_revenue_2018['order_purchase_month'])

    # Visualisasi 2: Tahun 2017
    with column_2:
        function_line(monthly_sales_2017, 'order_purchase_month', 'order_id', "Month (2017)", "Number of Orders", "Monthly Order Volume in 2017",
                monthly_sales_2017['order_purchase_month'])
        
        function_line(monthly_revenue_2017, 'order_purchase_month', 'payment_value', "Month (2017)", "Revenue (million)", "Monthly Revenue in 2017",
                monthly_revenue_2017['order_purchase_month'])

# Page 4: Kontribusi Kategori Produk terhadap Pendapatan
elif selected_page == "Kontribusi Kategori Produk terhadap Total Pendapatan":
    st.header("Kontribusi Kategori Produk terhadap Pendapatan")

    # Visualisasi 1: Pendapatan per kategori produk
    function_bar(total_order_by_category.sort_values(by='order_id', ascending=False).head(5), "product_category_name_english", "order_id", "Product Category",
             "Total Orders", "Top 5 Total Orders per Product Category", colors = ["#2A9D8F", "#D2D2D2", "#D2D2D2", "#D2D2D2", "#D2D2D2"])

    # Visualisasi 2: Freigh cost kategori produk
    function_bar(cost_freight.sort_values(by='freight_value', ascending=False).head(5), "product_category_name_english", "freight_value", "Product Category",
             "Total Freight Cost", "Top 5 Total Freight Cost per Product Category", colors = ["#2A9D8F", "#D2D2D2", "#D2D2D2", "#D2D2D2", "#D2D2D2"])

    # Visualisasi 3: Biaya pengiriman per kategori
    function_bar(category_revenue.sort_values(by='real_revenue', ascending=False).head(5), "product_category_name_english", "real_revenue", "Product Category",
             "Total Revenue (million)", "Top 5 Total Revenue per Product Category", colors = ["#2A9D8F", "#D2D2D2", "#D2D2D2", "#D2D2D2", "#D2D2D2"])

# Page 5: Wilayah dengan Keterlambatan Pengiriman Tertinggi
elif selected_page == "Wilayah dengan Rata-rata Keterlambatan Tertinggi":
    st.header("Wilayah dengan Rata-rata Keterlambatan Pengiriman Tertinggi")

    # Visualisasi 1: Keterlambatan rata-rata per negara bagian
    function_bar(late_delivery_per_state.sort_values('delivery_delay', ascending=False).head(5), "delivery_delay", "customer_state", "Average Delivery Delay (Days)",
             "State", "Top 5 Average Delivery Delay by State", colors = ["#2A9D8F","#D2D2D2", "#D2D2D2", "#D2D2D2", "#D2D2D2", "#2A9D8F"])
    
    # Visualisasi 2: Keterlambatan rata-rata per kota
    function_bar(late_delivery_per_city.sort_values('delivery_delay', ascending=False).head(5), "delivery_delay", "customer_city", "Average Delivery Delay (Days)",
             "City", "Top 5 Average Delivery Delay by City", colors = ["#2A9D8F", "#D2D2D2", "#D2D2D2", "#D2D2D2", "#D2D2D2", ])

# Page 6: RFM Analisis
elif selected_page == "RFM Analisis":
    st.header("RFM Analisis pada E-commerce dataset")
    column1, column2, column3 = st.columns(3)
 
    with column1:
        avg_recency = round(rfm_df.Recency.mean(), 1)
        st.metric("Average Recency (days)", value=avg_recency)
    
    with column2:
        avg_frequency = round(rfm_df.Frequency.mean(), 2)
        st.metric("Average Frequency", value=avg_frequency)
    
    with column3:
        avg_frequency = round(rfm_df.Monetary.mean(), 2) 
        st.metric("Average Monetary", value=avg_frequency)

    palette_color = ["#72BCD4"] * 5

    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 15))

    # Top 5 Pelanggan berdasarkan Recency
    sns.barplot(
        y='Recency', 
        x="customer_unique_id",
        hue="customer_unique_id",
        data=rfm_df.sort_values(by='Recency', ascending=True).head(5), 
        palette=palette_color, 
        ax=ax[0]
    )
    ax[0].set_title("Best Customers by Recency (days)", fontsize=18)
    ax[0].set_xlabel("Customer ID")
    ax[0].set_ylabel("Recency (Days)")
    ax[0].tick_params(axis='x', labelsize=15, rotation=30)

    # Top 5 Pelanggan berdasarkan Frequency
    sns.barplot(
        y="Frequency", 
        x="customer_unique_id",
        hue="customer_unique_id",
        data=rfm_df.sort_values(by="Frequency", ascending=False).head(5), 
        palette=palette_color, 
        ax=ax[1]
    )
    ax[1].set_title("Best Customers by Frequency", fontsize=18)
    ax[1].set_xlabel("Customer ID")
    ax[1].set_ylabel("Frequency (Total Orders)")
    ax[1].tick_params(axis='x', labelsize=15, rotation=30)

    # Top 5 Pelanggan berdasarkan Monetary
    sns.barplot(
        y="Monetary", 
        x="customer_unique_id", 
        hue="customer_unique_id",
        data=rfm_df.sort_values(by="Monetary", ascending=False).head(5), 
        palette=palette_color, 
        ax=ax[2]
    )
    ax[2].set_title("Best Customers by Monetary", fontsize=18)
    ax[2].set_xlabel("Customer ID")
    ax[2].set_ylabel("Monetary (Total Spending)")
    ax[2].tick_params(axis='x', labelsize=15, rotation=30)

    plt.suptitle("Best Customers Based on RFM Parameters", fontsize=22)
    st.pyplot(fig)