import math
import sys

import numpy as np
import vsketch


class LogoSketch(vsketch.SketchClass):
    # Sketch parameters:
    colors = vsketch.Param(value=3, min_value=1, max_value=64, step=1, decimals=0)
    # arcs
    arc_span = vsketch.Param(value=270., min_value=0, max_value=360., step=5., decimals=.1)
    arc_sub_arcs = vsketch.Param(value=42, min_value=0, max_value=1024,)
    arc_sub_arc_noise = vsketch.Param(value=5, min_value=0, max_value=10.0)
    arc_branches = vsketch.Param(value=9, min_value=0, max_value=1024, step=1, decimals=0)
    # trees
    tree_noise_seed = vsketch.Param(value=42, decimals=0)
    tree_length = vsketch.Param(value=1, min_value=0, max_value=10, step=.01, decimals=2)
    tree_min_length = vsketch.Param(value=.5, min_value=0, max_value=10, step=.01, decimals=3)
    tree_decrease = vsketch.Param(value=.6, min_value=0, max_value=1, step=.05, decimals=2)
    tree_angle = vsketch.Param(value=8, min_value=0, max_value=360, step=5, decimals=0)
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
        vsk.translate(ctr_x, ctr_x);

        # arcs
        # setup
        arc_sep = (SIZE/1.) / self.arc_sub_arcs
        if arc_sep < self.arc_sep_cutoff:
            raise ValueError("distance between arcs is less than {arc_sep_cutoff}")
        print(f"separation between arcs is {arc_sep}")
        def noise_int(n: int, r: int):
            return np.floor(vsk.noise(np.linspace(0, n/2, n))*(r+1)).astype(int)
        arc_col_prlns = noise_int(int(self.arc_span), self.colors)
        vsk.noiseSeed(int(vsk.random(0,42)))
        arc_len_prlns = vsk.noise(np.linspace(0, 1., self.arc_sub_arcs))
        vsk.noiseSeed(int(vsk.random(0,42)))
        arc_sep_prlns = vsk.noise(np.linspace(0, .1, self.arc_sub_arcs))
        vsk.noiseSeed(int(vsk.random(0,42)))
        arc_brnch_prlns = noise_int(self.arc_sub_arcs, self.arc_branches)
        #print(arc_brnch_prlns)
        def sample_start_stops(prlns: np.ndarray, scale: np.ndarray):
            """returns a list of tuples with on and off indexes always incrementing"""
            #print(prlns)
            on = False
            start_stops = []
            for idx, sample in enumerate(prlns):
                if vsk.random(0, sample) <= sample * scale[idx]:
                    if not on:
                        on = True
                        start = idx
                        color = arc_col_prlns[idx]
                elif on:
                        on = False
                        end = idx
                        start_stops.append((float(start), float(end), int(color)))
            return start_stops
        vsk.noiseSeed(int(vsk.random(0,42)))
        arc_breaks_prlns = vsk.noise(np.linspace(0, 1., int(self.arc_span)))
        arc_breaks = sample_start_stops(arc_breaks_prlns, arc_breaks_prlns)
        print(arc_breaks)
        # draw
        for idx, a in enumerate(range(self.arc_sub_arcs)):
            arc_frac = (idx + 0.5)/len(range(self.arc_sub_arcs))
            arc_rand_end = arc_len_prlns[idx] * self.arc_span
            #print(arc_rand_end)
            arc_rand_radius = (idx + 0.5) * arc_sep# + arc_sep_prlns[idx]
            #print(arc_rand_radius)
            # not used yet, but this will be the layer
            stop = False
            for brks in range(len(arc_breaks)):
                arc_start, arc_end, color = arc_breaks[brks]
                #print(f"arc {idx} = {arc_start}, {arc_end}")
                if -arc_rand_end > -arc_start:
                    break
                if -arc_rand_end > -arc_end:
                    arc_end = arc_rand_end
                    stop = True
                    #print(f"arc {idx} end cond = {arc_start}, {arc_end}")

                vsk.stroke(color+1)
                vsk.arc(0, 0, \
                    arc_rand_radius, arc_rand_radius, \
                    -arc_end, -arc_start, True, \
                    "no", "center")
                if stop:
                    break

        # now the fractal trees
        # setup
        vsk.noiseSeed(self.tree_noise_seed)
        # colors
        cplns = noise_int(sys.getrecursionlimit(), self.colors)
        # length
        vsk.noiseSeed(self.tree_noise_seed+1)
        lplns = vsk.noise(np.linspace(0, 2., self.arc_sub_arcs)) * 2
        # min length
        vsk.noiseSeed(self.tree_noise_seed+2)
        mlplns = vsk.noise(np.linspace(0, 1., self.arc_sub_arcs))
        # decreases
        vsk.noiseSeed(self.tree_noise_seed+3)
        dplns = vsk.noise(np.linspace(0, 1., self.arc_sub_arcs)) + .3
        # angle
        vsk.noiseSeed(self.tree_noise_seed+4)
        aplns = noise_int(self.arc_sub_arcs, 5) * 2
        def grow(length, min_length, decrease, angle, color, noise=0):
            #print(f"len = {length}  min_len = {min_length}  decrease = {decrease} ({length*decrease})  angle = {angle}")
            if length < min_length:
                return
            vsk.stroke(cplns[color]+1)
            with vsk.pushMatrix():
                vsk.line(0, 0, 0, -length);
                vsk.translate(0, -length);

                new_length = length * decrease
                new_angle = angle * 1/decrease
                new_color = color + 1

                with vsk.pushMatrix():
                    vsk.rotate(+angle, degrees=True)
                    grow(new_length, min_length, decrease, new_angle, new_color, noise)

                with vsk.pushMatrix():
                    vsk.rotate(-angle, degrees=True)
                    grow(new_length, min_length, decrease, new_angle, new_color, noise)
        # draw
        for idx, a in enumerate(range(self.arc_sub_arcs)):
            arc_frac = (idx + 0.5)/len(range(self.arc_sub_arcs))
            arc_rand_radius = (idx + 0.5) * arc_sep# + arc_sep_prlns[idx]
            with vsk.pushMatrix():
                vsk.translate(arc_rand_radius/2, 0)
                #grow(self.tree_length, self.tree_min_length, self.tree_decrease, self.tree_angle)
                vsk.stroke(cplns[0]+1)
                grow(lplns[idx], mlplns[idx], dplns[idx], aplns[idx], 1, noise=0)


    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")



if __name__ == "__main__":
    LogoSketch.save("/tmp/logo.svg")
    LogoSketch.display()
