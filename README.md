
# Loan Portfolio Monitoring & Early Warning System
# Credit Risk Monitoring & Early Warning System

A machine learning–driven **Credit Risk Analytics project** combining:
- Probability of Default (PD) modelling
- Rule-based Early Warning System (EWS)
- SHAP explainability
- Real-time deployment with Flask API + Power BI dashboards

---

## 📊 Project Highlights
- **Dataset:** 5,000 loan records, 24 features
- **Model:** Random Forest (AUC = 0.911, Accuracy = 89.7%)
- **EWS Flags:** 6 weighted conditions → risk bands (Green, Amber, Red)
- **Explainability:** SHAP values confirm Credit Score & DSCR as top drivers
- **Deployment:** Flask API + interactive Power BI dashboards

---

## 🗂 Repository Contents
- `/notebooks` → Exploratory Data Analysis, PD modelling, SHAP
- `/src` → Python pipeline + Flask API (`app.py`)
- `/dashboard` → Power BI dashboards (`CreditRisk.pbix`)
- `/reports` → Project presentation (`Credit_Risk_EWS_Presentation.pptx`)
- `/data` → Sample dataset (synthetic for demo)

---

## 🚀 How to Run
```bash
# Clone repo
git clone https://github.com/Elma-Fortunate/Credit-Risk-EWS.git
cd Credit-Risk-EWS

# Install dependencies
pip install -r requirements.txt

# Run Flask API
python src/app.py

