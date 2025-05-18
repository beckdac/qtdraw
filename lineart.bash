#!/bin/bash

echo line plotting
vpype read lineart.svg \
    scaleto 200px 200px \
    splitall \
    linemerge --tolerance 0.1mm \
    linesort \
    reloop \
    linesimplify \
    filter --min-length 0.5mm \
    write --center --page-size 220x240 lineart.out.svg

echo gcode rendering
vpype --config qtdraw.toml \
    read lineart.out.svg \
    gwrite -p qtdraw lineart.gcode
