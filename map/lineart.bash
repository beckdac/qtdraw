#!/bin/bash

dim=15cm
tol=0.1mm
tol=1mm
minlen=0.5mm
minlen=1mm

outsvg=`echo $1 | sed "s/.svg/.out.svg/g"`
outgcode=`echo $1 | sed "s/.svg/.gcode/g"`

echo line plotting
vpype read $1 \
    splitall \
    linemerge --tolerance $tol \
    linesort \
    reloop \
    linesimplify \
    filter --min-length $minlen \
    write --page-size ${dim}x$dim $outsvg

echo gcode rendering
vpype --config ../qtdraw.toml \
    read $outsvg \
    gwrite -p qtdraw $outgcode
