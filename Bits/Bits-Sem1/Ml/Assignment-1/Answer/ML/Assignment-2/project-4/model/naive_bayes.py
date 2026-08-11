"""
model/naive_bayes.py

Gaussian Naive Bayes classifier.
Does NOT need feature scaling (assumes per-feature Gaussian distributions,
each fit independently in its own units).
"""

from sklearn.naive_bayes import GaussianNB

NAME = "Naive Bayes"
NEEDS_SCALING = False


def build_model():
    return GaussianNB()


def train(X_train, y_train, scaler=None):
    model = build_model()
    model.fit(X_train, y_train)
    return model
