from timeit import timeit

import numpy as np


def op2():
    w = 1920
    h = 1080
    x = np.arange(1, w)
    y = np.arange(1, h)
    return np.sum(np.outer(x, y))


execution_time = timeit(op2, number=10)
