import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
import openai

# Load API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

@st.cache_data
def load_data():
    return pd.read_csv("data/Sample - Superstore.csv", encoding="ISO-8859-1")

df = load_data()

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

def generate_insight(kpis):
    kpi_text = "\n".join([f"{k}: {v}" for k, v in kpis.items()])
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are a business analyst assistant. Here are the KPIs:\n{kpi_text}"},
                {"role": "user", "content": "Give me an executive insight about recent performance based on these KPIs."}
            ],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI Error: {e}"

# Streamlit UI
st.title("F-Analytics - Executive Dashboard")
st.markdown("KPI insights powered by GPT-4 and real retail data")

kpis = calculate_kpis(df)

st.subheader("Key Performance Indicators")
col1, col2, col3 = st.columns(3)
col1.metric("Total Sales", f"${kpis['Total Sales']:,.2f}")
col2.metric("Total Profit", f"${kpis['Total Profit']:,.2f}")
col3.metric("Avg Order Value", f"${kpis['Avg Order Value']:,.2f}")

col4, col5 = st.columns(2)
col4.metric("Total Orders", kpis["Total Orders"])
col5.metric("Total Customers", kpis["Total Customers"])

st.subheader("GPT Business Insight")
if st.button("Generate Insight"):
    with st.spinner("Analyzing KPIs with GPT..."):
        insight = generate_insight(kpis)
        st.success("Insight Generated:")
        st.write(insight)
        
    
