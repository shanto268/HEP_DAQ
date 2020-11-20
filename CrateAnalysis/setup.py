# usage: python setup.py build_ext --inplace

from setuptools import setup
from Cython.Build import cythonize
import numpy

setup(
    name='Counts Numbers Up or Down',
    ext_modules=cythonize("countercy.pyx"),
    zip_safe=False,
)
