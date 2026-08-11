"""
model/data.py

Shared dataset loading + train/test split logic, used by every model file
(logistic_regression.py, decision_tree.py, knn.py, naive_bayes.py,
random_forest.py) and by app.py, so all models are trained on an identical
split.

Dataset : Breast Cancer Wisconsin (Diagnostic) Data Set
Source  : UCI Machine Learning Repository / scikit-learn built-in loader
          (https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic)
"""

from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42
TEST_SIZE = 0.20


def load_data():
    """Return the full dataframe and the list of feature column names."""
    data = load_breast_cancer(as_frame=True)
    df = data.frame.copy()
    df.rename(columns={"target": "diagnosis"}, inplace=True)
    feature_cols = list(data.feature_names)
    return df, feature_cols


def get_train_test_split():
    """Return X_train, X_test, y_train, y_test (unscaled, raw feature values)."""
    df, feature_cols = load_data()
    X = df[feature_cols]
    y = df["diagnosis"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    return X_train, X_test, y_train, y_test, feature_cols


def get_fitted_scaler(X_train):
    """Fit a StandardScaler on the training split (used by LR and kNN)."""
    scaler = StandardScaler()
    scaler.fit(X_train)
    return scaler
