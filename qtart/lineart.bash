#!/bin/bash

dim=16cm
tol=1mm
tol=0.1mm
tol=0.4mm
minlen=0.5mm
minlen=1mm

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <input svg>"
  exit 1
fi

insvg="$1"
outpre=`echo $insvg | sed "s/.svg//g"`
outsvg=`echo $insvg | sed "s/.svg/.out.svg/g"`

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

echo splitting by layer
vpype read $outsvg \
    forlayer write "${outpre}.layer_%_name or _lid%.svg" end

echo gcode rendering
#for file in `ls ${outpre}.layer_*.svg`
for file in ${outpre}.layer_*.svg
do
    echo $file
    outgcode=`echo $file | sed "s/.svg/.gcode/g"`
    vpype --config ../qtdraw.toml \
        read $file \
        gwrite -p qtdraw $outgcode
done
