import matplotlib.pyplot as plt
import numpy as np

from mpl_toolkits.mplot3d import Axes3D


def make_wireframe(limits):
    x_min, x_max, y_min, y_max, z_min, z_max = limits
    if x_min == x_max:
        z = np.arange(z_min, z_max+1)
        y = np.arange(y_min, y_max+1)
        Y, Z = np.meshgrid(y, z)
        X = x_min + 0*Y
    elif y_min == y_max:
        x = np.arange(x_min, x_max+1)
        z = np.arange(z_min, z_max+1)
        X, Z = np.meshgrid(x, z)
        Y = y_min + 0*X
    elif z_min == z_max:
        x = np.arange(x_min, x_max+1)
        y = np.arange(y_min, y_max+1)
        X, Y = np.meshgrid(x, y)
        Z = z_min + 0*X
    return X, Y, Z


def plot_wireframes(ax, wireframes, **kwds):
    for wireframe in wireframes:
        X, Y, Z = make_wireframe(wireframe['limits'])
        ax.plot_wireframe(
            X, Y, Z, color=wireframe['color'],
            rstride=stride, cstride=stride, **kwds)


def plot_cube(ax, wireframes_front, wireframes_top, wireframes_right):
    plot_wireframes(ax, wireframes_front, alpha=0.9)
    plot_wireframes(ax, wireframes_top, alpha=0.9)
    plot_wireframes(ax, wireframes_right, alpha=0.9)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')


def get_example_wireframes(x_min, x_max, y_min, y_max, z_min, z_max, y_h):
    y1 = y_min
    y2 = y_min + y_h
    y3 = y_max + y_h
    y4 = y_max + 2 * y_h
    wireframes_front = [
        {'color': 'r', 'limits': [x_min, x_max, y1, y2, z_min, z_min]},
        {'color': 'b', 'limits': [x_min, x_max, y2, y3, z_min, z_min]},
        {'color': 'r', 'limits': [x_min, x_max, y3, y4, z_min, z_min]}
    ]

    wireframes_top = [
        {'color': 'r', 'limits': [x_max, x_max, y1, y2, z_min, z_max]},
        {'color': 'b', 'limits': [x_max, x_max, y2, y3, z_min, z_max]},
        {'color': 'r', 'limits': [x_max, x_max, y3, y4, z_min, z_max]}
    ]

    wireframes_right = [
        {'color': 'r', 'limits': [x_min, x_max, y4, y4, z_min, z_max]}
    ]
    return wireframes_front, wireframes_top, wireframes_right


if __name__ == "__main__":
    wireframes_front, wireframes_top, wireframes_right = get_example_wireframes(
        x_min=0, x_max=100,
        y_min=0, y_max=200,
        z_min=0, z_max=100,
        y_h=20
    )
    stride=5
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(111, projection='3d')
    plot_cube(ax, wireframes_front, wireframes_top, wireframes_right)
    ax.view_init(155, 35)
    plt.savefig('wireframe.svg')
