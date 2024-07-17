from ctypes import POINTER, Structure, c_double, c_int, CDLL, byref, c_size_t
import time
from typing import List
import numpy as np
import cv2
import os
import xml.etree.ElementTree as ET
import math

try:
    elsdc = CDLL(os.path.join(os.path.dirname(os.path.realpath(__file__)), "libelsdc.so"))
except OSError:
    os.system("make shared")
    elsdc = CDLL(os.path.join(os.path.dirname(os.path.realpath(__file__)), "libelsdc.so"))


class _Ring(Structure):
    _fields_ = [
        ("x1", c_double), ("y1", c_double), ("x2", c_double), ("y2", c_double),
        ("width", c_double), ("cx", c_double), ("cy", c_double),
        ("theta", c_double), ("ax", c_double), ("bx", c_double),
        ("ang_start", c_double), ("ang_end", c_double),
        ("wmin", c_double), ("wmax", c_double),
        ("full", c_int)
    ]

class _PointD(Structure):
    _fields_ = [
        ("x", c_double), ("y", c_double)
    ]

class _Polygon(Structure):
    _fields_ = [
        ("dim", c_int), ("pts", POINTER(_PointD))
    ]


class Ring:
    '''
    x1: float
    y1: float
    x2: float
    y2: float
    width: float
    cx: float
    cy: float
    theta: float
    ax: float
    bx: float
    ang_start: float
    ang_end: float
    wmin: float
    wmax: float
    full: int
    label: int
    '''
    def __init__(self, x1: float, y1: float, x2: float, y2: float, 
        width: float, cx: float, cy: float, theta: float, ax: float, bx: float,
        ang_start: float, ang_end: float, wmin: float, wmax: float, full: int,
        label: int
    ):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.width = width
        self.cx = cx
        self.cy = cy
        self.theta = theta
        self.ax = ax
        self.bx = bx
        self.ang_start = ang_start
        self.ang_end = ang_end
        self.wmin = wmin
        self.wmax = wmax
        self.full = full
        self.label = label


class Polygon:
    def __init__(self, dim: int, pts: np.ndarray, label: int):
        self.dim = dim
        self.pts = pts
        self.label = label


def detect_primitives(img: np.ndarray):
    p_set = _detect_primitives(img)
    ell_arr: List[Ring] = []
    poly_arr: List[Polygon] = []
    for i in range(p_set.ell_count):
        elt = p_set.ell_arr[i]
        ell_arr.append(Ring(
            elt.x1, elt.y1, elt.x2, elt.y2, elt.width, elt.cx, elt.cy,
            elt.theta, elt.ax, elt.bx, elt.ang_start, elt.ang_end,
            elt.wmin, elt.wmax, elt.full, p_set.ell_label_arr[i]
        ))
    # for i in range(p_set.poly_count):
    #     elt = p_set.poly_arr[i]
    #     num_pts = elt.dim // 2
    #     pts = np.empty((num_pts, 2))
    #     _pts = elt.pts
    #     for j in range(num_pts):
    #         pts[j, 0] = _pts[j].x
    #         pts[j, 1] = _pts[j].y
    #     poly_arr.append(Polygon(elt.dim, pts, p_set.poly_label_arr[i]))
    output_img = np.ctypeslib.as_array(
        p_set.output_img, shape=(int(p_set.h.value), int(p_set.w.value))).copy()
    p_set.release_memory()
    return ell_arr, poly_arr, output_img


def _detect_primitives(img: np.ndarray) -> "PrimitveSet":
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype("float64")
    h, w = img_gray.shape
    # 确保传递的类型是正确的
    h = c_size_t(h)
    w = c_size_t(w)
    ell_arr = POINTER(_Ring)()
    ell_label_arr = POINTER(c_int)()
    ell_count = c_int()
    poly_arr = POINTER(_Polygon)()
    poly_label_arr = POINTER(c_int)()
    poly_count = c_int()
    output_img = POINTER(c_int)()
    elsdc.detect_primitives(
        byref(ell_arr), byref(ell_label_arr), byref(ell_count),
        byref(poly_arr), byref(poly_label_arr), byref(poly_count),
        byref(output_img), img_gray.ctypes.data_as(POINTER(c_double)),
        w, h
    )
    return PrimitveSet(
        ell_arr, ell_label_arr, ell_count.value, poly_arr, 
        poly_label_arr, poly_count.value, output_img, w, h
    )


