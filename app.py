"""
Credit Risk Early Warning System API (Production Ready)
Author: Elma Fortunate Phiri
"""

import json
import logging
from pathlib import Path
from datetime import datetime, date

import joblib
import pandas as pd
from flask import Flask, jsonify, request, abort

# =========================================================
# BASE PATH (FIXED - ALWAYS RELATIVE TO APP.PY)
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "credit_risk_model.pkl"
EWS_REPORT_CSV = BASE_DIR / "ews_report.csv"
MASTER_CSV = BASE_DIR / "ews_master.csv"

# =========================================================
# THRESHOLDS
# =========================================================

PD_URGENT = 0.70
PD_HIGH = 0.50
PD_WATCH = 0.30

# =========================================================
# REQUIRED FEATURES
# =========================================================

REQUIRED_FIELDS = [
    "Credit Score", "DTI (%)", "DSCR", "LTV (%)",
    "Revol Util (%)", "Int Rate (%)", "Loan Amt (USD)",
    "Annual Income (USD)", "Collateral Value (USD)",
    "Outstanding (USD)", "Emp Length (Yrs)",
    "Loan Tenor (Months)", "Sector", "Loan Product",
    "Employment Type"
]

# =========================================================
# LEAKAGE COLUMNS
# =========================================================

LEAKAGE_COLS = [
    "DPD", "Missed Pmts", "Default_Flag", "Loan Status",
    "Issue Date", "Maturity Date", "Loan ID", "Borrower Name",
    "Branch", "Risk_Score", "Risk_Band", "EWS_Action",
    "PD_Score", "PD"
]

# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

log = logging.getLogger(__name__)

app = Flask(__name__)

# =========================================================
# LOAD MODEL ONCE (FAST + SAFE)
# =========================================================

try:
    MODEL = joblib.load(MODEL_PATH)
    log.info("Model loaded successfully.")
except Exception as e:
    MODEL = None
    log.warning(f"Model not loaded: {e}")

# =========================================================
# HELPERS
# =========================================================

def load_ews_report():
    if not EWS_REPORT_CSV.exists():
        raise FileNotFoundError("EWS report missing.")
    df = pd.read_csv(EWS_REPORT_CSV)
    df["PD_Score"] = pd.to_numeric(df.get("PD_Score", 0), errors="coerce").fillna(0)
    return df


def risk_band(pd):
    if pd >= PD_URGENT:
        return "HIGH RISK"
    elif pd >= PD_HIGH:
        return "WATCH"
    elif pd >= PD_WATCH:
        return "MONITOR"
    return "LOW"


def ews_action(pd):
    if pd > PD_URGENT:
        return "URGENT — Credit Committee Review"
    elif pd > PD_HIGH:
        return "HIGH — RM Call Required"
    elif pd > PD_WATCH:
        return "WATCH — Monitor Closely"
    return "LOW — Routine Monitoring"


def to_json(df):
    return json.loads(df.to_json(orient="records", date_format="iso"))

# =========================================================
# ERROR HANDLER
# =========================================================

@app.errorhandler(Exception)
def handle_error(e):
    code = getattr(e, "code", 500)
    return jsonify({
        "error": str(e),
        "status": "failed"
    }), code

# =========================================================
# ROOT
# =========================================================

@app.route("/")
def home():
    return jsonify({
        "app": "Credit Risk EWS API",
        "status": "running",
        "version": "2.0",
        "author": "Elma Fortunate Phiri"
    })

# =========================================================
# HEALTH
# =========================================================

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "model_ready": MODEL is not None,
        "report_ready": EWS_REPORT_CSV.exists(),
        "timestamp": datetime.utcnow().isoformat()
    })

# =========================================================
# SCORE SINGLE LOAN
# =========================================================

@app.route("/score", methods=["POST"])
def score():

    if MODEL is None:
        abort(503, "Model not loaded")

    data = request.get_json(force=True)

    missing = [f for f in REQUIRED_FIELDS if f not in data]
    if missing:
        abort(400, f"Missing fields: {missing}")

    df = pd.DataFrame([data])

    df = df.drop(columns=[c for c in LEAKAGE_COLS if c in df.columns], errors="ignore")

    try:
        pd_score = float(MODEL.predict_proba(df)[0, 1])
    except Exception as e:
        abort(422, str(e))

    return jsonify({
        "pd_score": round(pd_score, 4),
        "risk_band": risk_band(pd_score),
        "ews_action": ews_action(pd_score),
        "timestamp": datetime.utcnow().isoformat()
    })

# =========================================================
# REPORT
# =========================================================

@app.route("/ews-report")
def report():

    df = load_ews_report()

    min_pd = float(request.args.get("min_pd", 0))
    limit = request.args.get("limit")

    df = df[df["PD_Score"] >= min_pd]
    df = df.sort_values("PD_Score", ascending=False)

    if limit:
        df = df.head(int(limit))

    return jsonify({
        "total": len(df),
        "data": to_json(df)
    })

# =========================================================
# URGENT
# =========================================================

@app.route("/ews-urgent")
def urgent():

    df = load_ews_report()

    df = df[df["PD_Score"] > PD_URGENT]

    exposure = float(df.get("Outstanding (USD)", pd.Series([0])).sum())

    return jsonify({
        "count": len(df),
        "exposure": exposure,
        "data": to_json(df)
    })

# =========================================================
# SUMMARY
# =========================================================

@app.route("/ews-summary")
def summary():

    df = load_ews_report()

    return jsonify({
        "total": len(df),
        "avg_pd": float(df["PD_Score"].mean()),
        "high_risk": len(df[df["PD_Score"] > PD_URGENT]),
        "watch": len(df[(df["PD_Score"] <= PD_URGENT) & (df["PD_Score"] > PD_HIGH)]),
        "low": len(df[df["PD_Score"] <= PD_HIGH])
    })

# =========================================================
# RUN APP
# =========================================================

if __name__ == "__main__":
    log.info("Starting Credit Risk EWS API...")
    app.run(host="0.0.0.0", port=5000, debug=False)