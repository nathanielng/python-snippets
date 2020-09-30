#!/usr/bin/env python

"""
ml_fits2.py

Intermediate-level code for building models in scikit-learn and xgboost
For basic-level code, see ml_fits.py
"""

import argparse
import catboost
import lightgbm
import numpy as np
import os
import pandas as pd
import pickle
import warnings
import xgboost as xgb

from hyperopt import hp, fmin, tpe, STATUS_OK, Trials

from sklearn import ensemble, gaussian_process, kernel_ridge, linear_model, naive_bayes, neighbors, neural_network
from sklearn import datasets, multiclass, pipeline, preprocessing, svm, tree
from sklearn.gaussian_process.kernels import ConstantKernel, RBF
from sklearn.model_selection import cross_val_score, KFold

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, make_scorer
from sklearn.metrics import accuracy_score, average_precision_score, f1_score, matthews_corrcoef, precision_score
from sklearn.metrics import recall_score, roc_auc_score
from sklearn.utils.multiclass import type_of_target

from typing import Any, Callable, Dict, List, Optional


warnings.filterwarnings('ignore')
RANDOM_STATE = 12345


gpr_kernel = ConstantKernel(
    1.0, (1e-3, 1e3)) * RBF(10, (1e-2, 1e2))

regression_models = {
    'cat': catboost.CatBoostRegressor(verbose=False),
    'dtr': tree.DecisionTreeRegressor(),
    'gbr': ensemble.GradientBoostingRegressor(),
    'gpr': gaussian_process.GaussianProcessRegressor(),
    'gpr2': gaussian_process.GaussianProcessRegressor(kernel=gpr_kernel),
    'knr': neighbors.KNeighborsRegressor(),
    'krr': kernel_ridge.KernelRidge(),
    'lasso': linear_model.Lasso(),
    'lgbm': lightgbm.LGBMRegressor(),
    'linear': linear_model.LinearRegression(),
    'logistic': linear_model.LogisticRegression(),
    'nb': naive_bayes.GaussianNB(),
    'nn': neural_network.MLPRegressor(hidden_layer_sizes=(100,), activation='relu', solver='adam'),
    'svr': svm.SVR(),
    'svr_rbf': svm.SVR(kernel='rbf', C=100, gamma=0.1, epsilon=.1),
    'svr_lin': svm.SVR(kernel='linear', C=100, gamma='auto'),
    'svr_poly': svm.SVR(kernel='poly', C=100, gamma='auto', degree=3, epsilon=.1, coef0=1),
    'ridge': linear_model.Ridge(),
    'rf': ensemble.RandomForestRegressor(n_estimators=100, criterion='mse'),
    'xgb': xgb.XGBRegressor()
}

regression_scores = {
    'MSE': mean_squared_error,
    'MAE': mean_absolute_error,
    'r2': r2_score
}
mae_scorer = make_scorer(mean_absolute_error, greater_is_better=False)
mse_scorer = make_scorer(mean_squared_error, greater_is_better=False)
r2_scorer = make_scorer(r2_score, greater_is_better=True)

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

multiclass_models = {
    'sgd': linear_model.SGDClassifier(),
    'ridge': linear_model.RidgeClassifier(),
    'logistic': linear_model.LogisticRegression(multi_class='multinomial'),
    'gnb': naive_bayes.GaussianNB(),
    'knr': neighbors.KNeighborsClassifier(),
    # 'mlp': neural_network.MLPClassifier(),
    'dtc': tree.DecisionTreeClassifier(),
    'rf': ensemble.RandomForestClassifier()
}

multiclass_scores = {
    'acc': accuracy_score,
    'avg_precision': average_precision_score,
}

multiclass_summary = {
    'acc': ['mean', 'std'],
    'avg_precision': ['mean', 'std'],
}


