#!/bin/bash

echo rendering text
vpype text --position 5 5 -f "cursive" "Amber Beck" \
    text --position 5 1cm -f "cursive" "is rad as F..k!" \
    write --center letter.svg

echo line plotting
vpype read letter.svg \
    scaleto 200px 200px \
    splitall \
    linemerge --tolerance 0.1mm \
    linesort \
    reloop \
    linesimplify \
    filter --min-length 0.5mm \
    write --center --page-size 220x240 letter.out.svg

echo gcode rendering
vpype --config qtdraw.toml \
    read letter.out.svg \
    gwrite -p qtdraw letter.gcode
