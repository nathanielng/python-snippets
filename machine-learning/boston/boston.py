#!/usr/bin/env python
# coding: utf-8

# # Boston

# In[1]:


from sklearn.datasets import load_boston
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import PolynomialFeatures


# In[2]:


boston = load_boston()
rows, cols = boston.data.shape
print(f'Boston dataset: {rows} rows, {cols} cols')
X_train, X_test, Y_train, Y_test = train_test_split(
    boston.data, boston.target, test_size=0.2)


# In[3]:


lr = LinearRegression(normalize=True)
# lr.fit(X_train, Y_train)
print(f'Linear regression: {cross_val_score(lr, X_train, Y_train, cv=7).mean()}')
rg = Ridge(0.001, normalize=True)
print(f'Ridge regression: {cross_val_score(rg, X_train, Y_train, cv=7).mean()}')
ls = Lasso(0.001, normalize=True)
print(f'Lasso score: {cross_val_score(ls, X_train, Y_train, cv=7).mean()}')
# Polynomial features
lr_pf = LinearRegression(normalize=True)
pf = PolynomialFeatures(degree=2)
Xp = pf.fit_transform(X_train)
lr_pf.fit(Xp, Y_train)
print(f'Linear regression (polynomial features): {cross_val_score(lr_pf, X_train, Y_train, cv=7).mean()}')

