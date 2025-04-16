import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
import openai

# Load API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

@st.cache_data
def load_data():
    return pd.read_csv("data/Sample - Superstore.csv", encoding="ISO-8859-1")

df = load_data()

# Sidebar filter
st.sidebar.header("Filter Data")
region = st.sidebar.selectbox("Select Region", ["All"] + sorted(df["Region"].unique()))
if region != "All":
    df = df[df["Region"] == region]

# KPI calculation
def calculate_kpis(df):
    total_sales = df['Sales'].sum()
    total_profit = df['Profit'].sum()
    total_orders = df['Order ID'].nunique()
    total_customers = df['Customer ID'].nunique()
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    return {
        "Total Sales": round(total_sales, 2),
        "Total Profit": round(total_profit, 2),
        "Total Orders": total_orders,
        "Total Customers": total_customers,
        "Avg Order Value": round(avg_order_value, 2)
    }

# GPT insight generator
def generate_insight(kpis, question):
    kpi_text = "\n".join([f"{k}: {v}" for k, v in kpis.items()])
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are a business analyst assistant. Here are the KPIs:\n{kpi_text}"},
                {"role": "user", "content": question}
            ],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI Error: {e}"

# App layout
st.title("F-Analytics – Executive Dashboard")
st.markdown("**Data Source:** Kaggle Superstore | **AI-Powered Analysis** with GPT-4")

kpis = calculate_kpis(df)

# KPI Display
st.subheader("📊 Key Performance Indicators")
col1, col2, col3 = st.columns(3)
col1.metric("Total Sales", f"${kpis['Total Sales']:,.2f}")
col2.metric("Total Profit", f"${kpis['Total Profit']:,.2f}")
col3.metric("Avg Order Value", f"${kpis['Avg Order Value']:,.2f}")

col4, col5 = st.columns(2)
col4.metric("Total Orders", kpis["Total Orders"])
col5.metric("Total Customers", kpis["Total Customers"])

# Sales by category chart
st.subheader("📈 Sales by Category")
category_sales = df.groupby("Category")["Sales"].sum().sort_values()
st.bar_chart(category_sales)

# Trendline chart: Sales & Profit Over Time
st.subheader("📉 Sales and Profit Over Time")

# Ensure Order Date is datetime
df["Order Date"] = pd.to_datetime(df["Order Date"])

# Group by month and aggregate
df_trend = df.groupby(pd.Grouper(key="Order Date", freq="M")).agg({
    "Sales": "sum",
    "Profit": "sum"
}).reset_index()

# Plot trendline chart
st.line_chart(df_trend.set_index("Order Date"))

# GPT prompt input
st.subheader("🧠 Ask GPT About the KPIs")
custom_question = st.text_input("Enter your business question:",
    value="Give me an executive insight about recent performance based on these KPIs.")

if st.button("Generate Insight"):
    with st.spinner("Analyzing data with GPT..."):
        insight = generate_insight(kpis, custom_question)
        st.success("Insight Generated:")
        st.write(insight)
        