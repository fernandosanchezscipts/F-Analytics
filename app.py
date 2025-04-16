# app.py - F-Analytics: Executive Dashboard & Decision Intelligence System

import pandas as pd
import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# === Load Dataset === #
try:
    df = pd.read_csv("data/Sample - Superstore.csv", encoding="ISO-8859-1")
except FileNotFoundError:
    print("ERROR: Dataset not found at 'data/Sample - Superstore.csv'.")
    exit()

# === KPI CALCULATIONS === #
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

# === GPT-4 Insight Generator === #
def generate_insight_with_gpt(question, kpis):
    kpi_summary = "\n".join([f"{k}: {v}" for k, v in kpis.items()])
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are a business analyst assistant. These are the current KPIs:\n{kpi_summary}"},
                {"role": "user", "content": question}
            ],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI error: {e}"

# === Main Program === #
if __name__ == "__main__":
    print("==== Running F-Analytics ====\n")

    kpis = calculate_kpis(df)

    print("==== KPI Summary ====")
    for key, value in kpis.items():
        if "Sales" in key or "Profit" in key or "Value" in key:
            print(f"{key}: ${value:,.2f}")
        else:
            print(f"{key}: {value}")

    print("\n==== GPT Insight ====")
    prompt = "Based on these KPIs, what sales and profit trends do you observe?"
    insight = generate_insight_with_gpt(prompt, kpis)
    print(insight)
    