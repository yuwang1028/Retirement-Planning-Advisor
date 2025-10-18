# Retirement Planning Advisor Demo (AI-Powered Version)

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import openai  # or use another provider if preferred
import os

# --- Title ---
st.set_page_config(page_title="Retirement AI Advisor", layout="centered")
st.title("🤖 Retirement Planning AI Advisor")
st.write("Ask questions about your retirement and let the AI analyze your plan and provide suggestions.")

# --- Natural Language Input ---
prompt = st.text_area("Ask your retirement-related question (e.g. 'Can I retire at 65 with 120k?')")

# --- Fallback structured input ---
with st.expander("Or manually input your data"):
    age = st.number_input("Your current age:", min_value=18, max_value=70, value=35)
    retire_age = st.number_input("Planned retirement age:", min_value=50, max_value=75, value=65)
    current_savings = st.number_input("Current pension savings (AUD):", min_value=0, value=120000)
    annual_contrib = st.number_input("Annual contribution (AUD):", min_value=0, value=10000)
    expected_expense = st.number_input("Expected annual retirement spending (AUD):", value=50000)
    investment_return = st.slider("Expected annual return rate:", 0.01, 0.10, 0.06)
    inflation = st.slider("Expected annual inflation rate:", 0.01, 0.05, 0.02)
    est_lifespan = st.slider("Expected lifespan:", 75, 100, 88)

# --- AI Assistant Response ---
def get_ai_explanation(prompt_text):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    messages = [
        {"role": "system", "content": "You are a helpful retirement financial advisor."},
        {"role": "user", "content": prompt_text},
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.6,
            max_tokens=400
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error calling AI model: {e}"

# --- Cash Flow Simulation Logic ---
def simulate_pension_growth():
    years_to_retire = retire_age - age
    years_in_retirement = est_lifespan - retire_age
    balance = current_savings
    balances = []

    for _ in range(years_to_retire):
        balance *= (1 + investment_return - inflation)
        balance += annual_contrib
        balances.append(balance)

    for _ in range(years_in_retirement):
        balance *= (1 + investment_return - inflation)
        balance -= expected_expense
        balances.append(balance)
        if balance <= 0:
            break

    return balances

# --- Trigger Simulation + Output ---
if st.button("Analyze My Retirement Plan"):
    # If AI prompt is used
    if prompt.strip():
        st.markdown("### 🤖 AI Advisor’s Analysis")
        response = get_ai_explanation(prompt)
        st.write(response)
    else:
        result = simulate_pension_growth()
        total_years = len(result)
        age_labels = list(range(age, age + total_years))

        if result[-1] <= 0:
            st.error(f"⚠️ Your savings may run out by age {age + total_years - 1}.")
        else:
            st.success(f"✅ Your savings may last until age {age + total_years - 1}.")

        # Chart
        fig, ax = plt.subplots()
        ax.plot(age_labels, result, marker='o')
        ax.axvline(x=retire_age, linestyle='--', color='gray', label='Retirement Age')
        ax.set_xlabel("Age")
        ax.set_ylabel("Projected Pension Balance (AUD)")
        ax.set_title("Projected Pension Balance vs Age")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

        # Recommendation
        shortfall_age = age + total_years - 1
        if shortfall_age < est_lifespan:
            extra_needed = (expected_expense * (est_lifespan - shortfall_age)) / (retire_age - age)
            st.info(f"💡 Suggested: Increase annual contribution by approx **AUD ${int(extra_needed):,}** or invest in higher-growth products.")
        else:
            st.info("You're on track with your current savings and plan.")
