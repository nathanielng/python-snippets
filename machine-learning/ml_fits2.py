#!/usr/bin/env python

import argparse
import os
import pandas as pd
import pickle
import warnings

from sklearn import datasets, linear_model, preprocessing, svm
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier. RandomForestRegressor
from sklearn.linear_model import SGDClassifier, LogisticRegression, RidgeClassifier
from sklearn.model_selection import KFold
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics import accuracy_score, average_precision_score, f1_score, precision_score, recall_score, roc_auc_score

from typing import Any, Dict, Optional


warnings.filterwarnings('ignore')

models = {
    'dtr': DecisionTreeRegressor(),
    'linear': linear_model.LinearRegression(),
    'logistic': linear_model.LogisticRegression(),
    'knr': KNeighborsRegressor(),
    'svr': svm.SVR(),
    'svr_rbf': svm.SVR(kernel='rbf', C=100, gamma=0.1, epsilon=.1),
    'svr_lin': svm.SVR(kernel='linear', C=100, gamma='auto'),
    'svr_poly': svm.SVR(kernel='poly', C=100, gamma='auto', degree=3, epsilon=.1, coef0=1),
    'gbr': GradientBoostingRegressor(),
    'rf': RandomForestRegressor(n_estimators=100, criterion='mse')
}

scores = {
    'MSE': mean_squared_error,
    'MAE': mean_absolute_error,
    'r2': r2_score
}

classification_models = {
    'sgd': SGDClassifier(),
    'ridge': RidgeClassifier(),
    'logistic': LogisticRegression(multi_class='multinomial'),
    'gnb': GaussianNB(),
    'knr': KNeighborsClassifier(),
    'mlp': MLPClassifier(),
    'dtc': DecisionTreeClassifier(),
    'rf': RandomForestClassifier()
}

classification_scores = {
    'acc': accuracy_score,
    'avg_precision': average_precision_score,
    'f1': f1_score,
    'precision': precision_score,
    'recall': recall_score,
    'roc': roc_auc_score
}

def load_xy(filename: str):
    prefix, ext = os.path.splitext(filename)
    if ext == '.xlsx':
        df = pd.read_excel(filename, index_col=0)
    elif ext == '.csv':
        df = pd.read_csv(filename, index_col=0)
    else:
        print('Unable to load file with unknown extension')
        return None, None
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    return X.values, y.values


def evaluate(model: Any, X_train: np.ndarray, y_train: np.ndarray,
             X_test: np.ndarray, y_test: np.ndarray, scores: Dict[str, Any]):
    obj = model.fit(X_train, y_train)
    y_pred = obj.predict(X_test)

    results = {}
    for score_name, score_fn in scores.items():
        results[score_name] = score_fn(y_test, y_pred)
    return results


def run_kfold(X: np.ndarray, y: np.ndarray, n_splits: int = 10):
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


def create_single_model(model_name: str, X: np.ndarray, y: np.ndarray,
                        filename: Optional[str] = None):
    model = models[model_name]
    obj = model.fit(X, y)

    if filename is None:
        filename = f'{model_name}.pickle'
    with open(filename, 'wb') as f:
        pickle.dump(obj, f)
    print(f'Saved: {filename}')


def get_summary(filename: str):
    X, y = load_xy(filename)
    df = run_kfold(X, y, 10)

    cols = ['fold', 'method'] + list(scores.keys())
    df = df[cols]

    print('----- results.csv (raw) -----')
    print(df)
    df.to_csv('results.csv')

    print('----- summary.csv (data averaged across k-folds) -----')
    df_summary = df.groupby('method').agg({
        'MSE': ['mean', 'std'],
        'MAE': ['mean', 'std'],
        'r2': ['mean', 'std']
    })
    print(df_summary)
    df_summary.to_csv('summary.csv')
    df_summary = df_summary.sort_values(('MSE', 'mean'), ascending=True)
    df_summary.to_excel('summary.xlsx')

    best_model = df_summary.index[0]
    create_single_model(best_model, X, y)

    return df_summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', help='Input .csv file')
    args = parser.parse_args()

    df_summary = get_summary(args.file)
