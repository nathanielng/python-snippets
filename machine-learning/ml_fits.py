#!/usr/bin/env python

"""
ml_fits.py

Basic code for building models in scikit-learn and xgboost
For intermediate-level code, see ml_fits2.py
"""

import argparse
import numpy as np
import pandas as pd
import seaborn as sns
import warnings

from sklearn.metrics import accuracy_score, mean_absolute_error
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn import preprocessing

warnings.filterwarnings('ignore')


def load_column_dataset(folder, train_file='train.csv', test_file='test.csv', index_col=None):
    """
    Loads a dataset, assuming that the training data is in train.csv
    and the test data is in test.csv and that the last column is the target column.
    """
    if index_col is None:
        df_train = pd.read_csv(f'{folder}/{train_file}')
        df_test = pd.read_csv(f'{folder}/{test_file}')
    else:
        df_train = pd.read_csv(f'{folder}/{train_file}', index_col=index_col)
        df_test = pd.read_csv(f'{folder}/{test_file}', index_col=index_col)

    X = df_train.iloc[:, :-1]
    y = df_train.iloc[:, -1]
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2)
    X_test = df_test
    return X_train, X_val, X_test, y_train, y_val


def evaluate_model_mae(model, X_val, y_val):
    y_pred = model.predict(X_val)
    mae = mean_absolute_error(y_pred, y_val)
    return mae


def evaluate_model_acc(model, X_val, y_val):
    y_pred = model.predict(X_val)
    acc = accuracy_score(y_pred, y_val)
    return acc


def cross_val_score(model, X_train, y_train, cv=5):
    score = cross_val_score(model, X_train, y_train, cv=cv)
    return score.mean()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder')
    args = parser.parse_args()

    X_train, X_val, X_test, y_train, y_val = load_column_dataset(args.folder)

    scaler = preprocessing.MinMaxScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # ----- Random Forest Example -----
    from sklearn.ensemble import RandomForestClassifier

    rf = RandomForestClassifier(n_estimators=n_estimators)
    rf.fit(X_train, y_train)
    print(f'Random Forest, n={n_estimators}: {evaluate_model_mae(rf, X_val, y_val)}')


    # ----- XGBoost Example
    from xgboost import XGBRegressor

    xgb = XGBRegressor(n_estimators=n_estimators)
    xgb.fit(X_train, y_train)
    print(f'XGB, n={n_estimators}: {evaluate_model_mae(xgb, X_val, y_val)}')


    # ----- Regression Example -----
    from sklearn.linear_model import LinearRegression, Ridge, Lasso

    lr = LinearRegression(normalize=True)
    lr.fit(X_train, y_train)
    print(f'LinearRegression: {evaluate_model_mae(lr, X_val, y_val)}')
