
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="CSV Metrics Analyzer", layout="wide")
st.title("📊 CSV Sales Metrics Dashboard")

uploaded_file = st.file_uploader("🔼 Upload your CSV file", type=["csv"])

def to_float(x):
    if pd.isna(x): return np.nan
    x_str = str(x).strip().lower()
    if x_str in ['', 'nan', 'none']: return np.nan
    try: return float(x_str.replace(',', ''))
    except: return np.nan

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success(f"✅ Loaded file: {uploaded_file.name} — Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    st.write("🧾 Columns:", df.columns.tolist())

    numeric_columns = [
        'order_net_amount', 'order_gross_amount', 'order_tax_total', 'order_discount',
        'net_product_amount', 'gross_product_amount', 'lineitem_tax_amount',
        'product_discount', 'quantity'
    ]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = df[col].apply(to_float)

    if 'event_id' in df.columns:
        df['event_id'] = pd.to_numeric(df['event_id'], errors='coerce')

    with st.expander("🔢 Key Totals"):
        if 'order_net_amount' in df.columns:
            st.metric("🧾 Total order_net_amount", round(df['order_net_amount'].sum(), 2))
        if 'order_gross_amount' in df.columns:
            st.metric("💰 Total order_gross_amount", round(df['order_gross_amount'].sum(), 2))
        if 'net_product_amount' in df.columns:
            st.metric("📦 Total net_product_amount", round(df['net_product_amount'].sum(), 2))
        if 'gross_product_amount' in df.columns:
            st.metric("💸 Total gross_product_amount", round(df['gross_product_amount'].sum(), 2))

    with st.expander("🛒 Basket Metrics"):
        if 'bill_no' in df.columns and 'quantity' in df.columns:
            avg_basket = df['quantity'].sum() / df['bill_no'].nunique()
            st.write("🛒 Avg Basket Size:", round(avg_basket, 2))
        if 'bill_no' in df.columns and 'gross_product_amount' in df.columns:
            atv = df['gross_product_amount'].sum() / df['bill_no'].nunique()
            st.write("💳 ATV:", round(atv, 2))
        if 'customer_id' in df.columns and 'gross_product_amount' in df.columns:
            sales_pc = df['gross_product_amount'].sum() / df['customer_id'].nunique()
            st.write("👤 Sales per Customer:", round(sales_pc, 2))

    with st.expander("📈 Summary Stats"):
        st.dataframe(df[numeric_columns].describe())

    with st.expander("📊 Unique Counts"):
        st.write("🧍 Unique Customers:", df['customer_id'].nunique())
        st.write("📍 Unique Locations:", df['location_id'].nunique())
        st.write("🏪 Unique Stores:", df['store'].nunique())
        st.write("📦 Unique Products:", df['product_name'].nunique())
        st.write("🗂️ Unique Categories:", df['category_name'].nunique())
        st.write("🔖 Unique Subcategories:", df['subcategory_name'].nunique())
        st.write("🏬 Unique Departments:", df['department_name'].nunique())

    with st.expander("🗓️ Event Types & Channels"):
        st.write("Event Types:", df['event_type'].value_counts(dropna=False))
        st.write("Channels:", df['channel'].value_counts(dropna=False))

    with st.expander("💸 Discount Rate"):
        if all(col in df.columns for col in ['order_discount','order_gross_amount']):
            df['order_discount_rate'] = df['order_discount'] / df['order_gross_amount']
            mask = (df['order_discount'] > 0) & (df['order_gross_amount'] > 0)
            st.write("Avg Order Discount Rate:", df.loc[mask, 'order_discount_rate'].mean())
        if all(col in df.columns for col in ['product_discount','gross_product_amount']):
            df['product_discount_rate'] = df['product_discount'] / df['gross_product_amount']
            mask = (df['product_discount'] > 0) & (df['gross_product_amount'] > 0)
            st.write("Avg Product Discount Rate:", df.loc[mask, 'product_discount_rate'].mean())

    with st.expander("↩️ Returns"):
        if 'quantity' in df.columns:
            returns = (df['quantity'] < 0).sum()
            st.write("Returned Line Items:", returns)

    def show_top(group_col, label):
        if group_col in df.columns and 'gross_product_amount' in df.columns:
            top = df.groupby(group_col)['gross_product_amount'].sum().sort_values(ascending=False).head(10)
            st.write(f"🏆 Top 10 {label} by Revenue:")
            st.dataframe(top)

    with st.expander("🏆 Top 10 by Revenue"):
        show_top('category_name', 'Categories')
        show_top('subcategory_name', 'Subcategories')
        show_top('department_name', 'Departments')

    with st.expander("🏪 Top 5 Stores by Revenue"):
        if 'store' in df.columns and 'gross_product_amount' in df.columns:
            top_stores = df.groupby('store')['gross_product_amount'].sum().sort_values(ascending=False).head(5)
            st.dataframe(top_stores)

    with st.expander("🧾 Consultant Metrics"):
        if 'bill_no' in df.columns:
            items_per_txn = df.shape[0] / df['bill_no'].nunique()
            st.write("📋 Line Items per Bill:", round(items_per_txn, 2))

        if 'product_name' in df.columns and 'quantity' in df.columns:
            top_qty = df.groupby('product_name')['quantity'].sum().sort_values(ascending=False).head(10)
            st.write("📦 Top 10 Products by Quantity:")
            st.dataframe(top_qty)

        if 'category_name' in df.columns and 'gross_product_amount' in df.columns:
            mix = df.groupby('category_name')['gross_product_amount'].sum().reset_index()
            total_sales = mix['gross_product_amount'].sum()
            mix['% Contribution'] = (mix['gross_product_amount'] / total_sales) * 100
            st.write("📊 Category Contribution to Sales:")
            st.dataframe(mix.sort_values('% Contribution', ascending=False).head(10))

        if 'order_date' in df.columns:
            df['order_date'] = pd.to_datetime(df['order_date'])
            df['month'] = df['order_date'].dt.to_period('M')
            monthly = df.groupby('month')['gross_product_amount'].sum().reset_index()
            st.write("📆 Monthly Sales Trend:")
            st.line_chart(monthly.rename(columns={'month':'index'}).set_index('index'))

        if 'quantity' in df.columns:
            total_qty = df['quantity'].sum()
            return_qty = df[df['quantity'] < 0]['quantity'].abs().sum()
            return_rate = (return_qty / (total_qty + return_qty)) * 100 if (total_qty + return_qty) > 0 else 0
            st.write("↩️ Return Rate:", round(return_rate, 2), "%")

        if 'order_tax_total' in df.columns and 'order_net_amount' in df.columns:
            tax = df['order_tax_total'].sum()
            net = df['order_net_amount'].sum()
            rate = (tax / net) * 100 if net > 0 else 0
            st.write("📊 Avg Tax Rate:", round(rate, 2), "%")
