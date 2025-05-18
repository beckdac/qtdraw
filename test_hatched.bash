#!/bin/bash

echo hatching
vpype hatched \
    -p 3 \
    civicsi.png \
    write --center civicsi.hatched.svg

echo line plotting
vpype read civicsi.hatched.svg \
    scaleto 200px 200px \
    splitall \
    linemerge --tolerance 0.1mm \
    linesort \
    reloop \
    linesimplify \
    filter --min-length 0.5mm \
    write --page-size 220x240 --center civicsi.hatched.out.svg

echo gcode rendering
vpype --config qtdraw.toml \
    read civicsi.hatched.out.svg \
    gwrite -p qtdraw civicsi.hatched.gcode
