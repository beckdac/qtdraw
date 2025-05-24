#!/usr/bin/env python

import math

import click
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import matplotlib.pyplot as plt

def mesh_read(input_filename: str) -> pd.DataFrame:
    df = pd.read_csv(input_filename, sep='\t', usecols=('x','y','z'))
    print(f"found a mesh in '{input_filename}' of size {df.size} with {df.shape[0]} rows and {df.shape[1]} cols")
    return df


@click.command()
@click.option('--output_filename', type=str, default='qtdraw_mesh.png')
@click.option('--input_filename', type=str, default='qtdraw_mesh.tsv')
def qtdraw_mesh_plot(output_filename: str, input_filename: str):
    mesh = mesh_read(input_filename)
    mesh = mesh.sort_values(by=['y', 'x'])
    print(mesh)

    xv = mesh['x'].unique()
    yv = mesh['y'].unique()
    shape = (len(xv), len(yv))
    x = mesh['x'].to_numpy().reshape(shape)
    y = mesh['y'].to_numpy().reshape(shape)
    z = mesh['z'].to_numpy().reshape(shape)

    fig = plt.figure(figsize=plt.figaspect(0.5))

    ax = fig.add_subplot(1, 2, 1, projection='3d')
    surf = ax.plot_surface(x, y, z, \
        cmap=cm.jet, linewidth=1, rstride=1, cstride=1)
    ax.set_zlim(z.min()-2, z.max()+2)
    ax.zaxis.set_major_locator(LinearLocator(11))
    ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
    plt.xlabel("X")
    plt.ylabel("Y")
    ax.invert_xaxis()
    fig.colorbar(surf, shrink=0.3, aspect=5, pad=0.18)

    ax = fig.add_subplot(1, 2, 2, projection='3d')
    surf = ax.plot_surface(x, y, z, \
        cmap=cm.jet, linewidth=1, rstride=1, cstride=1)
    ax.zaxis.set_major_locator(LinearLocator(11))
    ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
    plt.xlabel("X")
    plt.ylabel("Y")
    ax.invert_xaxis()
    fig.colorbar(surf, shrink=0.3, aspect=5, pad=0.18)

    print(f"saving to '{output_filename}'")
    plt.savefig(output_filename)
    plt.show()

if __name__ == '__main__':
    qtdraw_mesh_plot()
