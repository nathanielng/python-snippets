#!/usr/bin/env python

"""
Hyperparameters for use with
1. sklearn.model_selection.GridSearchCV()
2. hyperopt.hp
3. scikit-optimize (in a future update)
"""

import numpy as np

from hyperopt import hp
from random import randrange as sp_randrange
from scipy.stats import randint as sp_randint
from sklearn.gaussian_process.kernels import ConstantKernel, DotProduct, Matern, RationalQuadratic, RBF, WhiteKernel


RANDOM_STATE = 12345


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
rand_space_lr = {
    'LR__warm_start': [True, False],
    'LR__fit_intercept': [True, False],
    'LR__tol': sp_randrange(0.00001, 0.0001),
    'LR__C': sp_randrange(0.05, 3.0),
    'LR__max_iter': sp_randint(80, 200),
    'LR__scale': [0, 1],
    'LR__normalize': [0, 1],
    'LR__multi_class': 'auto',
    'LR__class_weight': 'balanced'
}

params_lr = {
    'LR__warm_start': [True, False],
    'LR__fit_intercept': [True, False],
    'LR__tol': [0.00001, 0.0001],
    'LR__C': [0.05, 0.1, 0.2, 0.5, 1.0, 3.0],
    'LR__max_iter': [80, 120, 200],
    'LR__scale': [0, 1],
    'LR__normalize': [0, 1],
    'LR__multi_class': 'auto',
    'LR__class_weight': 'balanced'
}

# Support Vector Classifier
hp_space_svc = {
    'C': hp.loguniform('C', np.log(1), np.log(1000)),
    'kernel': hp.choice('kernel', ['linear', 'sigmoid', 'poly', 'rbf']),
    'gamma': hp.uniform('gamma', 0, 20),
    'scale': hp.choice('scale', [0, 1]),
    'normalize': hp.choice('normalize', [0, 1]),
    'max_iter': hp.choice('max_iter', [10000])
}
params_svc = {
    'SVC__C': np.logspace(0, 3, 4),
    'SVC__kernel': ['linear', 'rbf', 'poly'],
    'SVC__gamma': ['scale', 'auto'],
    'SVC__max_iter': [10000]
}

# Support Vector Regressor
hp_space_svr = {
    'C': hp.loguniform('C', np.log(1), np.log(1e3)),
    'kernel': hp.choice('kernel', ['linear', 'rbf', 'poly', 'sigmoid']),
    # ['scale', 'auto']
    'gamma': hp.loguniform('gamma', np.log(1e-2), np.log(1e2)),
    'epsilon': hp.choice('epsilon', [0.1]),
    'max_iter': hp.choice('max_iter', [10000])
}
params_svr = {
    'SVR__C': np.logspace(0, 3, 4),
    'SVR__kernel': ['linear', 'rbf', 'poly', 'sigmoid'],
    'SVR__gamma': np.logspace(-2, 2, 5),  # ['scale', 'auto'],
    'SVR__epsilon': [0.1],
    'SVR__max_iter': [10000]
}

# Kernel Ridge Regressor
hp_space_krr = {
    'alpha': hp.loguniform('alpha', np.log(1), np.log(1e3)),
    'kernel': hp.choice('kernel', ['linear', 'rbf', 'poly', 'sigmoid']),
    'gamma': hp.loguniform('gamma', np.log(1e-2), np.log(1e2)),
}
params_krr = {
    'KRR__alpha': np.logspace(0, 3, 4),
    'KRR__kernel': ['linear', 'rbf', 'poly', 'sigmoid'],
    'KRR__gamma': np.logspace(-2, 2, 5),
}

# K Nearest Neighbor
hp_space_knn = {
    'n_neighbors': hp.choice('n_neighbors', range(2, 80)),
    'scale': hp.choice('scale', [0, 1]),
    'normalize': hp.choice('normalize', [0, 1]),
}
params_knn = {
    'KNN__n_neighbors': [2, 4, 8, 16, 32, 80],
    'KNN__scale': [0, 1],
    'KNN__normalize': [0, 1]
}

