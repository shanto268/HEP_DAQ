# cython: language_level=3
import cython
import numpy as np
cimport numpy as np
cimport cython
from cython.parallel import prange


DTYPE_f64 = np.float64
ctypedef np.float64_t DTYPE_f64_t


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
cdef int count_above_cython(DTYPE_f64_t [:] arr_view, DTYPE_f64_t thresh) nogil:

    cdef int length, i, total
    total = 0
    length = arr_view.shape[0]

    for i in prange(length):
        if arr_view[i] >= thresh:
            total += 1

    return total


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
def count_above(np.ndarray arr, DTYPE_f64_t thresh):

    cdef DTYPE_f64_t [:] arr_view = arr.ravel()
    cdef int total

    with nogil:
       total =  count_above_cython(arr_view, thresh)
    return total

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
cdef int count_below_cython(DTYPE_f64_t [:] arr_view, DTYPE_f64_t thresh) nogil:

    cdef int length, i, total
    total = 0
    length = arr_view.shape[0]

    for i in prange(length):
        if arr_view[i] <= thresh:
            total += 1

    return total


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
def count_below(np.ndarray arr, DTYPE_f64_t thresh):
    cdef DTYPE_f64_t [:] arr_view = arr.ravel()
    cdef int total
    with nogil:
        total =  count_below_cython(arr_view, thresh)
        return total


