#!/usr/bin/env python

import argparse
import numpy as np
import os
import pandas as pd
import pickle
import warnings

from hyperopt import hp, fmin, tpe, STATUS_OK, Trials

from sklearn import ensemble, linear_model, naive_bayes, neighbors, neural_network
from sklearn import preprocessing, svm, tree
from sklearn.model_selection import cross_val_score, KFold

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics import accuracy_score, average_precision_score, f1_score, matthews_corrcoef, precision_score
from sklearn.metrics import recall_score, roc_auc_score, make_scorer

from typing import Any, Callable, Dict, List, Optional


warnings.filterwarnings('ignore')

regression_models = {
    'dtr': tree.DecisionTreeRegressor(),
    'linear': linear_model.LinearRegression(),
    'logistic': linear_model.LogisticRegression(),
    'knr': neighbors.KNeighborsRegressor(),
    'svr': svm.SVR(),
    'svr_rbf': svm.SVR(kernel='rbf', C=100, gamma=0.1, epsilon=.1),
    'svr_lin': svm.SVR(kernel='linear', C=100, gamma='auto'),
    'svr_poly': svm.SVR(kernel='poly', C=100, gamma='auto', degree=3, epsilon=.1, coef0=1),
    'gbr': ensemble.GradientBoostingRegressor(),
    'rf': ensemble.RandomForestRegressor(n_estimators=100, criterion='mse')
}

regression_scores = {
    'MSE': mean_squared_error,
    'MAE': mean_absolute_error,
    'r2': r2_score
}

regression_summary = {
    'MSE': ['mean', 'std'],
    'MAE': ['mean', 'std'],
    'r2': ['mean', 'std']
}

classification_models = {
    'sgd': linear_model.SGDClassifier(),
    'ridge': linear_model.RidgeClassifier(),
    'logistic': linear_model.LogisticRegression(multi_class='multinomial'),
    'gnb': naive_bayes.GaussianNB(),
    'knr': neighbors.KNeighborsClassifier(),
    'mlp': neural_network.MLPClassifier(),
    'dtc': tree.DecisionTreeClassifier(),
    'rf': ensemble.RandomForestClassifier()
}

classification_scores = {
    'acc': accuracy_score,
    'avg_precision': average_precision_score,
    'f1': f1_score,
    'mcc': matthews_corrcoef,
    'precision': precision_score,
    'recall': recall_score,
    'roc': roc_auc_score
}

classification_summary = {
    'acc': ['mean', 'std'],
    'avg_precision': ['mean', 'std'],
    'f1': ['mean', 'std'],
    'precision': ['mean', 'std'],
    'recall': ['mean', 'std'],
    'roc': ['mean', 'std']
}

space_knn = {
    'n_neighbors': hp.choice('n_neighbors', range(2, 80)),
    'scale': hp.choice('scale', [0, 1]),
    'normalize': hp.choice('normalize', [0, 1]),
}

space_lr = {
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

space_rf = {
    'max_depth': hp.choice('max_depth', range(5, 20)),
    'max_features': hp.choice('max_features', range(1, 5)),
    'n_estimators': hp.choice('n_estimators', range(15, 120, 5)),
    'criterion': hp.choice('criterion', ["gini", "entropy"]),
}

space_svc = {
    'C': hp.uniform('C', 0, 100),
    'kernel': hp.choice('kernel', ['linear', 'sigmoid', 'poly', 'rbf']),
    'gamma': hp.uniform('gamma', 0, 20),
    'scale': hp.choice('scale', [0, 1]),
    'normalize': hp.choice('normalize', [0, 1]),
}

space_xgboost = {
    'max_depth': hp.choice('max_depth', range(5, 20, 1)),
    'learning_rate': hp.quniform('learning_rate', 0.01, 0.3, 0.005),
    'n_estimators': hp.choice('n_estimators', range(20, 150, 5)),
    'gamma': hp.quniform('gamma', 0, 0.50, 0.005),
    'min_child_weight': hp.quniform('min_child_weight', 1, 10, 1),
    'subsample': hp.quniform('subsample', 0.1, 1, 0.005),
    'colsample_bytree': hp.quniform('colsample_bytree', 0.1, 1.0, 0.005)
}


def load_xy(filename: str, target_col: int):
    _, ext = os.path.splitext(filename)
    if ext == '.xlsx':
        df = pd.read_excel(filename, index_col=0).dropna()
    elif ext == '.csv':
        df = pd.read_csv(filename, index_col=0).dropna()
    else:
        print('Unable to load file with unknown extension')
        return None, None
    if target_col == -1:
        X = df.iloc[:, :-1]._get_numeric_data()
        y = df.iloc[:, -1]
    else:
        feature_cols = [x for x in df.columns if x != df.columns[target_col]]
        X = df.loc[:, feature_cols]._get_numeric_data()
        y = df.iloc[:, target_col]
    return X.values, y.values


def evaluate(model: Any, X_train: np.ndarray, y_train: np.ndarray,
             X_test: np.ndarray, y_test: np.ndarray, scores: Dict[str, Any]):
    obj = model.fit(X_train, y_train)
    y_pred = obj.predict(X_test)

    results = {}
    for score_name, score_fn in scores.items():
        try:
            results[score_name] = score_fn(y_test, y_pred)
        except ValueError as e:
            # if e == 'multiclass format is not supported':
            print(e)
            results[score_name] = np.nan
    return results


def run_kfold(X: np.ndarray, y: np.ndarray, models: Dict[str, Any],
              scores: Dict[str, Any], n_splits: int = 10):
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=12345)

    results = []
    for model_name, model in models.items():
        print(f"----- {model_name} -----")
        for i, (train_index, test_index) in enumerate(kf.split(X)):
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]
            temp_results = evaluate(
                model, X_train, y_train, X_test, y_test, scores)
            print(f"Fold = {i}: {temp_results}")

            temp_results['method'] = model_name
            temp_results['fold'] = i
            results.append(temp_results)

    return pd.DataFrame(results)


