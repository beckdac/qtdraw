#!/usr/bin/env python

import sys
import queue
import threading

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
            if line.startswith("PING:") or \
                  line.startswith("CURRENT_ID:") or \
                  line.startswith("ACTIVE_ID:") or \
                  line.startswith("<Run|Mpos"):
                continue
            else:
                #print(line)
                q.put(line)
            if not qdone.empty():
                return

def ws_send_and_get(ws: websocket.WebSocket, q: queue.Queue, send: str, data: queue.Queue, expect: str="ok") -> str:
    ws.send(send);
    while True:
        resp = q.get()
        if resp.startswith(expect):
            #print(f"expected response to {send} : {resp}")
            break
        print(f"unexpected response to {send} : {resp}")
        data.put(resp)
    return resp

@click.command()
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
@click.option('--safe_height', type=int, default=15, \
        help='Safe height after meshing')
@click.option('--uri', type=str, default='ws://qtdraw.local:81', \
        help='Output websocket to use for gcode input and output')
@click.option('--output_filename', type=str, default='qt_mesh.tsv')
def qt_mesh(lim, div, \
        feed, seek, probe_depth, travel_height, safe_height, \
        output_filename, uri):
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

    if True:
        # preamble
        ws_send_and_get(ws, q, f"G90 G21 G17\n", data)
        fine_seek = seek / 2
        # fine touch off routine
        # travel to safe height
        ws_send_and_get(ws, q, f"G0 Z{safe_height}\n", data)
        # go to the middle to use as a reference
        ws_send_and_get(ws, q, f"G1 X{lim[0]/2} Y{lim[1]/2} F{feed}\n", data)
        # go to search start
        ws_send_and_get(ws, q, f"G0 Z{travel_height} F{seek}\n", data)
        # probe
        ws_send_and_get(ws, q, f"G38.2 Z{probe_depth} F{seek}\n", data)
        # set the work 0
        ws_send_and_get(ws, q, f"G92 Z0\n", data)
        # go to travel_height
        ws_send_and_get(ws, q, f"G0 Z{travel_height} F{seek}\n", data)
        # probe at a slower speed
        ws_send_and_get(ws, q, f"G38.2 Z{probe_depth} F{fine_seek}\n", data)
        ws_send_and_get(ws, q, f"G92 Z0\n", data)
        ws_send_and_get(ws, q, f"G0 Z{travel_height} F{seek}\n", data)
    
        for x in xv:
            for y in yv:
                ws_send_and_get(ws, q, f"G1 X{x} Y{y} F{feed}\n", data)
                ws_send_and_get(ws, q, f"G38.2 Z{probe_depth} F{seek}\n", data)
                ws_send_and_get(ws, q, f"G0 Z2 F{seek}\n", data)

        ws_send_and_get(ws, q, f"G0 Z{safe_height} F{seek}\n", data)

        # signal to the thread to quit, it will see this at the 
        # next ping from fluidnc
        qdone.put(True);
        t.join()

        while not data.empty:
            line = data.get()
            print(line)

if __name__ == '__main__':
    qt_mesh()
