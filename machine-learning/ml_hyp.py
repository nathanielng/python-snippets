#!/usr/bin/env python

import hyperopt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def function_to_minimize(params):
    x = params['x']
    y = params['y']
    return np.sin(x)*np.cos(y)


class Hyperopt():

    def __init__(self, fn, space,
                 algo=hyperopt.tpe.suggest,
                 seed=12345,
                 n_trials=100):
        self._fn = fn
        self._space = space
        self._algo = algo
        self._trials = hyperopt.Trials()
        self._max_evals = n_trials
        self._rstate = np.random.RandomState(seed)
        self._result = None


    def optimize(self):
        self._result = hyperopt.fmin(
            fn=self._fn,
            space=self._space,
            algo=self._algo,
            trials=self._trials,
            max_evals=self._max_evals,
            rstate=self._rstate
        )
        df_x = pd.DataFrame(self._trials.idxs_vals[1])
        loss = pd.DataFrame(self._trials.results)
        self._df_r = pd.concat((df_x, loss), axis=1)

        return {
            'result': self._result,
            'trials': self._trials
        }


    def results(self, sort=True):
        if sort is True:
            return self._df_r.sort_values('loss', ascending=True)
        else:
            return self._df_r


    def best(self):
        idxmin = df['loss'].idxmin()
        return df.loc[idxmin, :]


if __name__ == "__main__":
    space = {
        'x': hyperopt.hp.uniform('x', -2*np.pi, 2*np.pi),
        'y': hyperopt.hp.uniform('y', -2*np.pi, 2*np.pi)
    }
    H = Hyperopt(function_to_minimize, space)
    result = H.optimize()

    print(f"Result = {result['result']}")
    df = H.results()
    print(df.head())
    print()
    best = H.best()

    print('---- Best Result ----')
    for idx, data in best.iteritems():
        print(f'{idx}: {data}')
