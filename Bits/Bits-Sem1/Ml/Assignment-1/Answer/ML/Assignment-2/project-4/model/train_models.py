"""
model/train_models.py

Reference / reproducibility script. Reuses the exact same model files
(logistic_regression.py, decision_tree.py, knn.py, naive_bayes.py,
random_forest.py) and data.py that app.py imports, so there is a single
source of truth for "how each model is built" across the whole project.

Run this to:
1. Regenerate ../test_data.csv (the held-out test split used by the app)
2. Regenerate model_results.csv (the metrics table used in the README)

No models are pickled — this script trains fresh, computes metrics, and
exits. app.py does the same thing at runtime.
"""

import pandas as pd
from sklearn.metrics import (
    accuracy_score, roc_auc_score, precision_score,
    recall_score, f1_score, matthews_corrcoef
)

from data import get_train_test_split, get_fitted_scaler
from registry import MODEL_MODULES

# ------------------------------------------------------------------
# 1. Load + split data
# ------------------------------------------------------------------
X_train, X_test, y_train, y_test, feature_cols = get_train_test_split()
print(f"Train shape: {X_train.shape}, Test shape: {X_test.shape}")

# Save the RAW test data (features + true label) -> used as test_data.csv
test_data = X_test.copy()
test_data["diagnosis"] = y_test.values
test_data.to_csv("../test_data.csv", index=False)
print("Saved ../test_data.csv")

# ------------------------------------------------------------------
# 2. Fit scaler (needed by Logistic Regression and kNN)
# ------------------------------------------------------------------
scaler = get_fitted_scaler(X_train)
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ------------------------------------------------------------------
# 3. Train each model (imported from its own file) + compute metrics
# ------------------------------------------------------------------
results = []

for name, module in MODEL_MODULES.items():
    Xtr = X_train_scaled if module.NEEDS_SCALING else X_train.values
    Xte = X_test_scaled if module.NEEDS_SCALING else X_test.values

    model = module.train(Xtr, y_train)
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

# ------------------------------------------------------------------
# 4. Save results
# ------------------------------------------------------------------
results_df = pd.DataFrame(results)
results_df.to_csv("model_results.csv", index=False)
print("\nSaved model_results.csv")
print(results_df.to_string(index=False))
