#!/usr/bin/env python

import ctypes
import numpy as np
import pathlib


HOME = pathlib.Path().absolute()


if __name__ == "__main__":
    c_lib = ctypes.CDLL(HOME/'c_function.so')
    c_lib.cfunc_float.restype = ctypes.c_float

    pi = ctypes.c_float(np.pi)
    a = ctypes.c_float(2.0)
    b = ctypes.c_float(5.0)
    print(c_lib.cfunc_float(pi, a, b))
