#!/bin/bash

dim=16cm
tol=1mm
tol=0.4mm
tol=0.1mm
minlen=1mm
minlen=0.5mm

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <input svg>"
  exit 1
fi

insvg="$1"
outsvg=`echo $insvg | sed "s/.svg/.out.svg/g"`
outgcode=`echo $insvg | sed "s/.svg/.gcode/g"`

echo line plotting
vpype read $insvg \
    scaleto $dim $dim \
    splitall \
    linemerge --tolerance $tol \
    linesort \
    reloop \
    linesimplify \
    filter --min-length $minlen \
    write --center --page-size ${dim}x$dim $outsvg

echo gcode rendering
vpype --config qtdraw.toml \
    read $outsvg \
    gwrite -p qtdraw $outgcode
