"""
Assignment 2 - Machine Learning
Streamlit App: Breast Cancer Classification Model Demo

Features:
  a. Dataset upload option (CSV)          -> upload the test data (or your own,
                                              same schema as test_data.csv)
  b. Model selection dropdown             -> choose among 5 trained classifiers
  c. Display of evaluation metrics        -> Accuracy, AUC, Precision, Recall, F1, MCC
  d. Confusion matrix / classification report
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, roc_auc_score, precision_score, recall_score,
    f1_score, matthews_corrcoef, confusion_matrix, classification_report
)

st.set_page_config(page_title="Breast Cancer Classifier Demo", layout="wide")

MODEL_DIR = "model"

MODEL_FILES = {
    "Logistic Regression": "logistic_regression.pkl",
    "Decision Tree": "decision_tree.pkl",
    "kNN": "knn.pkl",
    "Naive Bayes": "naive_bayes.pkl",
    "Random Forest (Ensemble)": "random_forest_ensemble.pkl",
}


@st.cache_resource
def load_meta():
    with open(f"{MODEL_DIR}/meta.json") as f:
        return json.load(f)


@st.cache_resource
def load_scaler():
    return joblib.load(f"{MODEL_DIR}/scaler.pkl")


@st.cache_resource
def load_model(name):
    return joblib.load(f"{MODEL_DIR}/{MODEL_FILES[name]}")


meta = load_meta()
scaler = load_scaler()
feature_cols = meta["feature_cols"]
needs_scaling = meta["needs_scaling"]

st.title("🩺 Breast Cancer Classification — Model Demo")
st.caption(
    "Assignment 2 · Machine Learning · M.Tech (AIML/DSE), BITS Pilani WILP  \n"
    "Dataset: Breast Cancer Wisconsin (Diagnostic) — UCI ML Repository"
)

# ------------------------------------------------------------------
# a. Dataset upload
# ------------------------------------------------------------------
st.header("1. Upload Test Data")
st.write(
    "Upload a CSV with the same columns as `test_data.csv` "
    "(30 numeric features + a `diagnosis` column: 0 = malignant, 1 = benign)."
)

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    st.info("No file uploaded — using the bundled sample `test_data.csv`.")
    df = pd.read_csv("test_data.csv")

st.dataframe(df.head(10), use_container_width=True)
st.caption(f"Loaded {df.shape[0]} rows × {df.shape[1]} columns")

missing_cols = [c for c in feature_cols if c not in df.columns]
if missing_cols:
    st.error(f"Uploaded file is missing required feature columns: {missing_cols}")
    st.stop()

has_labels = "diagnosis" in df.columns

X = df[feature_cols]
y_true = df["diagnosis"] if has_labels else None

# ------------------------------------------------------------------
# b. Model selection dropdown
# ------------------------------------------------------------------
st.header("2. Select a Model")
model_name = st.selectbox("Choose a classification model", list(MODEL_FILES.keys()))
model = load_model(model_name)

X_input = scaler.transform(X) if needs_scaling.get(model_name, False) else X.values

y_pred = model.predict(X_input)
y_proba = model.predict_proba(X_input)[:, 1]

# ------------------------------------------------------------------
# c. Evaluation metrics
# ------------------------------------------------------------------
st.header("3. Evaluation Metrics")

if has_labels:
    acc = accuracy_score(y_true, y_pred)
    auc = roc_auc_score(y_true, y_proba)
    prec = precision_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    mcc = matthews_corrcoef(y_true, y_pred)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Accuracy", f"{acc:.4f}")
    c2.metric("AUC", f"{auc:.4f}")
    c3.metric("Precision", f"{prec:.4f}")
    c4.metric("Recall", f"{rec:.4f}")
    c5.metric("F1 Score", f"{f1:.4f}")
    c6.metric("MCC", f"{mcc:.4f}")
else:
    st.warning(
        "Uploaded data has no `diagnosis` column, so evaluation metrics "
        "can't be computed — only predictions are shown below."
    )

# ------------------------------------------------------------------
# d. Confusion matrix / classification report
# ------------------------------------------------------------------
st.header("4. Confusion Matrix & Classification Report")

if has_labels:
    col1, col2 = st.columns([1, 1.4])

    with col1:
        cm = confusion_matrix(y_true, y_pred)
        fig, ax = plt.subplots(figsize=(4, 3.5))
        sns.heatmap(
            cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=["Malignant (0)", "Benign (1)"],
            yticklabels=["Malignant (0)", "Benign (1)"],
            ax=ax,
        )
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
        ax.set_title(f"Confusion Matrix — {model_name}")
        st.pyplot(fig)

    with col2:
        report = classification_report(
            y_true, y_pred, target_names=["Malignant (0)", "Benign (1)"], output_dict=True
        )
        st.dataframe(pd.DataFrame(report).transpose().round(3), use_container_width=True)
else:
    st.write("Predictions on uploaded data:")
    out = df.copy()
    out["predicted_diagnosis"] = y_pred
    out["predicted_probability_benign"] = y_proba.round(4)
    st.dataframe(out, use_container_width=True)

# ------------------------------------------------------------------
# Comparison across all models (bonus view)
# ------------------------------------------------------------------
st.header("5. Compare All Models on This Data")
if has_labels and st.checkbox("Run all 5 models on the current dataset"):
    rows = []
    for name in MODEL_FILES:
        m = load_model(name)
        Xi = scaler.transform(X) if needs_scaling.get(name, False) else X.values
        yp = m.predict(Xi)
        ypr = m.predict_proba(Xi)[:, 1]
        rows.append({
            "Model": name,
            "Accuracy": round(accuracy_score(y_true, yp), 4),
            "AUC": round(roc_auc_score(y_true, ypr), 4),
            "Precision": round(precision_score(y_true, yp), 4),
            "Recall": round(recall_score(y_true, yp), 4),
            "F1": round(f1_score(y_true, yp), 4),
            "MCC": round(matthews_corrcoef(y_true, yp), 4),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

st.divider()
st.caption("Built with Streamlit · scikit-learn · Assignment 2 submission")
