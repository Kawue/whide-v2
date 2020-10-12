import sys
sys.path.append("..")
import timeit

print "10000\tx\tbmu-Search\t\t\t", timeit.timeit(
    "pycluster.core.bmu(signal,data)",
    setup=
    "import pycluster;import numpy;signal=numpy.random.rand(64);data=numpy.random.rand(10000,64)",
    number=10000), "s"
print "10000\tx\tbmu-Search (float)\t\t", timeit.timeit(
    "pycluster.core.bmuf(signal,data)",
    setup=
    "import pycluster;import numpy;signal=numpy.random.rand(64).astype('float32');data=numpy.random.rand(10000,64).astype('float32')",
    number=10000), "s"
print "10\tx\tbmus-Search\t\t\t", timeit.timeit(
    "pycluster.core.bmus(signals,data)",
    setup=
    "import pycluster;import numpy;signals=numpy.random.rand(1000,64);data=numpy.random.rand(10000,64)",
    number=10), "s"
print "10\tx\tbmus-Search (float)\t\t", timeit.timeit(
    "pycluster.core.bmusf(signals,data)",
    setup=
    "import pycluster;import numpy;signals=numpy.random.rand(1000,64).astype('float32');data=numpy.random.rand(10000,64).astype('float32')",
    number=10), "s"
print "100\tx\tMean Quantization Error\t\t", timeit.timeit(
    "pycluster.core.mqe(signals,centroids,mqe)",
    setup=
    "import pycluster;import numpy;signals=numpy.random.rand(10000,64);centroids=numpy.random.rand(100,64);mqe=numpy.zeros(10000)",
    number=100), "s"
print "100\tx\tMean Quantization Error (float)\t", timeit.timeit(
    "pycluster.core.mqef(signals,centroids,mqe)",
    setup=
    "import pycluster;import numpy;signals=numpy.random.rand(10000,64).astype('float32');centroids=numpy.random.rand(100,64).astype('float32');mqe=numpy.zeros(10000).astype('float32')",
    number=100), "s"
print "1000000\tx\tH2SOM adaption\t\t\t", timeit.timeit(
    "pycluster.core.adapt(signal,centroids,3,1,8,8.,1.,pos)",
    setup=
    "import pycluster;import numpy;signal=numpy.random.rand(64);centroids=numpy.random.rand(9,64);pos=numpy.array([[  0.00000000e+00,   0.00000000e+00],[  4.55089861e-01,   4.55089861e-01],[  3.94087821e-17,   6.43594253e-01],[ -4.55089861e-01,   4.55089861e-01],[ -6.43594253e-01,   7.88175642e-17],[ -4.55089861e-01,  -4.55089861e-01],[ -1.18226346e-16,  -6.43594253e-01],[  4.55089861e-01,  -4.55089861e-01],[  6.43594253e-01,  -1.57635128e-16]])",
    number=1000000), "s"
print "1000000\tx\tH2SOM adaption (float)\t\t", timeit.timeit(
    "pycluster.core.adaptf(signal,centroids,3,1,8,8.,1.,pos)",
    setup=
    "import pycluster;import numpy;signal=numpy.random.rand(64).astype('float32');centroids=numpy.random.rand(9,64).astype('float32');pos=numpy.array([[  0.00000000e+00,   0.00000000e+00],[  4.55089861e-01,   4.55089861e-01],[  3.94087821e-17,   6.43594253e-01],[ -4.55089861e-01,   4.55089861e-01],[ -6.43594253e-01,   7.88175642e-17],[ -4.55089861e-01,  -4.55089861e-01],[ -1.18226346e-16,  -6.43594253e-01],[  4.55089861e-01,  -4.55089861e-01],[  6.43594253e-01,  -1.57635128e-16]]).astype('float32')",
    number=1000000), "s"
