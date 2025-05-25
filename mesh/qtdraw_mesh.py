#!/usr/bin/env python

import enum
import sys
import threading
import typing

import click
import numpy as np
import pandas as pd

class WorkMode(enum.Enum):
    gcode = enum.auto()
    parse = enum.auto()

@click.command()
@click.option('--work-mode', default=WorkMode.gcode, \
              type=click.Choice(WorkMode, case_sensitive=False),
              help='Choose tool function from list')
@click.option('--lim', nargs=2, type=int, default=(200, 240), \
        help='Size limit of the work area in mm')
@click.option('--div', nargs=2, type=int, default=(10, 11), \
        help='Samples per axis')
@click.option('--feed', type=int, default=1000, \
        help='Feed rate in x and y')
@click.option('--seek', type=int, default=100, \
        help='Seek rate in z')
@click.option('--probe_depth', type=int, default=-2, \
        help='Max probe depth from 0')
@click.option('--travel_height', type=int, default=2, \
        help='Travel height for Z from sample to sample')
@click.option('--safe_height', type=int, default=15, \
        help='Safe height after meshing')
@click.option('--output_mesh_filename', type=str, default='qtdraw_mesh.tsv')
@click.option('--input_log_filename', type=str, default='qtdraw_mesh.log')
@click.option('--output_gcode_filename', type=str, default='qtdraw_mesh.gcode')
@click.option('--probe_x_offset', type=int, default=22)
@click.option('--probe_y_offset', type=int, default=27)
#@click.option('', type=int, default=)
def qt_mesh(lim, div, \
        feed, seek, probe_depth, travel_height, safe_height, \
        output_mesh_filename, input_log_filename, output_gcode_filename, \
        probe_x_offset, probe_y_offset, work_mode: WorkMode):
    """Do one of several different tasks related to mapping a bed
    and remapping G-code (gcode, GCODE, whatever) in the Z axis.

    gcode mode:
    Generate G-code for fluidnc. Should work with a lot of grbl.

    parse:
    Parse the output to a mesh file from std in or a file. Assumes
    global position in PRB as the custom from fluidnc. Outputs a 
    table that can be used for down stream operations or in spread
    sheet stuff or whatever.

    remap:
    Take a map from a tsv and a gcode file and remap the z axis
    onto the bed mesh using a very simple approach that only uses
    lines. NO ARCS.  Yet, but that is a goal.
    """

    if (work_mode == WorkMode.gcode):
        xv = np.linspace(0, lim[0], div[0])
        yv = np.linspace(0, lim[1], div[1])

        print(f"generating {div[0] * div[1]} points on a grid from ({xv[0]},{yv[0]}) to ({xv[-1]},{yv[-1]}) and saving to '{output_gcode_filename}'")

        with open(output_gcode_filename, 'w') as gcode:
            # preamble
            # we do this in machine coordinates
            gcode.write(f"G90 G21 G17\n")
            fine_seek = seek / 2
            # travel to safe height
            gcode.write(f"G0 Z{safe_height} F{seek}\n")


            def write_probe_at_xy(x, y):
                gcode.write(f"G1 X{x:0.4f} Y{y:0.4f} F{feed}\n")
                gcode.write(f"G38.2 Z{probe_depth} F{fine_seek}\n")
                gcode.write(f"G0 Z2 F{seek}\n")

            # traverse the matrix but zig zag
            for i, x in enumerate(xv):
                if i % 2 == 0:
                    for y in yv:
                        write_probe_at_xy(x, y)
                else:
                    for y in reversed(yv):
                        write_probe_at_xy(x, y)

            gcode.write(f"G0 Z{safe_height} F{seek}\n")
    elif (work_mode == WorkMode.parse):
        print(f"parsing mesh data from log in '{input_log_filename}'")
        mesh_data = []
        with open(input_log_filename, 'r') as log:
          for line in log.readlines():
            line = line.strip()
            #print(line)
            if not line.startswith("[PRB:"):
                #raise ValueError(f"unable to find probe prefix '[PRB:' at start of data: {line}")
                print(f"ignoring line that doesn't look like a PRB line: {line}")
            colon_fields = line.split(":")
            if len(colon_fields) != 3:
                raise ValueError(f"expected 3 fields in probe data after split on ':', found {len(colon_fields)}, in data: {line}")
            xyz = colon_fields[1].split(",")
            if len(xyz) != 3:
                raise ValueError(f"expected 3 fields (x, y, z) in second : split field when splitting on ',', found {len(xyz)} in data: {line}")
            if colon_fields[2] != "1]":
                raise ValueError(f"expected to find true (1) value at probe success field in data, found: {colon_fields[2]} in data: {line}")
            #print(f"x = {xyz[0]}, y = {xyz[1]}, z = {xyz[2]}")
            mesh_data.append(xyz)

        df = pd.DataFrame(mesh_data, columns=("x", "y", "z"), dtype=float)
        print(f"writing mesh x,y,z data to '{output_mesh_filename}")
        df["x"] = df["x"] + probe_x_offset
        df["y"] = df["y"] + probe_y_offset
        df.to_csv(output_mesh_filename, sep='\t', header=True, index=False)


if __name__ == '__main__':
    qt_mesh()
