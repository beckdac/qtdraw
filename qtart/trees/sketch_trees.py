import math
import sys

import numpy as np
import vsketch


class LogoSketch(vsketch.SketchClass):
    # Sketch parameters:
    colors = vsketch.Param(value=4, min_value=1, max_value=64, step=1, decimals=0)
    # trees
    trees = vsketch.Param(value=16, min_value=1, step=1, decimals=0)
    tree_noise_seed = vsketch.Param(value=42, decimals=0)
    tree_length = vsketch.Param(value=1, min_value=0, max_value=10, step=.01, decimals=2)
    tree_min_length = vsketch.Param(value=.5, min_value=0, max_value=10, step=.01, decimals=3)
    tree_decrease = vsketch.Param(value=.6, min_value=0, max_value=1, step=.05, decimals=2)
    tree_angle = vsketch.Param(value=8, min_value=0, max_value=360, step=5, decimals=0)

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
        #vsk.translate(ctr_x, ctr_x);
        vsk.translate(ctr_x, SIZE*.1);

        # arcs
        # setup
        tree_sep = (SIZE/1.) / self.trees
        print(f"separation between trees is {tree_sep}")
        def noise_int(n: int, r: int):
            return np.floor(vsk.noise(np.linspace(0, n/2, n))*(r+1)).astype(int)
        # draw
        # trees
        # setup
        vsk.noiseSeed(self.tree_noise_seed)
        # colors
        cplns = noise_int(sys.getrecursionlimit(), self.colors)
        # length
        vsk.noiseSeed(self.tree_noise_seed+1)
        lplns = vsk.noise(np.linspace(0, 2., self.trees)) * 1
        # min length
        vsk.noiseSeed(self.tree_noise_seed+2)
        mlplns = vsk.noise(np.linspace(0, 1., self.trees)) / 3
        # decreases
        vsk.noiseSeed(self.tree_noise_seed+3)
        dplns = vsk.noise(np.linspace(0, 1., self.trees)) + .3
        # angle
        vsk.noiseSeed(self.tree_noise_seed+4)
        aplns = noise_int(self.trees, 5) * 2
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
        x_base = 2;
        x_range = SIZE - x_base * 2;
        x_tree_sep = (x_range/1) / self.trees

        for idx, a in enumerate(range(self.trees)):
            tree_x = idx * x_tree_sep + x_base
            # + arc_sep_prlns[idx]
            with vsk.pushMatrix():
                vsk.translate(tree_x, 0)
                #grow(self.tree_length, self.tree_min_length, self.tree_decrease, self.tree_angle)
                vsk.stroke(cplns[0]+1)
                grow(lplns[idx], mlplns[idx], dplns[idx], aplns[idx], 1, noise=0)


    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")



if __name__ == "__main__":
    LogoSketch.save("/tmp/logo.svg")
    LogoSketch.display()
