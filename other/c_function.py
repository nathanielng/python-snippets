#!/usr/bin/env python

import ctypes
import numpy as np
import pathlib


HOME = pathlib.Path().absolute()


def float_demo():
    c_lib = ctypes.CDLL(HOME/'c_function.so')
    c_lib.cfunc_float.restype = ctypes.c_float

    pi = ctypes.c_float(np.pi)
    a = ctypes.c_float(2.0)
    b = ctypes.c_float(4.987654321)
    print(c_lib.cfunc_float(pi, a, b))


def double_demo():
    c_lib = ctypes.CDLL(HOME/'c_function.so')
    c_lib.cfunc_double.restype = ctypes.c_double

    pi = ctypes.c_double(np.pi)
    a = ctypes.c_double(2.0)
    b = ctypes.c_double(4.987654321)
    print(c_lib.cfunc_double(pi, a, b))


if __name__ == "__main__":
    float_demo()
    double_demo()
