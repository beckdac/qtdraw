I had to use the following on WSL w/ 20.04
```
export QT_QPA_PLATFORM="xcb"
```

```
pip install -e "git+https://github.com/AndyEveritt/GcodeParser.git@master#egg=gcodeparser"
```

Example output:
![Example bed mesh measurement png output](https://github.com/beckdac/qtdraw/blob/main/mesh/qtdraw_mesh.png?raw=true)
![Example bed mesh measurement repeatability png output](https://github.com/beckdac/qtdraw/blob/main/mesh/qtdraw_mesh_diff.png?raw=true)

Workflow
```
# generate mesh with qtdraw at default uri
./qtdraw_mesh.py --lim 200 200 --div 10 10 --feed 1000
# visualize mesh
./qtdraw_mesh_plot.py
# perhaps compare with previous mesh
./qtdraw_mesh_diff.py
./qtdraw_mesh_plot.py --input_filename qtdraw_mesh.previous.tsv
# remap an input gcode file
./qtdraw_remap_gcode.py --input_filename input.gcode --output_filename output.gcode
```
