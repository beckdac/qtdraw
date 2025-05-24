#!/usr/bin/env python

import sys
import threading

import websocket

ws = websocket.WebSocket()
ws.connect("ws://qtdraw.local:81")

# Reception needs to be done in a separate thread; you cannot
# assume that a given command will always result in exactly one
# response at a predictable time
def receiver():
    while True:
        for l in ws.recv().splitlines():
            if isinstance(l, str):
                print(l)
            else:
                print(str(l, 'utf-8'))

t = threading.Thread(target=receiver)
t.start()

def sender():
    ws.send("?")  # realtime characters need no line terminator
    ws.send("$/axes/x\n")  # line-oriented commands need \n at the end


if __name__ == '__main__':
    sender()
