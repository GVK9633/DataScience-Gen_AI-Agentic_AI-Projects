"""
Assignment 2 - Machine Learning
Model training script.

Dataset : Breast Cancer Wisconsin (Diagnostic) Data Set
Source  : UCI Machine Learning Repository / scikit-learn built-in loader
          (https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic)
Task    : Binary classification (Malignant vs Benign)
Rows    : 569
Features: 30 (all numeric, computed from digitized images of a fine needle
          aspirate (FNA) of a breast mass)

This script:
1. Loads the dataset
2. Splits into train (80%) / test (20%)
3. Trains 5 classification models
4. Computes Accuracy, AUC, Precision, Recall, F1, MCC for each model
5. Saves trained models (.pkl) to the model/ folder
6. Saves the test split to test_data.csv (used by the Streamlit app)
7. Writes results to model_results.csv (used to build the README table)
"""

import pandas as pd
import numpy as np
import joblib
import json
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, roc_auc_score, precision_score,
    recall_score, f1_score, matthews_corrcoef
)

RANDOM_STATE = 42

# ------------------------------------------------------------------
# 1. Load data
# ------------------------------------------------------------------
data = load_breast_cancer(as_frame=True)
df = data.frame.copy()
# rename target for clarity: 0 = malignant, 1 = benign (sklearn's default)
df.rename(columns={"target": "diagnosis"}, inplace=True)

feature_cols = list(data.feature_names)
X = df[feature_cols]
y = df["diagnosis"]

print(f"Dataset shape: {df.shape}")
print(f"Class balance:\n{y.value_counts()}")

# ------------------------------------------------------------------
# 2. Train / test split
# ------------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
)

# Save the RAW test data (features + true label) -> used as test_data.csv
test_data = X_test.copy()
test_data["diagnosis"] = y_test.values
test_data.to_csv("../test_data.csv", index=False)
print("Saved ../test_data.csv")

# ------------------------------------------------------------------
# 3. Scaling (fit on train only, needed for LR / KNN)
# ------------------------------------------------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
joblib.dump(scaler, "scaler.pkl")

# ------------------------------------------------------------------
# 4. Define models
# ------------------------------------------------------------------
models = {
    "Logistic Regression": (LogisticRegression(max_iter=5000, random_state=RANDOM_STATE), True),
    "Decision Tree": (DecisionTreeClassifier(random_state=RANDOM_STATE, max_depth=6), False),
    "kNN": (KNeighborsClassifier(n_neighbors=7), True),
    "Naive Bayes": (GaussianNB(), False),
    "Random Forest (Ensemble)": (RandomForestClassifier(n_estimators=300, random_state=RANDOM_STATE), False),
}

results = []

for name, (model, needs_scaling) in models.items():
    Xtr = X_train_scaled if needs_scaling else X_train.values
    Xte = X_test_scaled if needs_scaling else X_test.values

    model.fit(Xtr, y_train)
    y_pred = model.predict(Xte)
    y_proba = model.predict_proba(Xte)[:, 1]

    metrics = {
        "Model": name,
        "Accuracy": round(accuracy_score(y_test, y_pred), 4),
        "AUC": round(roc_auc_score(y_test, y_proba), 4),
        "Precision": round(precision_score(y_test, y_pred), 4),
        "Recall": round(recall_score(y_test, y_pred), 4),
        "F1": round(f1_score(y_test, y_pred), 4),
        "MCC": round(matthews_corrcoef(y_test, y_pred), 4),
    }
    results.append(metrics)
    print(metrics)

    fname = name.lower().replace(" ", "_").replace("(", "").replace(")", "")
    joblib.dump(model, f"{fname}.pkl")

# ------------------------------------------------------------------
# 5. Save results
# ------------------------------------------------------------------
results_df = pd.DataFrame(results)
results_df.to_csv("model_results.csv", index=False)
print("\nSaved model_results.csv")
print(results_df.to_string(index=False))

# Save feature column order + which models need scaling (used by the app)
meta = {
    "feature_cols": feature_cols,
    "needs_scaling": {name: needs for name, (_, needs) in models.items()},
    "target_names": {"0": "malignant", "1": "benign"},
}
with open("meta.json", "w") as f:
    json.dump(meta, f, indent=2)
print("Saved meta.json")
