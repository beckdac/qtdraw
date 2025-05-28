from collections import defaultdict
import math
import sys

import numpy as np
import vsketch


# function to check if point q lies on line segment 'pr'
def onSegment(p, q, r):
    return (q[0] <= max(p[0], r[0]) and q[0] >= min(p[0], r[0]) and
            q[1] <= max(p[1], r[1]) and q[1] >= min(p[1], r[1]))

# function to find orientation of ordered triplet (p, q, r)
# 0 --> p, q and r are collinear
# 1 --> Clockwise
# 2 --> Counterclockwise
def orientation(p, q, r):
    val = (q[1] - p[1]) * (r[0] - q[0]) - \
          (q[0] - p[0]) * (r[1] - q[1])

    # collinear
    if val == 0:
        return 0

    # clock or counterclock wise
    # 1 for clockwise, 2 for counterclockwise
    return 1 if val > 0 else 2


# function to check if two line segments intersect
def intersect(points):
    # find the four orientations needed
    # for general and special cases
    o1 = orientation(points[0][0], points[0][1], points[1][0])
    o2 = orientation(points[0][0], points[0][1], points[1][1])
    o3 = orientation(points[1][0], points[1][1], points[0][0])
    o4 = orientation(points[1][0], points[1][1], points[0][1])

    # general case
    if o1 != o2 and o3 != o4:
        return True

    # special cases
    # p1, q1 and p2 are collinear and p2 lies on segment p1q1
    if o1 == 0 and onSegment(points[0][0], points[1][0], points[0][1]):
        return True

    # p1, q1 and q2 are collinear and q2 lies on segment p1q1
    if o2 == 0 and onSegment(points[0][0], points[1][1], points[0][1]):
        return True

    # p2, q2 and p1 are collinear and p1 lies on segment p2q2
    if o3 == 0 and onSegment(points[1][0], points[0][0], points[1][1]):
        return True

    # p2, q2 and q1 are collinear and q1 lies on segment p2q2 
    if o4 == 0 and onSegment(points[1][0], points[0][1], points[1][1]):
        return True

    return False

def xy_next(xy: (float, float), length: float, angle: float) -> (float, float):
    x, y = xy
    rad = math.radians(angle)
    x_next = x + length * math.cos(rad)
    y_next = y + length * math.sin(rad)
    return (x_next, y_next)


def search(xy: (float, float), parent_xy: (float, float), last_angle: float, depth: int, vsk: vsketch.Vsketch, self):
    global lines
    #print(f"search called with {xy}, {last_angle}, and {color}")
    if (depth == sys.getrecursionlimit() - 100):
    #if (depth == 100):
        return 
    noise = vsk.noise(x=xy[0], y=xy[1])
    # interesting below how the noise is handles will determine left and right
    tmp_angle = self.angle_range_min_degrees + ((self.angle_range_max_degrees - self.angle_range_min_degrees) * noise)
    if vsk.randomGaussian() > 0.5:
        tmp_angle *= -1
    angle = last_angle + tmp_angle
    distance = self.distance_range_min + (self.distance_range_max - self.distance_range_min) * noise
    new_xy = xy_next(xy, distance, angle)
    new_line = (xy, new_xy)
    #print(f"A {depth} looking for lines intersecting: {new_line}", flush=True)
    a_failed=False
    if len(lines) > 4:
        skip = 2 # last one
    else:
        skip = 1 # 0
    for line in lines[:-skip]:
        if line[0] == parent_xy or line[1] == parent_xy:
            continue
        if intersect(((new_line[0], new_line[1]), (line[0], line[1]))):
            a_failed=True
            break
    vsk.strokeWeight(int(depth * self.strokeWeight_scale) + 1)
    if not a_failed:
        vsk.line(xy[0], xy[1], new_xy[0], new_xy[1])
        lines.append((new_line))
        search(new_xy, xy, angle, depth+1, vsk, self)
        skip += 1
    # negative angle
    angle = last_angle - tmp_angle
    distance = self.distance_range_min + (self.distance_range_max - self.distance_range_min) * noise
    new_xy = xy_next(xy, distance, angle)
    new_line = (xy, new_xy)
    #print(f"B {depth} looking for lines intersecting: {new_line}", flush=True)
    b_failed=False
    for line in lines[:-skip]:
        if line[0] == parent_xy or line[1] == parent_xy:
            continue
        if intersect(((new_line[0], new_line[1]), (line[0], line[1]))):
            b_failed=True
            break
    if b_failed:
        return
    vsk.strokeWeight(int(depth * self.strokeWeight_scale) + 1)
    vsk.line(xy[0], xy[1], new_xy[0], new_xy[1])
    lines.append((new_line))
    search(new_xy, xy, angle, depth+1, vsk, self)


lines = []

class LogoSketch(vsketch.SketchClass):
    # Sketch parameters:
    colors = vsketch.Param(value=8, min_value=1, max_value=64, step=1, decimals=0)
    size_mm = vsketch.Param(value=160, min_value=10, max_value=1000, step=1, decimals=0)
    stroke_width = vsketch.Param(value=1, min_value=1, max_value=10, step=1, decimals=0)
    angle_range_min_degrees = vsketch.Param(value=15, min_value=1, max_value=180, step=1, decimals=1)
    angle_range_max_degrees = vsketch.Param(value=45, min_value=2, max_value=359, step=1, decimals=1)
    distance_range_min = vsketch.Param(value=2, min_value=1, max_value=100, step=.5, decimals=1)
    distance_range_max = vsketch.Param(value=10, min_value=2, max_value=100, step=.5, decimals=1)
    searches = vsketch.Param(value=512, min_value=1, max_value=10000, step=1, decimals=0)
    strokeWeight_scale = vsketch.Param(value=.1, min_value=0, max_value=10, step=.01, decimals=2)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        # size
        vsk.size(f"{self.size_mm}mmx{self.size_mm}", landscape=False)
        vsk.scale("mm")
        # graphics
        vsk.noFill()
        vsk.penWidth("0.5mm")

        if self.stroke_width != 1:
            vsk.strokeWeight(self.stroke_width)

        x_ctr = self.size_mm/2.
        y_ctr = self.size_mm/2.
        x_min = 5.
        x_max = self.size_mm-x_min
        y_min = 5.
        y_max = self.size_mm-y_min
        vsk.translate(x_ctr, y_ctr)


        # arcs
        # setup
        def noise_int(n: int, r: int):
            return np.floor(vsk.noise(np.linspace(0, n/2, n))*(r+1)).astype(int)
        cplns = noise_int(sys.getrecursionlimit(), self.colors)
        #cplns = noise_int(self.searches, self.colors)

        #print(intersect((((0, 0), (1, 0)), ((.5, -5), (.5,.5)))))
        #print(intersect((((0, 0), (0, 0.1)), ((.5, -5), (.5,.5)))))

        global lines
        lines = [((x_min,y_min), (x_min,y_max)),((x_min,y_max), (x_max,y_max)),((x_max,y_max), (x_max,y_min)),((x_max,y_min), (x_min,y_min))]
        lines += lines; # this allows the 0:-2 below to work at the expense of four extra comparisons every line

        xy = (x_ctr, y_ctr)
        for srch in range(self.searches):
            noise = vsk.noise(x=xy[0], y=xy[1])
            angle = 360 * noise
            search(xy, xy, angle, 0, vsk, self)
            vsk.stroke((self.colors * noise) + 1)
            xy = (vsk.random(x_min, x_max), vsk.random(y_min, y_max))


    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")



if __name__ == "__main__":
    LogoSketch.save("/tmp/logo.svg")
    LogoSketch.display()