# Multilayer Perceptron
hp_space_mlp = {
    'hidden_layer_sizes': hp.choice('hidden_layer_sizes', [
        (20), (40), (75), (100),
        (20, 20), (40, 40), (75, 75), (100, 100),
        (20, 40), (40, 20), (40, 75), (75, 40), (75, 100), (100, 75)
    ]),
    'activation': hp.choice('activation', ['logistic', 'tanh', 'relu']),
    'solver': hp.choice('solver', ['adam']),
    'alpha': hp.loguniform('alpha', np.log(0.0001), np.log(0.001)),
    'learning_rate_init': hp.loguniform('learning_rate_init', np.log(0.001), np.log(0.01))
}
params_mlp = {
    'MLP__hidden_layer_sizes': [
        (20), (40), (75), (100),
        (20, 20), (40, 40), (75, 75), (100, 100),
        (20, 40), (40, 20), (40, 75), (75, 40), (75, 100), (100, 75)
    ],
    'MLP__activation': ['logistic', 'tanh', 'relu'],
    'MLP__solver': ['adam'],
    'MLP__alpha': [0.001, 0.0001, 0.00001],
    'MLP__learning_rate_init': [0.01, 0.001, 0.0001]
}

# Random Forest
hp_space_rf = {
    'max_depth': hp.choice('max_depth', range(5, 20)),
    'max_features': hp.choice('max_features', range(1, 5)),
    'n_estimators': hp.choice('n_estimators', range(20, 300, 10)),
    'criterion': hp.choice('criterion', ["gini", "entropy"]),
}
params_rf = {
    'RF__max_depth': [5, 10, 20],
    'RF__max_features': [1, 2, 5],
    'RF__n_estimators': [15, 30, 50, 80, 120],
    'RF__criterion': ['gini', 'entropy']
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
    'XGB__max_depth': [5, 10, 20],
    'XGB__learning_rate': [0.01, 0.05, 0.1, 0.3],
    'XGB__n_estimators': [20, 40, 70, 110, 150],
    'XGB__gamma': [0, 0.05, 0.1, 0.2, 0.5],
    'XGB__min_child_weight': [1, 2, 4, 10],
    'XGB__subsample': [0.1, 0.2, 0.4, 1.0],
    'XGB__colsample_bytree': [0.1, 0.2, 0.4, 1.0]
}

# Gaussian Process Regression
hp_space_gpr = {
    'kernel': hp.choice('kernel', [
        DotProduct(),
        DotProduct() + WhiteKernel(2e-1),
        RationalQuadratic(length_scale=1.0, alpha=0.1),
        RationalQuadratic(length_scale=1.0, alpha=0.1) + WhiteKernel(1e-1),
        RBF(length_scale=1.0, length_scale_bounds=(1e-1, 10.0)),
        RBF(length_scale=1.0, length_scale_bounds=(
            1e-1, 10.0)) + WhiteKernel(1e-1),
        Matern(length_scale=1.0, length_scale_bounds=(1e-1, 10.0), nu=1.5),
        Matern(length_scale=1.0, length_scale_bounds=(
            1e-1, 10.0), nu=1.5) + WhiteKernel(2e-1)
    ]),
    'alpha': hp.loguniform('alpha', np.log(1e-12), np.log(1e-8)),
    'random_state': hp.choice('random_state', [RANDOM_STATE])
}
params_gpr = {
    'kernel': [
        DotProduct(),
        DotProduct() + WhiteKernel(2e-1),
        RationalQuadratic(length_scale=1.0, alpha=0.1),
        RationalQuadratic(length_scale=1.0, alpha=0.1) + WhiteKernel(1e-1),
        RBF(length_scale=1.0, length_scale_bounds=(1e-1, 10.0)),
        RBF(length_scale=1.0, length_scale_bounds=(
            1e-1, 10.0)) + WhiteKernel(1e-1),
        Matern(length_scale=1.0, length_scale_bounds=(1e-1, 10.0), nu=1.5),
        Matern(length_scale=1.0, length_scale_bounds=(
            1e-1, 10.0), nu=1.5) + WhiteKernel(2e-1)
    ],
    'alpha': [1e-8, 1e-10, 1e-12],
    'random_state': [RANDOM_STATE]
}


def get_hyperparams(model_type: str, backend: str):
    global params_gpr, params_mlp, params_svr, params_xgboost
    global hp_space_gpr, hp_space_mlp, hp_space_svr, hp_space_xgboost

    if model_type == 'MLP':
        if backend == 'grid_search':
            return params_mlp
        else:
            return hp_space_mlp
    elif model_type == 'SVR':
        if backend == 'grid_search':
            return params_svr
        else:
            return hp_space_svr
    elif model_type == 'XGB':
        if backend == 'grid_search':
            return params_xgboost
        else:
            return hp_space_xgboost
    elif model_type == 'GPR':
        if backend == 'grid_search':
            return params_gpr
        else:
            return hp_space_gpr
    else:
        print('Invalid Model Type')
        assert False