# ----- Scalers -----
scalers = {
    'box_cos': preprocessing.PowerTransformer(method='box-cox', standardize=False),
    'max_abs': preprocessing.MaxAbsScaler(),
    'min_max': preprocessing.MinMaxScaler(),
    'mm_quantile': pipeline.Pipeline([
        ('min_max', preprocessing.MinMaxScaler()),
        ('quantile', preprocessing.QuantileTransformer(
            output_distribution='normal', random_state=RANDOM_STATE))
    ]),
    'normalizer': preprocessing.Normalizer(),
    'quantile': preprocessing.QuantileTransformer(),
    'quantile1': preprocessing.QuantileTransformer(output_distribution='normal', random_state=RANDOM_STATE),
    'robust': preprocessing.RobustScaler(),
    'standard': preprocessing.StandardScaler(),
    'yeo_johnson': preprocessing.PowerTransformer(method='yeo-johnson', standardize=True)
}


def load_df(filename: str):
    _, ext = os.path.splitext(filename)
    if ext == '.xlsx':
        df = pd.read_excel(filename, index_col=0).dropna()
    elif ext == '.csv':
        df = pd.read_csv(filename, index_col=0).dropna()
    else:
        print('Unable to load file with unknown extension')
        return None
    return df


def df_to_xy(df: pd.DataFrame, target_col: int):
    if target_col == -1:
        X = df.iloc[:, :-1]._get_numeric_data()
        y = df.iloc[:, -1]
    else:
        feature_cols = [x for x in df.columns if x != df.columns[target_col]]
        X = df.loc[:, feature_cols]._get_numeric_data()
        y = df.iloc[:, target_col]
    return X.values, y.values


def load_xy(filename: str, target_col: int):
    df = load_df(filename)
    X, y = df_to_xy(df, target_col)
    return X, y


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
              scores: Dict[str, Any], n_splits: int = 10,
              multiclass_strat: Optional[str] = ''):
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=12345)

    results = []
    for model_name, model in models.items():
        print(f"----- {model_name} -----")
        for i, (train_index, test_index) in enumerate(kf.split(X)):
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]
            model2 = model
            if multiclass_strat == 'ovr':
                model2 = multiclass.OneVsRestClassifier(model)
            elif multiclass_strat == 'ovo':
                model2 = multiclass.OneVsOneClassifier(model)
            
            temp_results = evaluate(
                model2, X_train, y_train, X_test, y_test, scores)
            print(f"Fold = {i}: {temp_results}")

            temp_results['method'] = model_name
            temp_results['fold'] = i
            results.append(temp_results)

    return pd.DataFrame(results)


