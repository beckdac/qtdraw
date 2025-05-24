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
@click.option('--output_filename', type=str, default='qtdraw_mesh.diff.png')
@click.option('--input_a_filename', type=str, default='qtdraw_mesh.tsv')
@click.option('--input_b_filename', type=str, default='qtdraw_mesh.previous.tsv')
def qtdraw_mesh_plot(output_filename: str, input_a_filename: str, input_b_filename: str):
    """Read two mesh files and output a new mesh file with the difference of A - B."""
    mesh_A = mesh_read(input_a_filename)
    mesh_A = mesh_A.sort_values(by=['y', 'x'])
    mesh_B = mesh_read(input_b_filename)
    mesh_B = mesh_B.sort_values(by=['y', 'x'])
    mesh = mesh_A.sub(mesh_B)
    if max(mesh['x'])-min(mesh['x']) > .001:
        raise ValueError("too much misalignment between x coordinates in meshes")
    if max(mesh['y'])-min(mesh['y']) > .001:
        raise ValueError("too much misalignment between y coordinates in meshes")
    # move over the actual x y coords
    mesh['x'] = mesh_A['x']
    mesh['y'] = mesh_A['y']
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

    plt.show()
    print(f"saving to '{output_filename}'")
    plt.savefig(output_filename)

if __name__ == '__main__':
    qtdraw_mesh_plot()
