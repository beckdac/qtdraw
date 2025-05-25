#!/usr/bin/env python

import math

import click
import gcodeparser
import pandas as pd
import numpy as np
import scipy

def mesh_read(input_filename: str) -> pd.DataFrame:
    df = pd.read_csv(input_filename, sep='\t', usecols=('x','y','z'))
    print(f"found a mesh in '{input_filename}' of size {df.size} with {df.shape[0]} rows and {df.shape[1]} cols")
    return df


@click.command()
@click.option('--output_gcode_filename', type=str, default='input.qtdraw_remapped.gcode')
@click.option('--input_gcode_filename', type=str, default='input.gcode')
@click.option('--input_mesh_filename', type=str, default='qtdraw_mesh.tsv')
@click.option('--remap_x_offset', type=float, default=30, help='an offset applied to the x coords')
@click.option('--remap_y_offset', type=float, default=30, help='an offset applied to the y coords')
@click.option('--machine_x_offset', type=float, default=0, help='an offset applied to the mesh x coords')
@click.option('--machine_y_offset', type=float, default=0, help='an offset applied to the mesh y coords')
def qtdraw_remap_gcode(output_gcode_filename: str, input_gcode_filename: str, \
        input_mesh_filename: str, \
        remap_x_offset: float, remap_y_offset: float, \
        machine_x_offset: float, machine_y_offset: float):
    """Read two mesh files and output a new mesh file with the difference of A - B."""
    mesh = mesh_read(input_mesh_filename)
    mesh = mesh.sort_values(by=['y', 'x'])
    mesh['x'] = mesh['x'] + machine_x_offset
    mesh['y'] = mesh['y'] + machine_y_offset
    print(f"read {mesh.size} elements from mesh in {mesh.shape} from '{input_mesh_filename}")

    # process the mesh into a meshgrid for sampling for gcode remapping
    xv = mesh['x'].unique()
    yv = mesh['y'].unique()
    shape = (len(xv), len(yv))
    x = mesh['x'].to_numpy().reshape(shape)
    y = mesh['y'].to_numpy().reshape(shape)
    z = mesh['z'].to_numpy().reshape(shape)
    z = z - z[0][0];
    #print(x)
    #print(y)
    #print(z)

    gcode_in = ""
    with open(input_gcode_filename, 'r') as input:
        gcode_in += input.read()

    gcode = gcodeparser.GcodeParser(gcode_in, include_comments=True)
    print(f"read {len(gcode.lines)} lines of gcode from '{input_gcode_filename}'")
    #print(xv)
    #print(yv)
    remap_func = scipy.interpolate.RegularGridInterpolator((xv, yv), z)
    last_X = None
    last_Y = None
    for line in gcode.lines:
        X = line.get_param('X')
        if X is not None:
            line.update_param('X', round(X+remap_x_offset, 3))
            last_X = X+remap_x_offset
        Y = line.get_param('Y')
        if Y is not None:
            line.update_param('Y', round(Y+remap_y_offset, 3))
            last_Y = Y+remap_y_offset
        Z = line.get_param('Z')
        if Z is not None:
            if last_X is not None and last_Y is not None:
                #print(f"{([last_X], [last_Y])}")
                Z_adjust = remap_func(([last_X, last_Y]))
                line.update_param('Z', round(Z+float(Z_adjust[0]),3))
    
    print(f"saving modified lines to '{output_gcode_filename}")
    with open(output_gcode_filename, 'w') as output:
        for line in gcode.lines:
            output.write(line.gcode_str + '\n')

if __name__ == '__main__':
    qtdraw_remap_gcode()
