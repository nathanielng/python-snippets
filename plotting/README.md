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

### 2.3 Plot backgrounds

Matplotlib plot with a background image. Figure size is adjusted based on the size
of the background image (note that the adjustment calculation does not take the
space for axis labels and ticks into account).

```python
def plot_background_image(background_image, output_image, extent, h_pad=0.2, w_pad=0.2):
    img = plt.imread(background_image)
    img_height, img_width, _ = img.shape
    dpi = plt.gcf().get_dpi()
    fig, ax = plt.subplots(1, 1, figsize=(img_width/dpi + w_pad, img_height/dpi + h_pad))
    ax.imshow(img, extent=extent, aspect='auto', alpha=0.7)
    ax.grid(True, ls=':', alpha=0.5)
    if output_image is not None:
        plt.savefig(output_image, bbox_inches='tight', h_pad=0.2, w_pad=0.2)

plot_background_image(img1, img2, extent=[-2.72, 8.39, 13.7, 1770])
```
