#!/usr/bin/env python

"""
ml-fits.py

Example code for building models in scikit-learn and xgboost
"""

import numpy as np
import pandas as pd
import seaborn as sns
import warnings

from sklearn.metrics import accuracy_score, mean_absolute_error
from sklearn.model_selection import cross_val_score, train_test_split

warnings.filterwarnings('ignore')


def load_column_dataset(folder, train_file='train.csv', test_file='test.csv', index_col=None):
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


if __name__ == "__main__":
    
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

