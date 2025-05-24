#!/usr/bin/env python

import click
import numpy as np
import pandas as pd

@click.option('--lim', nargs=2, type=int, default=(400, 400), \
        help='Size limit of the work area in mm')
@click.option('--div', nargs=2, type=int, default=(6, 6), \
        help='Samples per axis')
@click.option('--feed', type=int, default=500, \
        help='Feed rate in x and y')
@click.option('--seek', type=int, default=100, \
        help='Seek rate in z')
@click.option('--probe_depth', type=int, default=-1, \
        help='Max probe depth from 0')
@click.option('--travel_height', type=int, default=2, \
        help='Travel height for Z from sample to sample')
@click.option('--safe_height', type=int, default=0, \
        help='Safe height after meshing')
@click.option('--output_filename', type=str, default='qtdraw_mesh.gcode', \
        help='Filename to use for the gcode output')
def qt_mesh(lim: tuple[int,int]=[400,400], div: tuple[int, int]=(6,6), \
        feed: int=500, seek: int=100, \
        probe_depth: int=-1, travel_height: int=2, \
        safe_height: int=25, \
        output_filename: str='qtdraw_mesh.gcode'):
    """Generate G-code for fluidnc and parse the output to build
    a height map of the bed"""
    xv = np.linspace(0, lim[0], div[0])
    yv = np.linspace(0, lim[1], div[1])

    print(f"generating {div[0] * div[1]} points on a grid from ({xv[0]},{yv[0]}) to ({xv[1]},{yv[1]})")

    with(open(output_filename, 'w') as file):
        # preamble
        file.write(f"G90 G21 G17\n")
        fine_seek = seek / 2
        # fine touch off routine
        # travel to safe height
        file.write(f"G0 Z{safe_height}\n")
        # go to the middle to use as a reference
        file.write(f"G1 X{lim[0]/2} Y{lim[1]/2} F{feed}\n")
        # go to search start
        file.write(f"G0 Z{travel_height}\n")
        # probe
        file.write(f"G38.2 Z{probe_depth} F{seek}\n")
        # set the work 0
        file.write(f"G92 Z0\n")
        # go to travel_height
        file.write(f"G0 Z{travel_height}\n")
        # probe at a slower speed
        file.write(f"G38.2 Z{probe_depth} F{fine_seek}\n")
        file.write(f"G92 Z0\n")
        file.write(f"G0 Z{travel_height}\n")
    
        for x in xv:
            for y in yv:
                file.write(f"G1 X{x} Y{y} F{feed}\n")
                file.write(f"G38.2 Z{probe_depth} F{seek}\n")
                file.write(f"G0 Z2\n")
        file.write(f"G0 Z{safe_height}\n")


if __name__ == '__main__':
    qt_mesh()
