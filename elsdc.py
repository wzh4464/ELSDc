from ctypes import POINTER, Structure, c_double, c_int, CDLL, byref
import time
import numpy as np
import cv2


elsdc = CDLL("./libelsdc.so")


class Ring(Structure):
    _fields_ = [
        ("x1", c_double), ("y1", c_double), ("x2", c_double), ("y2", c_double),
        ("width", c_double), ("cx", c_double), ("cy", c_double),
        ("theta", c_double), ("ax", c_double), ("bx", c_double),
        ("ang_start", c_double), ("ang_end", c_double),
        ("wmin", c_double), ("wmax", c_double),
        ("full", c_int)
    ]

class PointD(Structure):
    _fields_ = [
        ("x", c_double), ("y", c_double)
    ]

class Polygon(Structure):
    _fields_ = [
        ("dim", c_int), ("pts", POINTER(PointD))
    ]


def detect_primitives(img: np.ndarray):
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype("float64")
    h, w = img_gray.shape
    ell_arr = POINTER(Ring)()
    ell_label_arr = POINTER(c_int)()
    ell_count = c_int()
    poly_arr = POINTER(Polygon)()
    poly_label_arr = POINTER(c_int)()
    poly_count = c_int()
    output_img = POINTER(c_int)()
    elsdc.detect_primitives(
        byref(ell_arr), byref(ell_label_arr), byref(ell_count),
        byref(poly_arr), byref(poly_label_arr), byref(poly_count),
        byref(output_img), img_gray.ctypes.data_as(POINTER(c_double)),
        w, h
    )
    return PrimitveSet(ell_arr, ell_label_arr, ell_count.value, poly_arr, 
        poly_label_arr, poly_count.value, output_img, w, h)


class PrimitveSet:
    def __init__(self, ell_arr: POINTER(Ring), ell_label_arr: POINTER(c_int),
        ell_count: int, poly_arr: POINTER(Polygon), 
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
                self.poly_label_arr, self.poly_count, self.output_img)
            self._freed_memory = True

    def __del__(self):
        self.release_memory()


if __name__ == "__main__":
    import sys
    img = cv2.imread(sys.argv[1])
    start = time.monotonic()
    p_set = detect_primitives(img)
    print("Detection took {}s".format(time.monotonic() - start))
    print("Printing out all the ellipse labels and x1 values")
    for i in range(p_set.ell_count):
        print(i, p_set.ell_label_arr[i], p_set.ell_arr[i].x1)
