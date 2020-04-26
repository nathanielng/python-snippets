# Plotting

## 1. Background

This folder contains code for data visualization using libraries such as
`matplotlib`, `seaborn`, `bokeh` (for plotting with hover tools), and
`drawille` (for ASCII plots).

The file `azure_plots.py` is for use with Azure Machine Learning Studio
projects. Azure automatically creates a visualization if
custom code is added to a project, and that code generates a .png file.

## 2. Matplotlib Snippets

### 2.1 Color Maps

```python
import matplotlib.pyplot as plt

clr_maps = plt.colormaps()
print(sorted(clr_maps))

cmap = plt.get_cmap("tab10")
df.plot(..., color=cmap(i), ...)
```

### 2.2 Annotation

[`matplotlib.axes.Axes.annotate`](https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.annotate.html)`(self, s, xy, *args, **kwargs)`

**Important Options**

- `xycoords='data'`: default option
- `xycoords='figure fraction'`: the (0,0)-(1,1) range corresponds to the *lower left* to the *upper right* of the figure
- `xycoords='axes fraction'`: the (0,0)-(1,1) range corresponds to the *lower left* to the *upper right* of the axes

- `horizontalalignment='left|center|right'`
- `verticalalignment='top|center|bottom'`
