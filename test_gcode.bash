#!/bin/bash

echo gcode rendering
vpype --config qtdraw.toml \
    read civicsi.out.svg \
    gwrite -p qtdraw civicsi.gcode
