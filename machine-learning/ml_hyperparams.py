#!/usr/bin/env python

"""
Hyperparameters for use with
1. sklearn.model_selection.GridSearchCV()
2. hyperopt.hp
"""

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

# K Neighbors
hp_space_knn = {
    'n_neighbors': hp.choice('n_neighbors', range(2, 80)),
    'scale': hp.choice('scale', [0, 1]),
    'normalize': hp.choice('normalize', [0, 1]),
}

# Multilayer Perceptron
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
