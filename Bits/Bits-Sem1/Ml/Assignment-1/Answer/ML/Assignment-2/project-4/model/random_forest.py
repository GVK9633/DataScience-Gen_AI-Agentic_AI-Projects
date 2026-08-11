"""
model/random_forest.py

Random Forest (ensemble) classifier.
Does NOT need feature scaling (tree-based ensemble, scale-invariant).
"""

from sklearn.ensemble import RandomForestClassifier
try:
    from .data import RANDOM_STATE
except ImportError:
    from data import RANDOM_STATE

NAME = "Random Forest (Ensemble)"
NEEDS_SCALING = False


def build_model():
    return RandomForestClassifier(n_estimators=300, random_state=RANDOM_STATE)


def train(X_train, y_train, scaler=None):
    model = build_model()
    model.fit(X_train, y_train)
    return model
