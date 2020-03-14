#!/usr/bin/env python
# coding: utf-8

# # Hyperparameter Optimization
# 
# ## 1. Introduction
# 
# This is a demonstration for hyperparameter optimization
# with a comparison with the results from scipy.optimize.minimize
# 
# 
# ### 1.1 Setup
# 
# Dependencies
# 
# ```bash
# pip install hyperopt
# ```

# In[1]:


import hyperopt
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from hyperopt import fmin, hp, rand, tpe
from hyperopt.pyll.stochastic import sample
from mpl_toolkits.mplot3d import Axes3D
from scipy.optimize import minimize

get_ipython().run_line_magic('matplotlib', 'inline')


# ### 1.2 Generate Data

# In[2]:


X_MINIMUM, X_MAXIMUM = -np.pi, np.pi
Y_MINIMUM, Y_MAXIMUM = -np.pi, np.pi

search_space = {
    'x': hyperopt.hp.uniform('x', X_MINIMUM, X_MAXIMUM),
    'y': hyperopt.hp.uniform('y', Y_MINIMUM, Y_MAXIMUM)
}

def my_fn(params):
    # Function to optimize, for use by hyperopt
    x = params['x']
    y = params['y']
    return 0.1*(x**2 + y**2) + np.cos(x) * np.sin(0.4*y)

def my_fn2(params):
    # Function to optimize, for use by scipy.optimize.minimize
    x, y = params
    return 0.1*(x**2 + y**2) + np.cos(x) * np.sin(0.4*y)

def generate_data(my_fn, n=100):
    x = np.linspace(X_MINIMUM, X_MAXIMUM, n)
    y = np.linspace(Y_MINIMUM, Y_MAXIMUM, n)
    X, Y = np.meshgrid(x, y)
    Z = my_fn({'x': X, 'y': Y})
    return X, Y, Z


# ## 2. Optimization
# 
# ### 2.1 Define optimization subroutine

# In[3]:


def optimize(my_fn, search_space, algo=hyperopt.tpe.suggest, max_evals=100, seed=12345):
    trials = hyperopt.Trials()
    result = hyperopt.fmin(
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

def result2df(r):
    # losses = pd.DataFrame(r['trials'].losses(), columns=['loss'])
    losses = pd.DataFrame(r['trials'].results)
    xy = pd.DataFrame(r['trials'].idxs_vals[1])
    return pd.concat((xy, losses), axis=1)


# ### 2.2 Optimize
# 
# #### 2.2.1 Using Scipy.optimize

# In[4]:


r = minimize(my_fn2, [2.0, -2.0])
print(r)
if r.success:
    x = r.x
    print(f'\nResult: f(x,y) = f({x[0]}, {x[1]}) = {r.fun}')
else:
    print('Optimization failed')


# #### 2.2.2 Using Hyperopt

# In[5]:


X, Y, Z = generate_data(my_fn)
r = optimize(my_fn, search_space)
df = result2df(r)
result = r['result']
print(f"\nResult: f(x,y) = f({result['x']}, {result['y']}) = {df['loss'].min()}")


# In[6]:


idx = df['loss'].idxmin()
optimum = df.loc[idx, :]


# In[7]:


df.head()


# In[8]:


best = df.sort_values('loss', ascending=True)
best.head()


# ### 2.3 Plot Data
# 
# #### 2.3.1 Scatter Plot

# In[9]:


fig, ax = plt.subplots(1, 1, figsize=(9,7))
df.plot.scatter('x', 'y', c='loss', marker='o', s=50, colormap='spring', alpha=0.5, ax=ax)
best.head(1).plot.scatter('x', 'y', color='blue', marker='x', s=180, ax=ax, label='hyperopt')
ax.plot([x[0]], [x[1]], 'x', color='black', markersize=12, markeredgewidth=2, label='scipy.optimize')
ax.legend(frameon=False);


# #### 2.3.2 3D Plot

# In[10]:


def plot_data(X, Y, Z, opt):
    fig = plt.figure(figsize=(8,7))
    ax = fig.gca(projection='3d')
    surf = ax.plot_surface(
        X, Y, Z, rstride=5, cstride=5, cmap=matplotlib.cm.coolwarm,
        linewidth=0.3, antialiased=True, alpha=0.9)
    
    ax.plot([opt['x']], [opt['y']], [opt['loss']], 'x',
            markerfacecolor='black', markeredgecolor='black',
            markersize=12, markeredgewidth=5)

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.view_init(elev=40, azim=60)
    
plot_data(X, Y, Z, optimum)


# #### 2.3.3 Contour Plot

# In[11]:


def plot_data_contour(X, Y, Z, opt):
    fig, ax = plt.subplots(1, 1, figsize=(8,7))
    CS = ax.contour(X, Y, Z, 20)
    ax.plot([opt['x']], [opt['y']], 'x',
            markerfacecolor='black', markeredgecolor='black',
            markersize=12, markeredgewidth=3)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    
plot_data_contour(X, Y, Z, optimum)


# ### 2.4 Show Sampling
# 
# Actual sampling during hyperparameter optimization

# In[12]:


df[['x', 'y']].plot.hist(bins=20, edgecolor='black', alpha=0.5, stacked=False);


# Default sampling

# In[13]:


samples = pd.DataFrame(
    [ sample(search_space) for i in range(100) ]
)
samples.plot.hist(bins=20, edgecolor='black', alpha=0.5, stacked=False);

