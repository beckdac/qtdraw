#!/bin/bash

dim=16cm
tol=0.1mm
tol=1.5mm
tol=1.0mm
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
    splitall \
    linemerge --tolerance $tol \
    linesort \
    reloop \
    linesimplify \
    deduplicate -t $tol\
    filter --min-length $minlen \
    write --page-size ${dim}x$dim $outsvg

echo splitting by layer
#vpype read $outsvg \
#    forlayer write "${outpre}.layer_%_name or _lid%.svg" end

echo gcode rendering
#for file in `ls ${outpre}.layer_*.svg`
#for file in ${outpre}.layer_*.svg
for file in ${outsvg}
do
    outgcode=`echo $file | sed "s/.svg/.gcode/g"`
    echo $file $outgcode
    vpype --config ../qtdraw.toml \
        read $file \
        gwrite -p qtdraw $outgcode
done
