#!/usr/bin/env python

import sys
import queue
import threading
import typing

from alive_progress import alive_bar
import click
import numpy as np
import pandas as pd
import websocket

# websocket portion
def receiver(ws: websocket.WebSocket, q: queue.Queue, qdone: queue.Queue):
    """Receive websocket messages and swallow pings and other session info
    placing the input lines in a queue for the main thread."""
    while True:
        for line in ws.recv().splitlines():
            if not isinstance(line, str):
                line = str(line, 'utf-8')
            if line.startswith("<Alarm"):
                raise Exception("Alarm! received from host.")
            if line.startswith("PING:") or \
                  line.startswith("CURRENT_ID:") or \
                  line.startswith("ACTIVE_ID:") or \
                  line.startswith("<Run|MPos") or \
                  line.startswith("<Idle|MPos"):
                if not qdone.empty():
                    return
                continue
            else:
                #print(line)
                q.put(line)
            if not qdone.empty():
                return

def ws_send_and_get(ws: websocket.WebSocket, q: queue.Queue, send: str, \
        data: queue.Queue, log: typing.TextIO, gcode: typing.TextIO, \
        expect: str="ok") -> str:
    """This is the main send and get result function that compares against
    an expected 'ok' style result. Any lines not matching the expected 
    result are assumed to be current or previous (pending in queue) probe
    responses from fluidnc.  They are added to a queue to be dequeued when
    probing is complete for later parsing. To make it easier to track
    what is happening, the unexpected responses are also written to a log
    file passed in.
    """
    ws.send(send);
    gcode.write(send+'\n')
    gcode.flush()
    while True:
        resp = q.get()
        if resp.startswith(expect):
            #print(f"expected response to {send} : {resp}")
            break
        #print(f"unexpected response to {send} : {resp}")
        data.put(resp)
        log.write(resp + '\n')
        log.flush() # force write for logging purposes
    return resp

@click.command()
@click.option('--lim', nargs=2, type=int, default=(200, 240), \
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
@click.option('--safe_height', type=int, default=15, \
        help='Safe height after meshing')
@click.option('--uri', type=str, default='ws://qtdraw.local:81', \
        help='Output websocket to use for gcode input and output')
@click.option('--output_filename', type=str, default='qtdraw_mesh.tsv')
@click.option('--log_filename', type=str, default='qtdraw_mesh.log')
@click.option('--gcode_filename', type=str, default='qtdraw_mesh.gcode')
@click.option('--probe_x_offset', type=int, default=26)
@click.option('--probe_y_offset', type=int, default=26)
def qt_mesh(lim, div, \
        feed, seek, probe_depth, travel_height, safe_height, \
        output_filename, log_filename, gcode_filename, uri, \
        probe_x_offset, probe_y_offset):
    """Generate G-code for fluidnc and parse the output to build
    a height map of the bed by communicating over a websocket and
    parsing the responses for probe messages."""

    ws = websocket.WebSocket()
    ws.connect(uri)
    q = queue.Queue()
    qdone = queue.Queue()
    data = queue.Queue()
    t = threading.Thread(target=receiver, args=(ws,q,qdone))
    t.start()

    xv = np.linspace(0, lim[0], div[0])
    yv = np.linspace(0, lim[1], div[1])

    print(f"generating {div[0] * div[1]} points on a grid from ({xv[0]},{yv[0]}) to ({xv[-1]},{yv[-1]})")

    with alive_bar(len(xv) * len(yv)) as bar, \
            open(log_filename, 'w') as log, \
            open(gcode_filename, 'w') as gcode:
        # preamble
        ws_send_and_get(ws, q, f"G90 G21 G17\n", data, log, gcode)
        fine_seek = seek / 2
        # travel to safe height
        ws_send_and_get(ws, q, f"G0 Z{safe_height} F{seek}\n", data, log, gcode)


        def ws_send_xy(x, y):
            ws_send_and_get(ws, q, f"G1 X{x:0.4f} Y{y:0.4f} F{feed}\n", data, log, gcode)
            ws_send_and_get(ws, q, f"G38.2 Z{probe_depth} F{fine_seek}\n", data, log, gcode)
            ws_send_and_get(ws, q, f"G0 Z2 F{seek}\n", data, log, gcode)
            bar()

        # traverse the matrix but zig zag
        for i, x in enumerate(xv):
            if i % 2 == 0:
                for y in yv:
                    ws_send_xy(x, y)
            else:
                for y in reversed(yv):
                    ws_send_xy(x, y)

        ws_send_and_get(ws, q, f"G0 Z{safe_height} F{seek}\n", data, log, gcode)
        

    # signal to the thread to quit, it will see this at the 
    # next ping from fluidnc
    qdone.put(True);

    print(f"parsing mesh data")
    mesh_data = []
    while not data.empty():
        line = data.get()
        line = line.strip()
        #print(line)
        if not line.startswith("[PRB:"):
            raise ValueError(f"unable to find probe prefix '[PRB:' at start of data: {line}")
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
    print(f"writing mesh x,y,z data to '{output_filename} after correcting for probe offset ({probe_x_offset}, {probe_y_offset})")
    df["x"] = df["x"] + probe_x_offset
    df["y"] = df["y"] + probe_y_offset
    df.to_csv(output_filename, sep='\t', header=True, index=False)

    # do this absolutely last because the qdone put won't trigger a
    # the receiver thread to leave until it gets a ping message so
    # this waits as long as possible from the put
    t.join()

if __name__ == '__main__':
    qt_mesh()
