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
    """
    Represents a ring shape defined by its center, axes, angles, and label.

    Members:
        - center (Tuple[int, int]): Center of the ring.
        - axes (Tuple[int, int]): Major and minor axes of the ring.
        - angle (float): Angle of rotation of the ring.
        - startAngle (float): Starting angle of the ring.
        - endAngle (float): Ending angle of the ring.
        - full (int): Flag indicating if the ring is full or partial.
        - label (int): Label associated with the ring.
        
    Methods:
        draw(img: np.ndarray) -> None: Draw the ring on the image.
        
    Dependencies:
        - numpy
        - cv2
        - math
    """

    def __init__(self, x1: float, y1: float, x2: float, y2: float, 
                 width: float, cx: float, cy: float, theta: float, ax: float, bx: float,
                 ang_start: float, ang_end: float, wmin: float, wmax: float, full: int,
                 label: int):
        self.center = (int(cx), int(cy))
        self.axes = (int(ax), int(bx))
        self.angle = theta * 180 / math.pi
        self.startAngle = ang_start * 180 / math.pi
        self.endAngle = ang_end * 180 / math.pi
        self.full = full
        self.label = label

    def draw(self, img):
        color = (0, 255, 0)  # Green color for ellipses and arcs
        thickness = 2  # Thickness of the ellipse edge
        if self.full:
            cv2.ellipse(img, self.center, self.axes, self.angle, 0, 360, color, thickness)
        else:
            cv2.ellipse(img, self.center, self.axes, self.angle, self.startAngle, self.endAngle, color, thickness)

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
    output_img = np.ctypeslib.as_array(
        p_set.output_img, shape=(int(p_set.h.value), int(p_set.w.value))).copy()
    p_set.release_memory()
    return ell_arr, poly_arr, output_img

def _detect_primitives(img: np.ndarray) -> "PrimitveSet":
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype("float64")
    h, w = img_gray.shape
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
    def __init__(self, ell_arr: POINTER(_Ring), ell_label_arr: POINTER(c_int), # type: ignore
        ell_count: int, poly_arr: POINTER(_Polygon),  # type: ignore
        poly_label_arr: POINTER(c_int), poly_count: int,  # type: ignore
        output_img: POINTER(c_int), w: int, h: int # type: ignore
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

def draw_ellipses_and_arcs(img, ellipses: List[Ring]):
    for ell in ellipses:
        ell.draw(img)

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
    
    # Draw ellipses and arcs on the image
    draw_ellipses_and_arcs(img, ellipses)
    
    cv2.imwrite("out_ell_py.png", img)
