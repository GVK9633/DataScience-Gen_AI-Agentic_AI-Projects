"""
model/knn.py

K-Nearest Neighbors classifier.
Needs feature scaling (distance-based model).
"""

from sklearn.neighbors import KNeighborsClassifier

NAME = "kNN"
NEEDS_SCALING = True


def build_model():
    return KNeighborsClassifier(n_neighbors=7)


def train(X_train, y_train, scaler=None):
    model = build_model()
    model.fit(X_train, y_train)
    return model
