gcode: building.gcode landuse.gcode natural.gcode railway.gcode way.gcode 

%.gcode: %.svg lineart.bash
	./lineart.bash $<

all: $(gcode)

clean:
	rm $(gcode)
