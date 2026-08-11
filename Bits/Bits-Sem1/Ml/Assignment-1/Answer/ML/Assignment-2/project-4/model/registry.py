"""
model/registry.py

Collects every model file in this package into a single ordered mapping,
so app.py and train_models.py both iterate over the exact same 5 models
without duplicating the list anywhere else.
"""

try:
    from . import logistic_regression
    from . import decision_tree
    from . import knn
    from . import naive_bayes
    from . import random_forest
except ImportError:  # allows running standalone (e.g. cd model && python train_models.py)
    import logistic_regression
    import decision_tree
    import knn
    import naive_bayes
    import random_forest

# Order here defines the order everywhere (dropdown, comparison table, etc.)
MODEL_MODULES = {
    logistic_regression.NAME: logistic_regression,
    decision_tree.NAME: decision_tree,
    knn.NAME: knn,
    naive_bayes.NAME: naive_bayes,
    random_forest.NAME: random_forest,
}


def train_all(X_train, y_train, X_train_scaled):
    """Train every registered model. Returns {name: fitted_model}."""
    trained = {}
    for name, module in MODEL_MODULES.items():
        Xtr = X_train_scaled if module.NEEDS_SCALING else X_train.values
        trained[name] = module.train(Xtr, y_train)
    return trained


def needs_scaling_map():
    return {name: module.NEEDS_SCALING for name, module in MODEL_MODULES.items()}