def get_classification_model_from_params(params):
    model = xgb.XGBClassifier(
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
    model = xgb.XGBRegressor(
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
        # random_state=...,
        # gpu_id=None  # gpu_id=0 for first GPU
    )
    return model


def loss_metric(params):
    """
    Calculates a cross-validated loss metric
    Use metric_sign=1, to get cv_scores.mean() in order to minimize
      metric = mean_absolute_error, mean_squared_error
    Use metric_sign=-1, to get -cv_scores.mean() in order to maximize
      metric = accuracy_score, average_precision_score, f1_score, matthews_corrcoef, precision_score
               recall_score, roc_auc_score, r2_score, ...
    Set get_model_from_params to a function that takes params as an
    input and returns a model
    """
    global X_train, y_train, X_valid, y_valid, metric, metric_sign, Model

    cv_scores = cross_val_score(
        Model(**params),
        X_train, y_train,
        scoring=make_scorer(metric),
        cv=5,
        n_jobs=-1  # use all cores if possible
    )
    return {
        'loss': metric_sign * cv_scores.mean(),
        'status': STATUS_OK
    }


def hyp_tune(my_fn, search_space, algo=tpe.suggest, max_evals=100, seed=12345):
    """
    Hyperparamter tuning of a model
    """
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

    df_x = pd.DataFrame(trials.idxs_vals[1])
    loss = pd.DataFrame(trials.results)
    df_r = pd.concat((df_x, loss), axis=1)
    return result, trials, df_r


def results2df(results, trials):
    df_x = pd.DataFrame(trials.idxs_vals[1])
    loss = pd.DataFrame(trials.results)
    df_r = pd.concat((df_x, loss), axis=1)
    return df_r


def plot_results(df_r: pd.DataFrame):
    _, ax = plt.subplots(1, 1, figsize=(12, 5))
    ax.semilogy(df_r.index, df_r['loss'], marker='+', markeredgecolor='red', markersize=5, markeredgewidth=1);
    ax.set_xlabel('Iteration number');
    ax.set_ylabel('Loss');
    ax.grid(True);


# ----- Machine Learning Models -----
def create_single_model(model: Any, X: np.ndarray, y: np.ndarray,
                        filename: Optional[str] = None):
    obj = model.fit(X, y)

    if filename is None:
        filename = f'model.pickle'
    with open(filename, 'wb') as f:
        pickle.dump(obj, f)
    print(f'Saved: {filename}')


def select_model_type(model_type, y):
    global regression_models, regression_scores, regression_summary
    global classification_models, classification_scores, classification_summary
    global multiclass_models, multiclass_scores, multiclass_summary

    multiclass_strat = ''
    sort_by, ascending = 'acc', False

    if model_type == 'auto':
        model_type = type_of_target(y)
        if model_type == 'multiclass' and len(np.unique(y)) > 20:
            model_type = 'continuous'
        print(f'Automatically selected model type: {model_type}')

    if model_type == 'continuous':
        # sort_by, ascending = 'MSE', True
        sort_by, ascending = 'r2', False
        models = regression_models
        scores = regression_scores
        summary = regression_summary
    elif model_type == 'binary':
        models = classification_models
        scores = classification_scores
        summary = classification_summary
    elif model_type == 'multiclass':
        models = multiclass_models
        scores = multiclass_scores
        summary = multiclass_summary
        multiclass_strat = 'ovr'
        y = preprocessing.label_binarize(y, classes=np.unique(y))
    return multiclass_strat, sort_by, ascending, models, scores, summary, multiclass_strat, y


def run_ML(X: np.array, y: np.array,
           model_type: str,
           multiclass_strat: Optional[str] = None):
    """
    Runs machine learning on all models specified in the parameter: models
    and evaluates them on all metrics in the paramter: scores
    """
    multiclass_strat, sort_by, ascending, models, scores, summary, multiclass_strat, y \
        = select_model_type(model_type, y)

    scaler = preprocessing.MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    df_raw = run_kfold(X_scaled, y, models, scores,
                       n_splits=5, multiclass_strat=multiclass_strat)

    cols = ['fold', 'method'] + list(scores.keys())
    df_raw = df_raw[cols]

    print('----- results.csv (raw) -----')
    print(df_raw)
    df_raw.to_csv('results.csv')

    print('----- summary.csv (data averaged across k-folds) -----')
    df_summary = df_raw.groupby('method').agg(summary)
    df_summary.to_csv('summary.csv')
    df_summary = df_summary.sort_values((sort_by, 'mean'), ascending=ascending)
    print(df_summary)
    df_summary.to_excel('summary.xlsx')
    return df_summary


def main(args):
    if args.demo:
        if args.task == 'regression':
            X, y = datasets.load_diabetes(return_X_y=True)
        elif args.task == 'classification':
            X, y = datasets.load_breast_cancer(return_X_y=True)
        elif args.task == 'multiclass':
            X, y = datasets.load_digits(return_X_y=True)
    else:
        X, y = load_xy(args.file, args.target_col)

    if args.task == 'regression':
        df_summary = run_ML(X, y, model_type='continuous')
    else:
        df_summary = run_ML(X, y, model_type='auto')

    best_model = df_summary.index[0]
    print(f'Best model: {best_model}')
    # create_single_model(best_model, X, y)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, help='Input .csv file')
    parser.add_argument('--target_col', type=int, default=-1, help='Target Column')
    parser.add_argument('--task', type=str, choices=['regression', 'classification', 'multiclass'])
    parser.add_argument('--demo', action='store_true', help='Run classification or regression demo')
    args = parser.parse_args()
    main(args)
