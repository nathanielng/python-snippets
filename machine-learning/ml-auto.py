import argparse
import autosklearn.regression
import os
import pandas as pd
import sklearn.model_selection
import sklearn.metrics

from sklearn.model_selection import train_test_split


def split_dataframe(df):
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=1)
    return X_train, X_test, y_train, y_test


def run_autosklearn(args):
    df = pd.read_csv(os.path.abspath(args.file))
    df.drop(labels=['Sl. No.'], axis=1, inplace=True)
    X_train, X_test, y_train, y_test = split_dataframe(df)
    feature_types = (['numerical'] * X_train.shape[1])
    model = autosklearn.regression.AutoSklearnRegressor(
        time_left_for_this_task=120,
        per_run_time_limit=30,
        tmp_folder='/tmp/autosklearn_regression_tmp',
        output_folder='tmp/autosklearn_regression_out'
    )
    model.fit(X_train, y_train, feat_type=feature_types)

    print(model.show_models())
    y_pred = model.predict(X_test)
    print(f"R2 score: {sklearn.metrics.r2_score(y_test, y_pred)}")
    print(f"RMSE: {sklearn.metrics.mean_squared_error(y_test, y_pred)}")
    print(f"MAE: {sklearn.metrics.mean_absolute_error(y_test, y_pred)}")


def run_h2o(args):
    df = pd.read_csv(os.path.abspath(args.file))
    df.drop(labels=['Sl. No.'], axis=1, inplace=True)


def main(args):
    if args.engine == 'autosklearn':
        run_autosklearn(args)
    elif args.engine == 'h2o':
        run_h2o(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file')
    parser.add_argument('--engine', default='autosklearn')
    args = parser.parse_args()
    main(args)


