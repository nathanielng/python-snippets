#!/usr/bin/env python

"""
ml-fits.py

Example code for building models in scikit-learn and xgboost
"""

import numpy as np
import pandas as pd
import seaborn as sns

from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split


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


def submit_to_kaggle(model, sample_submission, submission_file='submission.csv'):
    submission = pd.read_csv(sample_submission, index_col=0)
    y_pred = model.predict(X_test)
    assert np.all(submission.index == X_test.index)
    submission.iloc[:, -1] = y_pred
    submission.to_csv(submission_file)


if __name__ == "__main__":
    
    # ----- Random Forest Example -----
    from sklearn.ensemble import RandomForestClassifier

    rf = RandomForestClassifier(n_estimators=n_estimators)
    rf.fit(X_train, y_train)
    print(f'Random Forest{n_estimators}: {evaluate_model_mae(rf, X_val, y_val)}')


    # ----- XGBoost Example
    from xgboost import XGBRegressor

    xgb = XGBRegressor(n_estimators=n_estimators)
    xgb.fit(X_train, y_train)
    print(f'XGB: {evaluate_model_mae(xgb, X_val, y_val)}')    

