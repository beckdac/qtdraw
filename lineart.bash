#!/bin/bash

dim=7cm

echo line plotting
vpype read lineart.svg \
    scaleto $dim $dim \
    splitall \
    linemerge --tolerance 0.1mm \
    linesort \
    reloop \
    linesimplify \
    filter --min-length 0.5mm \
    write --center --page-size ${dim}x$dim lineart.out.svg

echo gcode rendering
vpype --config qtdraw.toml \
    read lineart.out.svg \
    gwrite -p qtdraw lineart.gcode
