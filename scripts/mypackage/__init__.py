import math
from jobflow import job, flow


@job
def add(a, b):
    return a + b


@job
def mult(a, b):
    return a * b


@job
def sqrt(x):
    return math.sqrt(x)


@flow
def hypot(a, b):
    a2 = mult(a, a)
    b2 = mult(b, b)
    c2 = add(a2.output, b2.output)
    c = sqrt(c2.output)
    return c.output
