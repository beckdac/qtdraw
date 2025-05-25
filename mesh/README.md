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
# generate gcode to sample a mesh 
./qtdraw_mesh.py --work-mode gcode --output_gcode_filename qtdraw_mesh.gcode
# run the gcode on the qtdraw using the fluidnc and grab the log
# telnet to the device is a an easy way to get the log
# parse the mesh into a tsv from the fuildnc log, specifically PRB lines
./qtdraw_mesh.py --work-mode parse --input_log_filename qtdraw_mesh.log --output_mesh_filename qtdraw_mesh.tsv
# visualize mesh
./qtdraw_mesh_plot.py
# perhaps compare with previous mesh
./qtdraw_mesh_diff.py
./qtdraw_mesh_plot.py --input_filename qtdraw_mesh.previous.tsv
# remap an input gcode file
./qtdraw_remap_gcode.py --input_gcode_filename ../civicsi.gcode --output_gcode_filename civicsi.qtdraw_remapped.gcode 
curl -F upload=@civicsi.qtdraw_remapped.gcode http://qtdraw.local/upload
# center pen on x 22 and y 27 and lower it to touch the paper; zero z axis, run the remapped gcode
```
