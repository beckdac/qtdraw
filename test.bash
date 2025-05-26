#!/bin/bash

dim=15cm

echo line plotting
vpype read civicsi.svg \
    scaleto $dim $dim \
    splitall \
    linemerge --tolerance 0.1mm \
    linesort \
    reloop \
    linesimplify \
    filter --min-length 0.5mm \
    write --center --page-size ${dim}x${dim} civicsi.out.svg

echo gcode rendering
vpype --config qtdraw.toml \
    read civicsi.out.svg \
    gwrite -p qtdraw civicsi.gcode