class PrimitveSet:
    def __init__(self, ell_arr: POINTER(_Ring), ell_label_arr: POINTER(c_int),
        ell_count: int, poly_arr: POINTER(_Polygon), 
        poly_label_arr: POINTER(c_int), poly_count: int, 
        output_img: POINTER(c_int), w: int, h: int
    ):
        self.ell_arr = ell_arr
        self.ell_label_arr = ell_label_arr
        self.ell_count = ell_count
        self.poly_arr = poly_arr
        self.poly_label_arr = poly_label_arr
        self.poly_count = poly_count
        self.output_img = output_img
        self.w = w
        self.h = h
        self._freed_memory = False

    def release_memory(self):
        if not self._freed_memory:
            elsdc.free_outputs(self.ell_arr, self.ell_label_arr, self.poly_arr, 
                self.poly_label_arr, self.poly_count, 
                self.output_img)
            self._freed_memory = True

    def __del__(self):
        self.release_memory()


def generate_svg(ellipses, polygons, output_file, width, height):
    svg = ET.Element('svg', xmlns="http://www.w3.org/2000/svg", width=str(width), height=str(height))
    
    for ellipse in ellipses:
        if ellipse.ax == ellipse.bx:
            ET.SubElement(svg, 'circle', cx=str(ellipse.cx), cy=str(ellipse.cy), 
                          r=str(ellipse.ax), stroke="blue", fill="none")
        else:
            ET.SubElement(svg, 'ellipse', cx=str(ellipse.cx), cy=str(ellipse.cy),
                          rx=str(ellipse.ax), ry=str(ellipse.bx), transform=f"rotate({ellipse.theta},{ellipse.cx},{ellipse.cy})",
                          stroke="blue", fill="none")
    
    for polygon in polygons:
        points_str = ' '.join([f"{x},{y}" for x, y in polygon.pts])
        ET.SubElement(svg, 'polygon', points=points_str, stroke="red", fill="none")
    
    tree = ET.ElementTree(svg)
    tree.write(output_file)
    
def generate_svg(ellipses, polygons, output_file, width, height):
    svg = ET.Element('svg', xmlns="http://www.w3.org/2000/svg", width=str(width), height=str(height))
    
    for ellipse in ellipses:
        if ellipse.ax == ellipse.bx:
            write_svg_circ_arc(svg, ellipse)
        else:
            write_svg_ell_arc(svg, ellipse)
    
    for polygon in polygons:
        points_str = ' '.join([f"{x},{y}" for x, y in polygon.pts])
        ET.SubElement(svg, 'polygon', points=points_str, stroke="red", fill="none")
    
    tree = ET.ElementTree(svg)
    tree.write(output_file)

def write_svg_circ_arc(svg, cring):
    fa = 0
    fs = 1
    
    ang_start = math.atan2(cring.y1 - cring.cy, cring.x1 - cring.cx)
    ang_end = math.atan2(cring.y2 - cring.cy, cring.x2 - cring.cx)
    
    C = 2 * math.pi * cring.ax
    if cring.full or (angle_diff(ang_start, ang_end) < 2 * math.pi * math.sqrt(2) / C and angle_diff_signed(ang_start, ang_end) > 0):
        ET.SubElement(svg, 'ellipse', cx=str(cring.cx), cy=str(cring.cy), rx=str(cring.ax), ry=str(cring.bx), stroke="red", fill="none", **{'stroke-width': "1"})
    else:
        x1 = cring.ax * math.cos(ang_start) + cring.cx
        y1 = cring.ax * math.sin(ang_start) + cring.cy
        x2 = cring.ax * math.cos(ang_end) + cring.cx
        y2 = cring.ax * math.sin(ang_end) + cring.cy
        if (x1 == x2 and y1 == y2) or dist(x1, y1, x2, y2) < 2.0:
            ET.SubElement(svg, 'ellipse', cx=str(cring.cx), cy=str(cring.cy), rx=str(cring.ax), ry=str(cring.bx), stroke="red", fill="none", **{'stroke-width': "1"})
        else:
            if ang_start < 0:
                ang_start += 2 * math.pi
            if ang_end < 0:
                ang_end += 2 * math.pi
            if ang_end < ang_start:
                ang_end += 2 * math.pi
            if ang_end - ang_start > math.pi:
                fa = 1
            d = f"M {x1},{y1} A {cring.ax},{cring.ax} 0 {fa},{fs} {x2},{y2}"
            ET.SubElement(svg, 'path', d=d, stroke="red", fill="none", **{'stroke-width': "1"})

