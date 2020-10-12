from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import numpy
import os
import platform

pl = platform.system()
if pl == 'Linux':
    os.environ["CC"] = "gcc"
    os.environ["CXX"] = "gcc"
if pl == 'Darwin':
    os.environ["CC"] = "icc"
    os.environ["CXX"] = "icc"

modules = None
if pl == 'Linux':
    modules = [Extension(
        "pyclusterbdmseed.core",
        sources=["pyclusterbdmseed/core.pyx", "pyclusterbdmseed/c_core.c"],
        include_dirs=[numpy.get_include()],
        extra_link_args=["-lcblas"],
        extra_compile_args=["-std=c99", "-ffast-math", "-msse", "-msse2",
                            "-mssse3", "-msse4.1", "-msse4.2", "-mtune=native",
                            "-march=native", "-ftree-vectorize", "-mno-avx"])]
elif pl == 'Darwin':
    modules = [Extension(
        "pyclusterbdmseed.core",
        sources=["pyclusterbdmseed/core.pyx", "pyclusterbdmseed/c_core.c"],
        include_dirs=[numpy.get_include()],
        extra_link_args=["-qopenmp"],
        extra_compile_args=["-DINTEL_MKL_VERSION", "-qopenmp", "-std=c99", "-Ofast",
                            "-Wl,-rpath,/opt/intel/compilers_and_libraries/mac/lib"])]
else:
    print("test")
    modules = [Extension(
        "pyclusterbdmseed.core",
        sources=["pyclusterbdmseed/core.pyx", "pyclusterbdmseed/c_core.c"],
        include_dirs=[numpy.get_include()])]

setup(
    name="pyclusterbdmseed",
    version='0.2',
    packages=['pyclusterbdmseed'],
    description='Unsupervised Machine Learning Algorithms for Python',
    install_requires=[
        'cython>=0.25.2',
        'numpy>=1.13.0',
        'scikit-learn>=0.18.2',
        'scipy>=0.19.1'
    ],
    ext_modules=cythonize(modules),
    test_suite='run_tests',
)