def get_model_from_params(params):
    model = XGBClassifier(
        # silent=False,
        # scale_pos_weight=1,
        max_depth=params['max_depth'],
        learning_rate=params['learning_rate'],
        # tree_method = 'gpu_hist',
        # gpu_id=0,
        n_estimators=params['n_estimators'],
        gamma=params['gamma'],
        min_child_weight=params['min_child_weight'],
        subsample=params['subsample'],
        colsample_bytree=params['colsample_bytree']
        # objective='binary:logistic',
        # reg_alpha = 0.3,
    )
    return model


def get_regression_model_from_params(params):
    # https://xgboost.readthedocs.io/en/latest/python/python_api.html
    model = XGBRegressor(
        n_estimators=params['n_estimators'],
        max_depth=params['max_depth'],
        learning_rate=params['learning_rate'],
        # verbosity=3, # (0=silent, 3=debug)
        # objective='...',
        # booster='...', # gbtree, gblinear or dart
        # tree_method='auto',
        # n_jobs=...,
        gamma=params['gamma'],
        min_child_weight=params['min_child_weight'],
        # max_delta_step=...,
        subsample=params['subsample'],
        colsample_bytree=params['colsample_bytree']
        # colsample_bylevel=...,
        # reg_alpha = 0.3,
        # reg_lambda=...,
        # scale_pos_weight=1,
        # base_score=...,
        # random_state=...
    )
    return model


def loss_metric(params):
    """
    Calculates the loss metric for classification
    Note the negation for -cv_scores.mean() as we typically wish to
    maximize accuracy, AUC, MCC, r2, ...
    """
    global X_train, y_train, X_valid, y_valid, metric

    cv_scores = cross_val_score(
        get_model_from_params(params),
        X_train, y_train,
        scoring=make_scorer(metric),
        cv=5,
        n_jobs=-1  # use all cores if possible
    )
    return {'loss': -cv_scores.mean(), 'status': STATUS_OK}


def loss_metric2(params):
    """
    Calculates the loss metric
    Note the postive sign for cv_scores.mean() as we typically
    minimize MAE, MSE, RMSE (but not r2)
    """
    global X_train, y_train, X_valid, y_valid, metric

    cv_scores = cross_val_score(
        get_model_from_params(params),
        X_train, y_train,
        scoring=make_scorer(metric),
        cv=5,
        n_jobs=-1  # use all cores if possible
    )
    return {'loss': cv_scores.mean(), 'status': STATUS_OK}


def tune(my_fn, search_space, algo=tpe.suggest, max_evals=100, seed=12345):
    global metric

    trials = Trials()
    result = fmin(
        fn=my_fn,
        space=search_space,
        algo=algo,
        trials=trials,
        max_evals=max_evals,
        rstate=np.random.RandomState(seed=seed)
    )
    return {
        'result': result,
        'trials': trials
    }


def create_single_model(model: Any, X: np.ndarray, y: np.ndarray,
                        filename: Optional[str] = None):
    obj = model.fit(X, y)

    if filename is None:
        filename = f'model.pickle'
    with open(filename, 'wb') as f:
        pickle.dump(obj, f)
    print(f'Saved: {filename}')


def run_ML(csv_file: str, target_col: int,
           models: Dict[str, Callable[..., float]],
           scores: Dict[str, Callable[..., float]],
           summary: Dict[str, List[str]]):
    X, y = load_xy(csv_file, target_col)

    scaler = preprocessing.MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    df_raw = run_kfold(X_scaled, y, models, scores, n_splits=5)

    cols = ['fold', 'method'] + list(scores.keys())
    df_raw = df_raw[cols]

    print('----- results.csv (raw) -----')
    print(df_raw)
    df_raw.to_csv('results.csv')

    print('----- summary.csv (data averaged across k-folds) -----')
    df_summary = df_raw.groupby('method').agg(summary)
    print(df_summary)
    return df_summary


def run_classification(csv_file: str, target_col: int, sort_by: str = 'acc'):
    df_summary = run_ML(csv_file, target_col, classification_models, classification_scores, classification_summary)
    df_summary.to_csv('summary.csv')
    df_summary = df_summary.sort_values((sort_by, 'mean'), ascending=True)
    df_summary.to_excel('summary.xlsx')
    return df_summary


def run_regression(csv_file: str, target_col: int, sort_by: str = 'MSE'):
    df_summary = run_ML(csv_file, target_col, regression_models, regression_scores, regression_summary)
    df_summary.to_csv('summary.csv')
    df_summary = df_summary.sort_values((sort_by, 'mean'), ascending=True)
    df_summary.to_excel('summary.xlsx')
    return df_summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, help='Input .csv file')
    parser.add_argument('--target_col', type=int, default=-1, help='Target Column')
    parser.add_argument('--task', type=str, choices=['regression', 'classification'])
    args = parser.parse_args()

    if args.task == 'regression':
        df_summary = run_regression(args.file, args.target_col)
    elif args.task == 'classification':
        df_summary = run_classification(args.file, args.target_col)
    else:
        quit()

    print(df_summary)
    best_model = df_summary.index[0]
    print(best_model)
    # create_single_model(best_model, X, y)
