import streamlit as st
import requests
import pandas as pd

BASE_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="Credit Risk EWS", layout="wide")

st.title("🏦 Credit Risk Early Warning System (EWS)")

# =========================
# HEALTH CHECK
# =========================

st.subheader("System Status")

if st.button("Check API Health"):
    try:
        res = requests.get(f"{BASE_URL}/health", timeout=5)
        st.json(res.json())
    except Exception:
        st.error("Flask API not running. Start app.py first.")

# =========================
# LOAN SCORING
# =========================

st.subheader("📊 Score a Loan")

with st.form("score_form"):
    col1, col2 = st.columns(2)

    with col1:
        credit = st.number_input("Credit Score", 300, 850, 600)
        dti = st.number_input("DTI (%)", 0.0, 100.0, 50.0)
        dscr = st.number_input("DSCR", 0.0, 5.0, 1.0)
        ltv = st.number_input("LTV (%)", 0.0, 150.0, 80.0)
        util = st.number_input("Revol Util (%)", 0.0, 100.0, 70.0)
        rate = st.number_input("Interest Rate (%)", 0.0, 50.0, 12.0)
        loan_amt = st.number_input("Loan Amount (USD)", 0, 1000000, 100000)

        collateral_type = st.text_input("Collateral Type", "Unknown")
        inflation = st.number_input("Inflation Expectation (%)", 0.0, 50.0, 5.0)
        bank_trend = st.number_input("Bank Balance Trend", -100.0, 100.0, 0.0)
        city = st.text_input("City / Town", "Harare")

    with col2:
        income = st.number_input("Annual Income", 0, 1000000, 50000)
        collateral = st.number_input("Collateral Value", 0, 2000000, 120000)
        outstanding = st.number_input("Outstanding", 0, 2000000, 90000)
        emp = st.number_input("Employment Length (Years)", 0, 40, 5)
        tenor = st.number_input("Loan Tenor (Months)", 1, 360, 60)

        part_payments = st.number_input("Partial Payments", 0, 100, 0)
        province = st.text_input("Province", "Harare")
        forex_income = st.number_input("Forex Income", 0, 1000000, 0)

        sector = st.text_input("Sector", "Retail")
        product = st.text_input("Loan Product", "Term Loan")
        employment = st.text_input("Employment Type", "Employed")

    submit = st.form_submit_button("Score Loan")

# =========================
# REQUEST TO API
# =========================

if submit:

    payload = {
        "Credit Score": credit,
        "DTI (%)": dti,
        "DSCR": dscr,
        "LTV (%)": ltv,
        "Revol Util (%)": util,
        "Int Rate (%)": rate,
        "Loan Amt (USD)": loan_amt,
        "Annual Income (USD)": income,
        "Collateral Value (USD)": collateral,
        "Outstanding (USD)": outstanding,
        "Emp Length (Yrs)": emp,
        "Loan Tenor (Months)": tenor,
        "Sector": sector,
        "Loan Product": product,
        "Employment Type": employment,

        # 🔥 MISSING FEATURES (FIX FOR 422 ERROR)
        "Collateral Type": collateral_type,
        "Inflation Exp": inflation,
        "Bank Bal Trend": bank_trend,
        "City / Town": city,
        "Part Pmts": part_payments,
        "Province": province,
        "Forex Income": forex_income,
        "Tenor (Mo)": tenor
    }

    try:
        res = requests.post(f"{BASE_URL}/score", json=payload, timeout=10)
        st.subheader("Result")
        st.json(res.json())
    except Exception as e:
        st.error(f"Request failed: {e}")

# =========================
# SUMMARY
# =========================

st.subheader("📈 Portfolio Summary")

if st.button("Load Summary"):
    try:
        res = requests.get(f"{BASE_URL}/ews-summary", timeout=5)
        st.json(res.json())
    except Exception:
        st.error("API not reachable")

# =========================
# URGENT LOANS
# =========================

st.subheader("🚨 Urgent Loans")

if st.button("Load Urgent Loans"):
    try:
        res = requests.get(f"{BASE_URL}/ews-urgent", timeout=5)
        data = res.json()

        st.metric("Urgent Count", data.get("count", 0))
        st.metric("Exposure", data.get("exposure", 0))

        df = pd.DataFrame(data.get("data", []))
        st.dataframe(df)

    except Exception:
        st.error("API not reachable")

# =========================
# FULL REPORT
# =========================

st.subheader("📋 Full Portfolio Report")

if st.button("Load Report"):
    try:
        res = requests.get(f"{BASE_URL}/ews-report", timeout=5)
        data = res.json()

        df = pd.DataFrame(data.get("data", []))
        st.dataframe(df)

    except Exception:
        st.error("API not reachable")