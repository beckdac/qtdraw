#!/bin/bash
./qtdraw_remap_gcode.py --input_gcode_filename ../map/landuse.gcode --output_gcode_filename ../map/landuse.remapped.gcode
./qtdraw_remap_gcode.py --input_gcode_filename ../map/natural.gcode --output_gcode_filename ../map/natural.remapped.gcode
./qtdraw_remap_gcode.py --input_gcode_filename ../map/railway.gcode --output_gcode_filename ../map/railway.remapped.gcode
./qtdraw_remap_gcode.py --input_gcode_filename ../map/way.gcode --output_gcode_filename ../map/way.remapped.gcode
./qtdraw_remap_gcode.py --input_gcode_filename ../map/building.gcode --output_gcode_filename ../map/building.remapped.gcode
