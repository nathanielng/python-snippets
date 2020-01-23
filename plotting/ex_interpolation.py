#!/usr/bin/env python
# coding: utf-8

# # Interpolation
# 
# ## 1. Libraries

# In[1]:


import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d, lagrange


# ## 2. Calculations
# 
# ### 2.1 Original data

# In[2]:


# Original data points
x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
y = np.array([0.1, 1.2, 3.0, 4.2, 3.8])

# Extra data points for drawing the curves
x1 = np.linspace(-0.9, 6.7, 50)
x2 = np.linspace(x.min(), x.max(), 50)


# ### 2.2 Calculate interpolating functions

# In[3]:


lg = lagrange(x, y)
linear = interp1d(x, y, kind='linear')
spline0 = interp1d(x, y, kind='zero')
spline1 = interp1d(x, y, kind='slinear')
spline2 = interp1d(x, y, kind='quadratic')
spline3 = interp1d(x, y, kind='cubic')


# ## 3. Plots

# In[4]:


fig, (ax0, ax1) = plt.subplots(2, 1, figsize=(7,13))
ax0.plot(x, y, 'bo')
ax0.plot(x1, lg(x1), label='Lagrange')
ax0.plot(x2, linear(x2), label='linear')
ax0.legend(loc='best', frameon=False)

ax1.plot(x, y, 'bo')
ax1.plot(x2, lg(x2), label='Lagrange', color='black')
ax1.plot(x2, spline0(x2), label='spline (0th order)', color='red')
ax1.plot(x2, spline1(x2), label='spline (1st order)', color='orange')
ax1.plot(x2, spline2(x2), label='spline (2nd order)', color='green')
ax1.plot(x2, spline3(x2), label='spline (3rd order)', color='blue')
ax1.legend(loc='best', frameon=False);

