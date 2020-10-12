import unittest
import sys
import numpy
import scipy
sys.path.append("..")
import pycluster


class TestSuite(unittest.TestCase):

    _data = None

    def setUp(self):
        self._data = numpy.random.multivariate_normal(numpy.random.randint(0, 100, 2), numpy.random.randint(0, 100, [2, 2]), 100)
        for i in range(99):
            self._data = numpy.vstack((self._data, numpy.random.multivariate_normal(numpy.random.randint(0, 100, 2), numpy.random.randint(0, 10, [2, 2]), 100)))

    def test_bmu(self):
        signal = numpy.random.rand(2)
        pycluster_idx = pycluster.core.bmu(signal, self._data)
        scipy_idx = numpy.argmin(scipy.spatial.distance.cdist(signal.reshape(1, 2), self._data, 'sqeuclidean'))
        self.assertEqual(pycluster_idx, scipy_idx)

    def test_bmus(self):
        signals = numpy.random.rand(100, 2)
        pycluster_idxs = pycluster.core.bmus(signals, self._data)
        scipy_idxs = numpy.array(map(numpy.argmin, scipy.spatial.distance.cdist(signals, self._data, 'sqeuclidean')))
        self.assertTrue(numpy.all(pycluster_idxs == scipy_idxs))

    def test_bmuf(self):
        signal = numpy.random.rand(2).astype('float32')
        pycluster_idx = pycluster.core.bmuf(signal, self._data.astype('float32'))
        scipy_idx = numpy.argmin(scipy.spatial.distance.cdist(signal.reshape(1, 2).astype('float32'), self._data.astype('float32'), 'sqeuclidean'))
        self.assertEqual(pycluster_idx, scipy_idx)

    def test_bmusf(self):
        signals = numpy.random.rand(100, 2)
        pycluster_idxs = pycluster.core.bmusf(signals.astype('float32'), self._data.astype('float32'))
        scipy_idxs = numpy.array(map(numpy.argmin, scipy.spatial.distance.cdist(signals.astype('float32'), self._data.astype('float32'), 'sqeuclidean')))
        self.assertTrue(numpy.all(pycluster_idxs == scipy_idxs))

    def test_mqe(self):
        signals = numpy.random.rand(10000, 2)
        centroids = numpy.random.rand(100, 2)
        mqe = numpy.zeros(100)
        pycluster.core.mqe(signals, centroids, mqe)

        distmat = scipy.spatial.distance.cdist(signals, centroids, 'sqeuclidean')
        scipy_idxs = numpy.array(map(numpy.argmin, distmat))
        scipy_minvals = numpy.array(map(numpy.min, distmat))
        scipy_mqe = numpy.zeros(100)
        for i in range(100):
            numHits = numpy.sum(scipy_idxs == i)
            if numHits:
                scipy_mqe[i] = numpy.sum(scipy_minvals[scipy_idxs == i]) / numpy.sum(scipy_idxs == i)

        self.assertTrue(numpy.all(scipy_mqe - mqe < 1e-5))

    def test_mqef(self):
        signals = numpy.random.rand(10000, 2).astype('float32')
        centroids = numpy.random.rand(100, 2).astype('float32')
        mqe = numpy.zeros(100).astype('float32')
        pycluster.core.mqef(signals, centroids, mqe)

        distmat = scipy.spatial.distance.cdist(signals, centroids, 'sqeuclidean')
        scipy_idxs = numpy.array(map(numpy.argmin, distmat)).astype('float32')
        scipy_minvals = numpy.array(map(numpy.min, distmat)).astype('float32')
        scipy_mqe = numpy.zeros(100, dtype='float32')
        for i in range(100):
            numHits = numpy.sum(scipy_idxs == i)
            if numHits:
                scipy_mqe[i] = (numpy.sum(scipy_minvals[scipy_idxs == i]) / numpy.sum(scipy_idxs == i)).astype('float32')

        self.assertTrue(numpy.all(scipy_mqe - mqe < 1e-5))

    def test_adapt(self):
        numpy.random.seed(5)
        signal = numpy.random.rand(2)
        centroids = numpy.random.rand(9, 2)
        bmu = 3
        minRing = 1
        maxRing = 8
        curSigma = 8.
        curEpsilon = 1.
        pos = numpy.array([[0.00000000e+00, 0.00000000e+00], [4.55089861e-01, 4.55089861e-01], [3.94087821e-17, 6.43594253e-01], [-4.55089861e-01, 4.55089861e-01], [-6.43594253e-01, 7.88175642e-17], [-4.55089861e-01, -4.55089861e-01], [-1.18226346e-16, -6.43594253e-01], [4.55089861e-01, -4.55089861e-01], [6.43594253e-01, -1.57635128e-16]])
        pycluster.core.adapt(signal, centroids, bmu, minRing, maxRing, curSigma, curEpsilon, pos)
        truecentroids = numpy.load("/Users/dlangenk/testresults/adapt.npy")
        self.assertTrue(numpy.all(truecentroids - centroids < 1e-5))

    def test_adaptf(self):
        numpy.random.seed(5)
        signal = numpy.random.rand(2).astype('float32')
        centroids = numpy.random.rand(9, 2).astype('float32')
        bmu = 3
        minRing = 1
        maxRing = 8
        curSigma = 8.
        curEpsilon = 1.
        pos = numpy.array([[0.00000000e+00, 0.00000000e+00], [4.55089861e-01, 4.55089861e-01], [3.94087821e-17, 6.43594253e-01], [-4.55089861e-01, 4.55089861e-01], [-6.43594253e-01, 7.88175642e-17], [-4.55089861e-01, -4.55089861e-01], [-1.18226346e-16, -6.43594253e-01], [4.55089861e-01, -4.55089861e-01], [6.43594253e-01, -1.57635128e-16]]).astype('float32')
        pycluster.core.adaptf(signal, centroids, bmu, minRing, maxRing, curSigma, curEpsilon, pos)
        truecentroids = numpy.load("/Users/dlangenk/testresults/adaptf.npy")
        self.assertTrue(numpy.all(truecentroids - centroids < 1e-5))

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSuite)
    unittest.TextTestRunner(verbosity=2).run(suite)
