#!/bin/bash

echo vector flow image conversion to lineart
vpype flow_img --min_sep .5 --max_sep 10 \
    --max_size 200 \
    --noise_coeff 0.001 \
    input.jpg \
    write lineart.svg

./lineart.bash
