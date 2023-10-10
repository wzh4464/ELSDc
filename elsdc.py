from ctypes import POINTER, Structure, c_double, c_int, CDLL, byref
import time
from typing import List
import numpy as np
import cv2
import os


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
        p_set.output_img, shape=(p_set.h, p_set.w)).copy()
    p_set.release_memory()
    return ell_arr, poly_arr, output_img


def _detect_primitives(img: np.ndarray) -> "PrimitveSet":
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype("float64")
    h, w = img_gray.shape
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


if __name__ == "__main__":
    import sys
    import matplotlib.pyplot as plt
    img = cv2.imread(sys.argv[1])
    start = time.monotonic()
    ellipses, polygons, out_img = detect_primitives(img)
    print("Detection took {}s".format(time.monotonic() - start))
    plt.imshow(out_img)
    plt.savefig("out_plot.png")

    # show ellipses
    for ell in ellipses:
        # print as: ell_label x1 y1 x2 y2 ax bx theta ang_start ang_end
        cx = ell.cx
        cy = ell.cy
        ax = ell.ax
        bx = ell.bx
        theta = ell.theta
        cv2.ellipse(img, (int(cx), int(cy)), (int(ax), int(bx)), theta, 0, 360, (255, 0, 0), 2)
    cv2.imwrite("out_ell.png", img)
