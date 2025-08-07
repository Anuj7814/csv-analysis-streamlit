import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Business Insights Dashboard", layout="wide")
st.title("📊 CSV Business Insights Tool")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    st.success("File uploaded successfully!")
    df = pd.read_csv(uploaded_file)

    def to_float(x):
        if pd.isna(x): return np.nan
        x_str = str(x).strip().lower()
        if x_str in ['', 'nan', 'none']: return np.nan
        try: return float(x_str.replace(',', ''))
        except: return np.nan

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

    st.subheader("🔍 Key Financial Sums")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Net Order Amount", round(df['order_net_amount'].sum(), 2))
    with col2:
        st.metric("Gross Order Amount", round(df['order_gross_amount'].sum(), 2))
    with col3:
        st.metric("Net Product Amount", round(df['net_product_amount'].sum(), 2))
    with col4:
        st.metric("Gross Product Amount", round(df['gross_product_amount'].sum(), 2))

    st.subheader("🛒 Basket & Customer Metrics")
    bills = df['bill_no'].nunique() if 'bill_no' in df.columns else 0
    customers = df['customer_id'].nunique() if 'customer_id' in df.columns else 0
    quantity = df['quantity'].sum() if 'quantity' in df.columns else 0
    gross_amt = df['gross_product_amount'].sum() if 'gross_product_amount' in df.columns else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Avg Basket Size", round(quantity / bills, 2) if bills > 0 else '-')
    with col2:
        st.metric("ATV (Avg Trans Value)", round(gross_amt / bills, 2) if bills > 0 else '-')
    with col3:
        st.metric("Sales per Customer", round(gross_amt / customers, 2) if customers > 0 else '-')

    st.subheader("📈 Top Categories / Subcategories / Departments")
    def top_table(group_col, label):
        if group_col in df.columns:
            top = df.groupby(group_col)['gross_product_amount'].sum().sort_values(ascending=False).head(10).reset_index()
            st.markdown(f"**Top 10 {label} by Revenue**")
            st.dataframe(top)

    top_table('category_name', 'Categories')
    top_table('subcategory_name', 'Subcategories')
    top_table('department_name', 'Departments')

    st.subheader("🏪 Top 5 Stores by Revenue")
    if 'store' in df.columns:
        top_stores = df.groupby('store')['gross_product_amount'].sum().sort_values(ascending=False).head(5).reset_index()
        st.dataframe(top_stores)

    st.subheader("📊 Discount & Return Metrics")
    if 'order_discount' in df.columns and 'order_gross_amount' in df.columns:
        df['order_discount_rate'] = df['order_discount'] / df['order_gross_amount']
        disc_rate = df.loc[(df['order_discount'] > 0) & (df['order_gross_amount'] > 0), 'order_discount_rate'].mean()
        st.write(f"**Avg Order Discount Rate:** {round(disc_rate * 100, 2)} %")

    if 'product_discount' in df.columns and 'gross_product_amount' in df.columns:
        df['product_discount_rate'] = df['product_discount'] / df['gross_product_amount']
        prod_disc_rate = df.loc[(df['product_discount'] > 0) & (df['gross_product_amount'] > 0), 'product_discount_rate'].mean()
        st.write(f"**Avg Product Discount Rate:** {round(prod_disc_rate * 100, 2)} %")

    if 'quantity' in df.columns:
        neg_qty = df[df['quantity'] < 0]['quantity'].abs().sum()
        total_qty = df['quantity'].sum() + neg_qty
        return_rate = (neg_qty / total_qty) * 100 if total_qty > 0 else 0
        st.write(f"**Return Rate:** {round(return_rate, 2)} %")

    if 'order_tax_total' in df.columns and 'order_net_amount' in df.columns:
        avg_tax_rate = (df['order_tax_total'].sum() / df['order_net_amount'].sum()) * 100
        st.write(f"**Avg Tax Rate on Orders:** {round(avg_tax_rate, 2)} %")
