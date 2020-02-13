#!/usr/bin/env python
# coding: utf-8

# # Matplotlib Annotations

# In[1]:


import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as colors
import math
import numpy as np


# In[2]:


fig, ax = plt.subplots(1, 1, figsize=(8,7))
ax.plot(np.array([0, 1, 3]),
        np.array([0, 2, 1]), 'o',
        markersize=10, markeredgewidth=2,
        markerfacecolor='gray', markeredgecolor='blue')
ax.annotate('Vector',
            xy=(0,0),          # end point (without text)
            xytext=(1.5,1.0),  # end point (with text annotation)
            arrowprops=dict(arrowstyle='<|-', color='blue',
                            relpos=(0.5,0), # lower, center of text box
                            patchA=None,
                            shrinkA=0.0, shrinkB=0.0),
            ha='center',       # horizontal alignment for annotation
            fontsize=18)

circle = plt.Circle((3, 2), 0.5, color='#00007f', alpha=0.5, clip_on=True)
ax.add_artist(circle)
ax.grid()


# In[3]:


def plot_colornames():
    fig, ax = plt.subplots(1, 1, figsize=(8,10))
    
    n = len(colors.cnames)
    col_height = n // 4 if (n % 4 == 0) else n // 4 + 1
    fn = lambda i: (i // col_height, i % col_height)

    for i, c in enumerate(colors.cnames):
        xy = fn(i)
        ax.add_patch(patches.Rectangle(xy, 1, 1, color=c))
        ax.annotate(c, xy=xy)
        ax.set_xlim(0, 4)
        ax.set_ylim(0, col_height if (n % 4==0) else col_height+1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title('Matplotlib colors.cnames')

plot_colornames()

