#!/usr/bin/env python

import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt

from bokeh.io import output_file
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure, show


def polar_plot(x, y, i, outfile):
    ax = plt.subplot(111, projection='polar')
    ax.plot(x, y)
    ax.plot([x[i]], [y[i]], 'bo')
    ax.set_rticks([-1, -.5, 0, .5, 1, 1.5])
    ax.grid(True)
    plt.savefig(outfile, transparent=True, bbox_inches='tight')
    plt.close()


def generate_sample_data():
    x = np.linspace(0, 2, 41)
    y = np.sin(2 * x * np.pi)
    df = pd.DataFrame({
        'x': x,
        'y': y
    })
    df['filename'] = 'images/img' + df.index.astype(str) + '.svg'
    return df


def generate_hovertool_images(df):
    x = df['x']
    y = df['y']
    theta = x * np.pi
    for row in df.iterrows():
        data = row[1]
        polar_plot(theta, y, row[0], data['filename'])
        print(data['filename'])


TOOLTIPS = f"""
    <div style="background-color: rgba(0, 0, 0, 0.05);">
        <table style="background-color: rgba(0, 0, 0, 0.05);">
        <tr>
            <td>
                <img src="@filename"
                    height="300" alt="@filename" width="300"
                    style="float: left; margin: 0px 15px 15px 0px; background: transparent";
                    border="1">
                </img>
            </td>
            <td>
            <span style="font-size: 12px; font-weight: bold;">x</span> = @x<br>
            <span style="font-size: 12px; font-weight: bold;">y</span> = @y<br>
            </td>
        </table>
    </div>
    """


def plot_scatter_hovertool(df_cds, tool_tips, outfile='plot.html'):
    output_file(outfile)
    fig = figure()
    fig.circle(x='x', y='y', source=df_cds)
    hover = HoverTool(tooltips=tool_tips)
    fig.add_tools(hover)
    show(fig)


def main():
    if not os.path.isdir('images'):
        os.mkdir('images')
    df = generate_sample_data()
    generate_hovertool_images(df)
    plot_scatter_hovertool(ColumnDataSource(df), TOOLTIPS)


if __name__ == "__main__":
    main()