def write_svg_ell_arc(svg, ering):
    fa = 0
    fs = 1
    
    if ering.full:
        ET.SubElement(svg, 'ellipse', transform=f"translate({ering.cx} {ering.cy}) rotate({ering.theta * 180 / math.pi})", rx=str(ering.ax), ry=str(ering.bx), stroke="red", fill="none", **{'stroke-width': "1"})
    else:
        x1, y1 = rosin_point(ering, ering.x1, ering.y1)
        x2, y2 = rosin_point(ering, ering.x2, ering.y2)
        if (x1 == x2 and y1 == y2) or dist(x1, y1, x2, y2) < 2.0:
            ET.SubElement(svg, 'ellipse', transform=f"translate({ering.cx} {ering.cy}) rotate({ering.theta * 180 / math.pi})", rx=str(ering.ax), ry=str(ering.bx), stroke="red", fill="none", **{'stroke-width': "1"})
        else:
            ang_start = math.atan2(y1 - ering.cy, x1 - ering.cx)
            ang_end = math.atan2(y2 - ering.cy, x2 - ering.cx)
            if ang_start < 0:
                ang_start += 2 * math.pi
            if ang_end < 0:
                ang_end += 2 * math.pi
            if ang_end < ang_start:
                ang_end += 2 * math.pi
            if ang_end - ang_start > math.pi:
                fa = 1
            d = f"M {x1},{y1} A {ering.ax},{ering.bx} {ering.theta * 180 / math.pi} {fa},{fs} {x2},{y2}"
            ET.SubElement(svg, 'path', d=d, stroke="red", fill="none", **{'stroke-width': "1"})

def angle_diff(ang1, ang2):
    return (ang2 - ang1) % (2 * math.pi)

def angle_diff_signed(ang1, ang2):
    return math.atan2(math.sin(ang2 - ang1), math.cos(ang2 - ang1))

def rosin_point(ering, x, y):
    cos_theta = math.cos(ering.theta)
    sin_theta = math.sin(ering.theta)
    x_new = ering.ax * cos_theta * x - ering.bx * sin_theta * y + ering.cx
    y_new = ering.ax * sin_theta * x + ering.bx * cos_theta * y + ering.cy
    return x_new, y_new

def dist(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def draw_ellipses_and_arcs(img, ellipses):
    for ell in ellipses:
        center = (int(ell.cx), int(ell.cy))
        axes = (int(ell.ax), int(ell.bx))
        angle = ell.theta * 180 / math.pi
        startAngle = ell.ang_start * 180 / math.pi
        endAngle = ell.ang_end * 180 / math.pi
        cv2.ellipse(img, center, axes, angle, startAngle, endAngle, (0, 255, 0), 2)

# Example usage in the main block
if __name__ == "__main__":
    import sys
    import matplotlib.pyplot as plt
    img = cv2.imread(sys.argv[1])
    start = time.monotonic()
    ellipses, polygons, out_img = detect_primitives(img)
    print(f"Detection took {time.monotonic() - start}s")
    
    plt.imshow(out_img)
    plt.savefig("out_plot_py.png")
    
    # Save ellipses and polygons to SVG
    generate_svg(ellipses, polygons, 'output_py.svg', img.shape[1], img.shape[0])

    # Draw ellipses and arcs on the image
    draw_ellipses_and_arcs(img, ellipses)
    
    cv2.imwrite("out_ell_py.png", img)
