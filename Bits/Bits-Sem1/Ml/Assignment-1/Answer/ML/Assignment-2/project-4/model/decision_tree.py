"""
model/decision_tree.py

Decision Tree classifier.
Does NOT need feature scaling (tree splits are scale-invariant).
"""

from sklearn.tree import DecisionTreeClassifier
try:
    from .data import RANDOM_STATE
except ImportError:
    from data import RANDOM_STATE

NAME = "Decision Tree"
NEEDS_SCALING = False


def build_model():
    return DecisionTreeClassifier(random_state=RANDOM_STATE, max_depth=6)


def train(X_train, y_train, scaler=None):
    model = build_model()
    model.fit(X_train, y_train)
    return model
