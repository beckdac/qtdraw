import math

import numpy as np
import vsketch


class LogoSketch(vsketch.SketchClass):
    # Sketch parameters:
    arc_span = vsketch.Param(value=270., min_value=0, max_value=360., step=5., decimals=.1)
    arc_sub_arcs = vsketch.Param(value=42, min_value=0, max_value=1024,)
    arc_sub_arc_noise = vsketch.Param(value=5, min_value=0, max_value=10.0)
    arc_colors = vsketch.Param(value=8, min_value=1, max_value=64, step=1, decimals=0)
    arc_branches = vsketch.Param(value=9, min_value=0, max_value=1024, step=1, decimals=0)
    # constraints
    arc_sep_cutoff = vsketch.Param(value=.1, min_value=0, max_value=1, step=.05, decimals=2, unit="mm")

    def draw(self, vsk: vsketch.Vsketch) -> None:
        # size
        SIZE=16
        vsk.size(f"{SIZE}cmx{SIZE}cm", landscape=False)
        vsk.scale("cm")
        # graphics
        vsk.noFill()
        vsk.penWidth("0.5mm")

        ctr_x = SIZE/2.
        ctr_y = SIZE/2.
        # arcs
        # setup
        arc_sep = (SIZE/1.) / self.arc_sub_arcs
        if arc_sep < self.arc_sep_cutoff:
            raise ValueError("distance between arcs is less than {arc_sep_cutoff}")
        print(f"separation between arcs is {arc_sep}")
        def noise_int(n: int, r: int):
            return np.floor(vsk.noise(np.linspace(0, 1., n))*(r+1)).astype(int)
        arc_col_prlns = noise_int(self.arc_sub_arcs, self.arc_colors)
        arc_len_prlns = vsk.noise(np.linspace(0, 1., self.arc_sub_arcs))
        arc_sep_prlns = vsk.noise(np.linspace(0, .1, self.arc_sub_arcs))
        arc_brnch_prlns = noise_int(self.arc_sub_arcs, self.arc_branches)
        #print(arc_brnch_prlns)
        def sample_start_stops(prlns: np.ndarray):
            """returns a list of tuples with on and off indexes always incrementing"""
            #print(prlns)
            on = False
            start_stops = []
            for idx, sample in enumerate(prlns):
                if vsk.randomGaussian() <= sample:
                    if not on:
                        on = True
                        start = idx
                elif on:
                        on = False
                        end = idx
                        start_stops.append((start, end))
            return start_stops
        arc_breaks_prlns = vsk.noise(np.linspace(0, 1., int(self.arc_span)))
        arc_breaks = sample_start_stops(arc_breaks_prlns)
        # draw
        for idx, a in enumerate(range(self.arc_sub_arcs)):
            arc_frac = (idx + 0.5)/len(range(self.arc_sub_arcs))
            #print(arc_frac)
            # add the abs gaussian to prevent a 0 length arc
            #arc_rand_end = (self.arc_span * arc_frac * vsk.random(0, 1)) + math.fabs(vsk.random(0, 1)+0.01)
            #arc_rand_end = (self.arc_span * arc_frac * vsk.random(arc_frac/arc_frac/2, arc_frac)) + math.fabs(vsk.random(0, 1)+0.01)
            arc_rand_end = arc_len_prlns[idx] * self.arc_span
            #print(arc_rand_end)
            arc_rand_radius = (idx + 0.5) * arc_sep# + arc_sep_prlns[idx]
            #print(arc_rand_radius)
            # not used yet, but this will be the layer
            arc_rand_col = int(vsk.random(1, self.arc_colors + 1))
            vsk.stroke(arc_rand_col)
            #print(arc_rand_col)
            stop = False
            for brks in range(len(arc_breaks)):
                arc_start, arc_end = arc_breaks[brks]
                print(f"arc = {arc_start}, {arc_end}")
                if -arc_rand_end > -arc_end:
                    arc_end = arc_rand_end
                    stop = True
                    print(f"arc end cond = {arc_start}, {arc_end}")

                vsk.arc(ctr_x, ctr_y, \
                    arc_rand_radius, arc_rand_radius, \
                    -arc_end, -arc_start, True, \
                    "no", "center")
                if stop:
                    break

        # now the fractal trees
        # setup

        # draw


    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    LogoSketch.display()
    #LogoSketch.save("logo.svg")
