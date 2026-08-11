"""
model/logistic_regression.py

Logistic Regression classifier.
Needs feature scaling (distance/coefficient-magnitude sensitive model).
"""

from sklearn.linear_model import LogisticRegression
try:
    from .data import RANDOM_STATE
except ImportError:  # allows running this file standalone (e.g. cd model && python train_models.py)
    from data import RANDOM_STATE

NAME = "Logistic Regression"
NEEDS_SCALING = True


def build_model():
    return LogisticRegression(max_iter=5000, random_state=RANDOM_STATE)


def train(X_train, y_train, scaler=None):
    """Fit and return a trained model. X_train should already be scaled
    if NEEDS_SCALING is True (scaler is accepted for interface symmetry
    with other model files but is not required here)."""
    model = build_model()
    model.fit(X_train, y_train)
    return model
