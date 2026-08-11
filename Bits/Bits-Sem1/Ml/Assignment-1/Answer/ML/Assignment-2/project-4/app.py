"""
Assignment 2 - Machine Learning
Streamlit App: Breast Cancer Classification Model Demo

No model pickling: every classifier is defined in its own .py file under
model/ (logistic_regression.py, decision_tree.py, knn.py, naive_bayes.py,
random_forest.py) and imported directly here. model/registry.py trains all
5 of them live at app startup (cached via st.cache_resource so it only runs
once per session). There are no .pkl files anywhere in this project, so
there is no scikit-learn version-compatibility risk between environments.

Features:
  a. Dataset upload option (CSV)          -> upload test data for evaluation
                                              (or use the bundled test_data.csv)
  b. Model selection dropdown             -> choose among 5 classifiers
  c. Display of evaluation metrics        -> Accuracy, AUC, Precision, Recall, F1, MCC
  d. Confusion matrix / classification report
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, roc_auc_score, precision_score, recall_score,
    f1_score, matthews_corrcoef, confusion_matrix, classification_report
)

from model.data import get_train_test_split, get_fitted_scaler
from model.registry import MODEL_MODULES, train_all, needs_scaling_map

st.set_page_config(page_title="Breast Cancer Classifier Demo", layout="wide")


@st.cache_resource(show_spinner="Training models (runs once per session)...")
def get_trained_artifacts():
    X_train, X_test, y_train, y_test, feature_cols = get_train_test_split()
    scaler = get_fitted_scaler(X_train)
    X_train_scaled = scaler.transform(X_train)
    trained_models = train_all(X_train, y_train, X_train_scaled)
    return {
        "feature_cols": feature_cols,
        "scaler": scaler,
        "models": trained_models,
        "needs_scaling": needs_scaling_map(),
    }


artifacts = get_trained_artifacts()
feature_cols = artifacts["feature_cols"]
scaler = artifacts["scaler"]
models = artifacts["models"]
needs_scaling = artifacts["needs_scaling"]

st.title("🩺 Breast Cancer Classification — Model Demo")
st.caption(
    "Assignment 2 · Machine Learning · M.Tech (AIML/DSE), BITS Pilani WILP  \n"
    "Dataset: Breast Cancer Wisconsin (Diagnostic) — UCI ML Repository  \n"
    "Models are defined in model/*.py and trained live in this session — no pickled files are used."
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
model_name = st.selectbox("Choose a classification model", list(models.keys()))
model = models[model_name]

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
    for name, m in models.items():
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
