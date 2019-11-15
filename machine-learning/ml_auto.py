#!/usr/bin/env python

# Performs AutoML on a dataset
# Assumptions:
# - last column is the target column for prediction
# - first column is the index column

import argparse
import autosklearn.regression
import autosklearn.classification
import os
import pandas as pd
import sklearn.model_selection
import sklearn.metrics

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def split_dataframe(df):
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=1)
    return X_train, X_test, y_train, y_test


def run_autosklearn_regression(X_train, y_train, tlftt, prtl):
    feature_types = (['numerical'] * X_train.shape[1])
    model = autosklearn.regression.AutoSklearnRegressor(
        time_left_for_this_task=tlftt,
        per_run_time_limit=prtl,
        tmp_folder='/tmp/autosklearn_regression_tmp',
        output_folder='tmp/autosklearn_regression_out'
    )
    model.fit(X_train, y_train, feat_type=feature_types)
    return model


def run_autosklearn_classification(X_train, y_train, tlftt, prtl):
    feature_types = (['numerical'] * X_train.shape[1])
    model = autosklearn.classification.AutoSklearnClassifier(
        time_left_for_this_task=tlftt,
        per_run_time_limit=prtl,
        tmp_folder='/tmp/autosklearn_classification_tmp',
        output_folder='tmp/autosklearn_classification_out'
    )
    model.fit(X_train, y_train, feat_type=feature_types)
    return model


def evaluate_regression_model(model, X_test, y_test):
    print(model.show_models())
    y_pred = model.predict(X_test)
    print(f"R2 score: {sklearn.metrics.r2_score(y_test, y_pred)}")
    print(f"RMSE: {sklearn.metrics.mean_squared_error(y_test, y_pred)}")
    print(f"MAE: {sklearn.metrics.mean_absolute_error(y_test, y_pred)}")


def evaluate_classification_model(model, X_test, y_test):
    print(model.show_models())
    y_pred = model.predict(X_test)
    print(f"Accuracy Score: {sklearn.metrics.accuracy_score(y_test, y_pred)}")


def run_h2o(X_train, X_test):
    pass


def load_dataset(filename, drop_first_column=False):
    df = pd.read_csv(os.path.abspath(filename))
    if drop_first_column is True:
        df.drop(labels=df.columns[0], axis=1, inplace=True)
    return df


def main(args):
    df = load_dataset(args.file, args.drop_first_column)
    X_train, X_test, y_train, y_test = split_dataframe(df)

    sc = StandardScaler()
    if args.scale is True:
        X_train = sc.fit_transform(X_train)
        X_test = sc.transform(X_test)

    if args.engine == 'autosklearn':
        if args.model == 'classification':
            model = run_autosklearn_classification(
                X_train, y_train,
                args.time_left_for_this_task,
                args.per_run_time_limit)
            evaluate_classification_model(model, X_test, y_test)
        elif args.model == 'regression':
            model = run_autosklearn_regression(
                X_train, y_train,
                args.time_left_for_this_task,
                args.per_run_time_limit)
            evaluate_regression_model(model, X_test, y_test)
    elif args.engine == 'h2o':
        run_h2o(X_train, X_test)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file')
    parser.add_argument('--drop_first_column', action='store_true')
    parser.add_argument('--engine', default='autosklearn')
    parser.add_argument('--model', default='classification')
    parser.add_argument('--per_run_time_limit', default=30, type=int)
    parser.add_argument('--scale', action='store_true')
    parser.add_argument('--time_left_for_this_task', default=120, type=int)
    args = parser.parse_args()
    main(args)
