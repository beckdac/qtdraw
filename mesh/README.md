I had to use the following on WSL w/ 20.04
```
export QT_QPA_PLATFORM="xcb"
```

```
pip install -e "git+https://github.com/AndyEveritt/GcodeParser.git@master#egg=gcodeparser"
```

Example output from a bed mesh probing run:
![Example bed mesh measurement png output](https://github.com/beckdac/qtdraw/blob/main/mesh/qtdraw_mesh.png?raw=true)

Comparing the repeatabilty of the bed mesh probe by comparing identical subsequent runs:
![Example bed mesh measurement repeatability png output](https://github.com/beckdac/qtdraw/blob/main/mesh/qtdraw_mesh.diff.png?raw=true)

*Workflow*
```
# generate mesh with qtdraw at default uri
./qtdraw_mesh.py
# visualize mesh
./qtdraw_mesh_plot.py
# perhaps compare with previous mesh
./qtdraw_mesh_diff.py
./qtdraw_mesh_plot.py --input_filename qtdraw_mesh.previous.tsv
# remap an input gcode file
./qtdraw_remap_gcode.py --input_gcode_filename ../civicsi.gcode --output_gcode_filename civicsi.qtdraw_remapped.gcode --machine_x_offset -29 --machine_y_offset -29
```
