#!/usr/bin/env python

import glob
import os
import pandas as pd
import pickle

from sklearn import linear_model, svm
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor


models = {
    'dtr': DecisionTreeRegressor(),
    'linear': linear_model.LinearRegression(),
    'logistic': linear_model.LogisticRegression(),
    'knr': KNeighborsRegressor(),
    'svr': svm.SVR(),
    'gbr': GradientBoostingRegressor(),
    'rf': RandomForestRegressor(n_estimators=100, criterion='mse')
}


def load_model(index=0):
    pickle_file = glob.glob('*.pickle')[index]
    print(f'Loading: {pickle_file}')

    with open(pickle_file, 'rb') as f:
        obj = pickle.load(f)

    return obj


def predict(obj, X_test):
    y_pred = obj.predict(X_test)
    return y_pred


if __name__ == "__main__":
    obj = load_model()
