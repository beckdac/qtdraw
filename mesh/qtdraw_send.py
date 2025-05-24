#!/usr/bin/env python

import sys
import threading

import websocket

ws = websocket.WebSocket()
ws.connect('ws://qtdraw.local:81')

# Reception needs to be done in a separate thread; you cannot
# assume that a given command will always result in exactly one
# response at a predictable time
def receiver():
    while True:
        for line in ws.recv().splitlines():
            if not isinstance(line, str):
                line = str(line, 'utf-8')
            if line.startswith("PING:") or \
                  line.startswith("CURRENT_ID:") or \
                  line.startswith("ACTIVE_ID:"):
                continue
            else:
                print(line)

def sender():
    #from testing
    #ws.send('?')  # realtime characters need no line terminator
    #ws.send('$/axes/x\n')  # line-oriented commands need \n at the end
    for line in sys.stdin:
        ws.send(line)


t = threading.Thread(target=receiver)
t.start()


if __name__ == '__main__':
    sender()
