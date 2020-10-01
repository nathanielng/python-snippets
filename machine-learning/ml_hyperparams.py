#!/usr/bin/env python

"""
Hyperparameters for use with
1. sklearn.model_selection.GridSearchCV()
2. hyperopt.hp
3. scikit-optimize (future)
"""

import numpy as np
from hyperopt import hp


# Logistic Regression
hp_space_lr = {
    'warm_start': hp.choice('warm_start', [True, False]),
    'fit_intercept': hp.choice('fit_intercept', [True, False]),
    'tol': hp.uniform('tol', 0.00001, 0.0001),
    'C': hp.uniform('C', 0.05, 3),
    'max_iter': hp.choice('max_iter', range(80, 200)),
    'scale': hp.choice('scale', [0, 1]),
    'normalize': hp.choice('normalize', [0, 1]),
    'multi_class': 'auto',
    'class_weight': 'balanced'
}
params_lr = {
    'warm_start': [True, False],
    'fit_intercept': [True, False],
    'tol': [0.00001, 0.0001],
    'C': [0.05, 0.1, 0.2, 0.5, 1.0, 3.0],
    'max_iter': [80, 120, 200],
    'scale': [0, 1],
    'normalize': [0, 1],
    'multi_class': 'auto',
    'class_weight': 'balanced'
}

# Support Vector Classifier
hp_space_svc = {
    'C': hp.uniform('C', 0, 100),
    'kernel': hp.choice('kernel', ['linear', 'sigmoid', 'poly', 'rbf']),
    'gamma': hp.uniform('gamma', 0, 20),
    'scale': hp.choice('scale', [0, 1]),
    'normalize': hp.choice('normalize', [0, 1]),
}
params_svc = {
    'SVC_C': [.05, .5, 1, 4, 8, 16, 32],
    'SVC__kernel': ['linear', 'rbf', 'poly'],
    'SVC__gamma': ['scale', 'auto']
}

# Support Vector Regressor
hp_space_svr = {
    'C': hp.choice('C', [.05, .5, 1, 4, 8, 16, 32]),
    'kernel': hp.choice('kernel', ['linear', 'rbf', 'poly']),
    'gamma': hp.choice('gamma', ['scale', 'auto'])
}

params_svr = {
    'SVR__C': [.05, .5, 1, 4, 8, 16, 32],
    'SVR__kernel': ['linear', 'rbf', 'poly'],
    'SVR__gamma': ['scale', 'auto']
}

# K Nearest Neighbor
hp_space_knn = {
    'n_neighbors': hp.choice('n_neighbors', range(2, 80)),
    'scale': hp.choice('scale', [0, 1]),
    'normalize': hp.choice('normalize', [0, 1]),
}
params_knn = {
    'n_neighbors': [2, 4, 8, 16, 32, 80],
    'scale': [0, 1],
    'normalize': [0, 1]
}

# Multilayer Perceptron
hp_space_mlp = {
    'hidden_layer_sizes': hp.choice('hidden_layer_sizes', [
        (20), (40), (75), (100),
        (20, 20), (40, 40), (75, 75), (100, 100)
        ]),
    'activation': hp.choice('activation', ['logistic', 'tanh', 'relu']),
    'solver': hp.choice('solver', ['adam']),
    'alpha': hp.loguniform('alpha', np.log(0.001), np.log(0.0001)),
    'learning_rate_init': hp.loguniform('learning_rate_init', np.log(0.01), np.log(0.001))
}
params_mlp = {
    'MLP__hidden_layer_sizes': [(20), (40), (60), (80), (100)],
    'MLP__activation': ['logistic', 'tanh', 'relu'],
    'MLP__solver': ['adam'],
    'MLP__alpha': [0.001, 0.0001, 0.00001],
    'MLP__learning_rate_init': [0.01, 0.001, 0.0001]
}

# Random Forest
hp_space_rf = {
    'max_depth': hp.choice('max_depth', range(5, 20)),
    'max_features': hp.choice('max_features', range(1, 5)),
    'n_estimators': hp.choice('n_estimators', range(15, 120, 5)),
    'criterion': hp.choice('criterion', ["gini", "entropy"]),
}
params_rf = {
    'max_depth': [5, 10, 20],
    'max_features': [1, 2, 5],
    'n_estimators': [15, 30, 50, 80, 120],
    'criterion': ['gini', 'entropy']
}

# XGBoost
hp_space_xgboost = {
    'max_depth': hp.choice('max_depth', range(5, 20, 1)),
    'learning_rate': hp.quniform('learning_rate', 0.01, 0.3, 0.005),
    'n_estimators': hp.choice('n_estimators', range(20, 150, 5)),
    'gamma': hp.quniform('gamma', 0, 0.50, 0.005),
    'min_child_weight': hp.quniform('min_child_weight', 1, 10, 1),
    'subsample': hp.quniform('subsample', 0.1, 1, 0.005),
    'colsample_bytree': hp.quniform('colsample_bytree', 0.1, 1.0, 0.005)
}

params_xgboost = {
    'max_depth': [5, 10, 20],
    'learning_rate': [0.01, 0.05, 0.1, 0.3],
    'n_estimators': [20, 40, 70, 110, 150],
    'gamma': [0, 0.05, 0.1, 0.2, 0.5],
    'min_child_weight': [1, 2, 4, 10],
    'subsample': [0.1, 0.2, 0.4, 1.0],
    'colsample_bytree': [0.1, 0.2, 0.4, 1.0]
}
