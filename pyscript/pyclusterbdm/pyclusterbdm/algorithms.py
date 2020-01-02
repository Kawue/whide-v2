import numpy
import math
import core
import clusterValidation
import scipy.spatial
import collections
import scipy.stats
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn import preprocessing
import sklearn.neighbors


class H2SOM:
    def __init__(self, data, epsilon=[1., 0.01], sigma=[8., 0.1], n_iter=10, arch=[3, 8], globalSearch=True, swidth=2):
        self._data = data
        self._rings = []
        self._childs = dict()
        self._sigma = sigma
        self._epsilon = epsilon
        self._n_iter = n_iter
        self._arch = arch
        self._pos = numpy.zeros((self.numNodes(arch), 2))
        self._centroids = numpy.zeros((self.numNodes(arch), data.shape[1]))
        self._globalSearch = globalSearch
        self._swidth = swidth
        if globalSearch:
            self.buildNetwork(self._arch)

    def dumpParameters(self):
        print('Architecture\t', self._arch)
        print('Sigma\t\t', self._sigma)
        print('Epsilon\t\t', self._epsilon)
        print('n_iter\t', self._n_iter)
        print('BeamSearch\t', not self._globalSearch)
        if not self._globalSearch:
            print('swidth\t\t', self._swidth)

    def addRing(self, first, last, spread):
        iCurrent = last + 1
        self._neighbourList[last] += 1
        self._neighbourList[iCurrent] += 1
        for originID in range(first, last + 1):
            iNumToAdd = spread - self._neighbourList[originID]
            for j in range(iNumToAdd):
                nodetoadd = self.rotateNode(originID, iCurrent - 1)
                self._pos[iCurrent] = nodetoadd
                self._neighbourList[iCurrent] += 3
                self._neighbourList[originID] += 1
                iCurrent += 1
            if originID != last:
                self._neighbourList[iCurrent - 1] += 1
                self._neighbourList[originID + 1] += 1
        return iCurrent - 1

    def rotateNode(self, iCenter, iFrom):
        tNewPos = [0, 0]
        fX1 = self._pos[iCenter][0]
        fY1 = self._pos[iCenter][1]
        fX2 = self._pos[iFrom][0]
        fY2 = self._pos[iFrom][1]
        fU = 1. - fX1 * fX2 - fY1 * fY2
        fV = fX2 * fY1 - fX1 * fY2
        fQ = fU * fU + fV * fV
        fDx = fX2 - fX1
        fDy = fY2 - fY1
        fX2 = (fDx * fU + fDy * fV) / fQ
        fY2 = (-fDx * fV + fDy * fU) / fQ
        fTmp = self._fCos * fX2 - self._fSin * fY2
        fY2 = self._fSin * fX2 + self._fCos * fY2
        fX2 = fTmp
        fU = 1. + fX1 * fX2 + fY1 * fY2
        fV = -fX2 * fY1 + fX1 * fY2
        fQ = fU * fU + fV * fV
        fDx = fX2 + fX1
        fDy = fY2 + fY1
        tNewPos[0] = (fDx * fU + fDy * fV) / fQ
        tNewPos[1] = (-fDx * fV + fDy * fU) / fQ
        return tNewPos

    def cluster(self):
        _learningSteps = self._n_iter * self._data.shape[0]
        if self._globalSearch:
            # set initial solution to mean of data
            initial = numpy.mean(self._data, axis=0)
            self._centroids[0] = initial
            for i in self._childs[0]:
                self._centroids[i] = self._centroids[0]

            # train each ring
            for ringIdx, ring in enumerate(self._rings):
                # print 'ringIdx',ringIdx,ring
                cursigma = self._sigma[0]  # TODO modify sigma for each ring
                sigStep = (cursigma - self._sigma[1]) / _learningSteps

                curepsilon = self._epsilon[0]
                epsStep = (curepsilon - self._epsilon[1]) / _learningSteps
                core.learning(self._data, self._centroids, _learningSteps,
                              ring[0], ring[1], cursigma, sigStep, curepsilon,
                              epsStep, self._pos)

                # init centroids for next ring
                if self._rings.index(ring) != (len(self._rings) - 1):
                    for i in range(ring[0], ring[1] + 1):
                        for child in self._childs[i]:
                            self._centroids[child] = self._centroids[i]
        else:
            core.h2sombeam_learning(
                self._data, self._centroids, _learningSteps, self._arch[0],
                self._arch[1], self._swidth, self._sigma[0], self._sigma[1],
                self._epsilon[0], self._epsilon[1])
            # numNodes=core.h2sombeam_learning(self._data,self._centroids,_learningSteps,self._arch[0],self._arch[1],self._swidth,self._sigma[0],self._sigma[1],self._epsilon[0],self._epsilon[1])
            # self._centroids=self._centroids[0:numNodes,:]

    def newNodes(self, arch):
        if arch[0] == 0:
            return 1
        if arch[0] == 1:
            return arch[1]
        if arch[0] == 2:
            return arch[1] * (arch[1] - 4)
        return self.newNodes([arch[0] - 1, arch[1]]) * (
            arch[1] - 4) - self.newNodes([arch[0] - 2, arch[1]])

    def numNodes(self, arch):
        if arch[0] == 0:
            return 1
        if arch[0] == 1:
            return arch[1] + 1
        return self.newNodes(arch) + self.numNodes([arch[0] - 1, arch[1]])

    def buildNetwork(self, arch):
        for ring in range(1, self._arch[0] + 1):
            self._rings.append([self.numNodes([ring - 1, arch[1]
                                               ]), self.numNodes([ring - 1, arch[1]]) +
                                self.newNodes([ring, arch[1]]) - 1])

        self._childs[0] = range(1, arch[1] + 1)
        cur = arch[1] + 1
        marker = arch[1]
        doubles = []
        for i in range(1, self.numNodes([arch[0] - 1, arch[1]])):
            if i == marker:
                self._childs[i] = [marker + 1] + range(cur, cur +
                                                       (arch[1] - 4))
                doubles += [marker + 1]
                marker = cur + (arch[1] - 5)
                cur += (arch[1] - 4)
            elif i in doubles:
                self._childs[i] = range(cur, cur + (arch[1] - 4))
                doubles += [cur + (arch[1] - 5)]
                cur += (arch[1] - 5)
            else:
                self._childs[i] = range(cur, cur + (arch[1] - 3))
                cur += (arch[1] - 4)
                doubles += [cur]

        # addGeometry
        fAngle = 2. * math.pi / self._arch[1]
        fRadius = math.sqrt(
            1.0 - 4.0 * math.pow(math.sin(math.pi / self._arch[1]), 2))
        self._fSin = math.sin(fAngle)
        self._fCos = math.cos(fAngle)
        self._neighbourList = numpy.zeros(self.numNodes(arch), numpy.int)
        self._neighbourList[0] = self._arch[1]
        # Add first ring
        for i in range(1, self._arch[1] + 1):
            tmp = [0, 0]
            tmp[0] = fRadius * math.cos(i * fAngle)
            tmp[1] = fRadius * math.sin(i * fAngle)
            self._pos[i] = tmp
            self._neighbourList[i] = 3

        # Add further rings
        iFirst = 1
        iLast = self._arch[1]
        for i in range(1, self._arch[0]):
            iLastAdded = self.addRing(iFirst, iLast, self._arch[1])
            iFirst = iLast + 1
            iLast = iLastAdded

    _data = None
    _sigma = [None, None]
    _epsilon = [None, None]
    _n_iter = None
    _arch = [None, None]
    _centroids = None
    _childs = None
    _rings = None
    _globalSearch = None
    _swidth = None
    _pos = None
    _neighbourList = None
    _fSin = None
    _fCos = None
    _lbl = None


class H2SOMClassifier(BaseEstimator, ClassifierMixin, H2SOM):
    def __init__(self,
                 epsilon=[1., 0.01],
                 sigma=[8., 0.1],
                 n_iter=10,
                 arch=[3, 8],
                 globalSearch=True,
                 swidth=2):
        self._sigma = sigma
        self._epsilon = epsilon
        self._n_iter = n_iter
        self._arch = arch
        self._globalSearch = globalSearch
        self._swidth = swidth

    def fit(self, X, y):
        self.classes_, self._indices = numpy.unique(y, return_inverse=True)
        self._childs = dict()
        self._rings = []
        self._pos = numpy.zeros((self.numNodes(self._arch), 2))
        if self._globalSearch:
            self.buildNetwork(self._arch)

        self._data = X
        self._centroids = numpy.zeros((self.numNodes(self._arch), X.shape[1]))
        self.cluster()
        self._lbl = numpy.zeros(self._centroids.shape[0], dtype=int)
        self._proba = numpy.zeros(
            (self._centroids.shape[0], self.classes_.shape[0]))
        d2c = core.bmus(self._data, self._centroids)

        approved = []

        for i in range(self._centroids.shape[0]):
            count = collections.Counter(self._indices[d2c == i])
            normdiv = numpy.sum(count.values())
            self._proba[i, count.keys()] = numpy.array(
                count.values()).astype(float) / normdiv
            mc = count.most_common(1)
            if mc:
                self._lbl[i] = mc[0][0]
                approved.append(i)

        self._lbl = self._lbl[approved]
        self._centroids = self._centroids[approved]
        self._proba = self._proba[approved]
        return self

    def predict(self, X):
        return self.classes_[self._lbl[core.bmus(X, self._centroids)]]

    def predictNeighborSmoothing(self, X):
        ret = []
        distmat = scipy.spatial.distance.cdist(X, self._centroids)
        for i in distmat:
            bmu = numpy.argmin(i)
            # which ring
            for ridx, j in enumerate(self._rings):
                if bmu >= j[0] and bmu <= j[1]:
                    break
            # cring = numpy.arange(self._rings[ridx][0], self._rings[ridx][1] + 1)
            # pos = numpy.where(cring == bmu)[0]
            lneighbor = bmu - 1 if bmu - 1 > self._rings[ridx][0] else (self._rings[ridx][1] - 1) % self._centroids.shape[0]
            uneighbor = (bmu + 1) % self._centroids.shape[0]
            if bmu != 0 and (i[lneighbor] + i[uneighbor]) < (3 * i[bmu]) and self._lbl[lneighbor] == self._lbl[uneighbor]:
                ret.append(self.classes_[self._lbl[uneighbor]])
            else:
                ret.append(self.classes_[self._lbl[bmu]])
        return numpy.array(ret)

    def predictThreshold(self, X, threshold):
        ret = []
        distmat = scipy.spatial.distance.cdist(X, self._centroids)
        for i in distmat:
            bmu = numpy.argmin(i)
            if i[bmu] > threshold:
                ret.append(-1)
            else:
                ret.append(self.classes_[self._lbl[bmu]])
        return numpy.array(ret)

    def predict_proba(self, X):
        distmat = scipy.spatial.distance.cdist(X, self._centroids)
        probs = numpy.zeros((X.shape[0], self.classes_.shape[0]))
        idx = self._lbl[numpy.argmin(distmat, 1)]
        probs[range(idx.shape[0]), idx] = numpy.exp(-numpy.min(distmat, 1))
        return probs

    def get_params(self, deep=True):
        return {
            "epsilon": self._epsilon,
            "sigma": self._sigma,
            "n_iter": self._n_iter,
            "arch": self._arch,
            "globalSearch": self._globalSearch,
            "swidth": self._swidth
        }

    def set_params(self, **parameters):
        self._epsilon = parameters['epsilon'
                                   ] if 'epsilon' in parameters else self._epsilon
        self._sigma = parameters['sigma'
                                 ] if 'sigma' in parameters else self._sigma
        self._n_iter = parameters['n_iter'
                                  ] if 'n_iter' in parameters else self._n_iter
        self._arch = parameters['arch'] if 'arch' in parameters else self._arch
        self._globalSearch = parameters[
            'globalSearch'
        ] if 'globalSearch' in parameters else self._globalSearch
        self._swidth = parameters['swidth'
                                  ] if 'swidth' in parameters else self._swidth
        return self

    _lbl = None
    classes_ = None
    _proba = None
    _indices = None


class H2SOMClassifierRejection(H2SOMClassifier):
    def fit(self, X, y):
        self.classes_, self._indices = numpy.unique(y, return_inverse=True)
        # add rejection class at last position
        self.classes_ = numpy.hstack((self.classes_, [-1]))
        self._childs = dict()
        self._rings = []
        self._pos = numpy.zeros((self.numNodes(self._arch), 2))
        if self._globalSearch:
            self.buildNetwork(self._arch)

        self._data = X
        self._centroids = numpy.zeros((self.numNodes(self._arch), X.shape[1]))
        self.cluster()
        self._lbl = numpy.zeros(self._centroids.shape[0], dtype=int)
        self._proba = numpy.zeros(
            (self._centroids.shape[0], self.classes_.shape[0]))
        d2c = core.bmus(self._data, self._centroids)

        approved = []

        for i in range(self._centroids.shape[0]):
            count = collections.Counter(self._indices[d2c == i])
            normdiv = numpy.sum(count.values())
            self._proba[i, count.keys()] = numpy.array(
                count.values()).astype(float) / normdiv
            mc = count.most_common(1)
            if mc:
                if float(mc[0][1]) / sum(count.values()) > 0.7:
                    self._lbl[i] = mc[0][0]
                else:
                    self._lbl[i] = -1
                approved.append(i)

        self._lbl = self._lbl[approved]
        self._centroids = self._centroids[approved]
        self._proba = self._proba[approved]
        return self

    def predict_proba(self, X):
        raise NotImplementedError('Belief value of rejected is undefined')


def outputLLM(theta, A, input, weight):
    return theta + numpy.dot(A, (input - weight) / numpy.linalg.norm(input -
                                                                     weight))


def normedOutputLLM(theta, A, input, weight):
    orig = outputLLM(theta, A, input, weight)
    mi = min(orig)
    if mi < 0:
        return sklearn.preprocessing.normalize(numpy.atleast_2d(orig - mi),
                                               norm='l1')
    else:
        return sklearn.preprocessing.normalize(numpy.atleast_2d(orig),
                                               norm='l1')


def trainLLM(outputdim, weight, data, labels, epsilon):
    items = data.shape[0]
    dim = data.shape[1]

    learningSteps = items * 10
    theta = numpy.zeros(outputdim)
    A = numpy.zeros((outputdim, dim))
    epsStep = ((epsilon[0] - epsilon[1]) / learningSteps)
    eps = epsilon[0]

    numpy.random.seed(2)

    for i in range(learningSteps):
        signal = numpy.random.randint(0, items)
        output = numpy.zeros(outputdim)
        output[labels[signal]] = 1.

        deltatheta = eps * (output - outputLLM(theta, A, data[signal], weight))
        lvec = numpy.linalg.norm((data[signal] - weight))
        if lvec != 0:
            outputLL = outputLLM(theta, A, data[signal], weight)
            front = eps * (output - outputLL)
            back = ((data[signal] - weight).transpose() / lvec)
            prod = numpy.outer(front, back)
            A += prod
        theta += deltatheta
        eps -= epsStep
    return A, theta


class H2SOMClassifierLLM(H2SOMClassifier):
    def _setup(self, X, y, classes=None):
        if classes is None:
            self.classes_, _ = numpy.unique(y, return_inverse=True)
        else:
            self.classes_ = classes
        self._childs = dict()
        self._rings = []
        self._pos = numpy.zeros((self.numNodes(self._arch), 2))
        if self._globalSearch:
            self.buildNetwork(self._arch)

        self._data = X
        self._y = y
        self._centroids = numpy.zeros((self.numNodes(self._arch), X.shape[1]))
        self._shortcut = numpy.ones(self.numNodes(self._arch)) * -1
        self._As = [None] * self.numNodes(self._arch)
        self._thetas = [None] * self.numNodes(self._arch)
        self._les = [None] * self.numNodes(self._arch)
        self._le = preprocessing.LabelEncoder()
        self._le.fit(self.classes_)
        self._bmuCounter = numpy.zeros((self.numNodes(self._arch)), numpy.int32)

    def _training(self, y):
        approved = []
        d2c = core.bmus(self._data, self._centroids)
        self._tmpd2c = d2c
        tmpidx = 1
        for i in range(self._centroids.shape[0]):
            if sum(d2c == i):
                classes = numpy.unique(y[d2c == i])
                numClasses = classes.shape[0]
                if numClasses == 1:
                    self._shortcut[i] = classes[0]
                else:
                    tmple = preprocessing.LabelEncoder()
                    tmple.fit(self._le.transform(classes))
                    # remember classes which are used
                    A, theta = trainLLM(numClasses, self._centroids[i], numpy.require(self._data[d2c == i], requirements='C'), tmple.transform(self._le.transform(y[d2c == i])), [0.99, 0.01])
                    self._As[i] = A
                    self._thetas[i] = theta
                    self._les[i] = tmple
                approved.append(i)
                tmpidx += 1
        self._tmpapproved = approved
        self._centroids = self._centroids[approved]
        self._shortcut = self._shortcut[approved]
        self._As = [self._As[i] for i in approved]
        self._thetas = [self._thetas[i] for i in approved]
        self._les = [self._les[i] for i in approved]

    def fit(self, X, y):
        self._setup(X, y)
        self.cluster()
        self._training(y)
        return self

    def finetune(self, X, y):
        '''
        finetune(self, X, y)

        Finetune an already trained net.

        Parameters
        ----------
        X: ndarray[double], shape(m,n)
            The data which should be used for finetuning

        y: ndarray[double], shape(n)
            The target for X.

        Returns
        -------
        self:
            Returns the classifier
        '''
        d2c = core.bmus(X, self._centroids)
        self._data = numpy.vstack((self._data, X))
        self._y = numpy.hstack((self._y, y))
        alld2c = core.bmus(self._data, self._centroids)
        for i in d2c:
            classes = numpy.unique(self._y[alld2c == i])
            numClasses = classes.shape[0]
            tmple = preprocessing.LabelEncoder()
            tmple.fit(self._le.transform(classes))
            A, theta = trainLLM(numClasses, self._centroids[i], numpy.require(self._data[alld2c == i], requirements='C'), tmple.transform(self._le.transform(self._y[alld2c == i])), [0.99, 0.01])
            self._As[i] = A
            self._thetas[i] = theta
            self._les[i] = tmple
        return self

    def partial_fit(self, X, y, classes=None):
        if not self._setupDone:
            self._setup(X, y, classes)

            self._data = X
            self._y = y
            _learningSteps = self._n_iter * self._data.shape[0]
            # set initial solution to mean of data
            initial = numpy.mean(self._data, axis=0)
            self._centroids[0] = initial
            for i in self._childs[0]:
                self._centroids[i] = self._centroids[0]
            self._setupDone = True

        # alternatingly learn old and new data
        # train each ring
            for ringIdx, ring in enumerate(self._rings):
                # print 'ringIdx',ringIdx,ring
                cursigma = self._sigma[0]  # TODO modify sigma for each ring
                sigStep = (cursigma - self._sigma[1]) / _learningSteps

                curepsilon = self._epsilon[0]
                epsStep = (curepsilon - self._epsilon[1]) / _learningSteps
                core.partial_learning(self._data, X, self._centroids, _learningSteps, ring[0], ring[1], cursigma, sigStep, curepsilon, epsStep, self._pos, self._bmuCounter)

                # init centroids for next ring
                if self._rings.index(ring) != (len(self._rings) - 1):
                    for i in range(ring[0], ring[1] + 1):
                        for child in self._childs[i]:
                            self._centroids[child] = self._centroids[i]

        self._data = numpy.vstack((self._data, X))
        self._y = numpy.hstack((self._y, y))
        # # approved = []
        # d2c = core.bmus(self._data, self._centroids)
        # self._tmpd2c = d2c
        # tmpidx = 1
        # for i in range(self._centroids.shape[0]):
        #     if sum(d2c == i):
        #         classes = numpy.unique(self._y[d2c == i])
        #         numClasses = classes.shape[0]
        #         if numClasses == 1:
        #             self._shortcut[i] = classes[0]
        #         else:
        #             tmple = preprocessing.LabelEncoder()
        #             tmple.fit(self._le.transform(classes))
        #             A, theta = trainLLM(numClasses, self._centroids[i], numpy.require(self._data[d2c == i], requirements='C'), tmple.transform(self._le.transform(self._y[d2c == i])), [0.99, 0.01])
        #             self._As[i] = A
        #             self._thetas[i] = theta
        #             self._les[i] = tmple
        #         # approved.append(i)
        #         tmpidx += 1
        # self._tmpapproved = approved
        # self._centroids = self._centroids[approved]
        # self._shortcut = self._shortcut[approved]
        # self._As = [self._As[i] for i in approved]
        # self._thetas = [self._thetas[i] for i in approved]
        # self._les = [self._les[i] for i in approved]
        return self

    def finishIt(self):
        approved = []
        d2c = core.bmus(self._data, self._centroids)
        self._tmpd2c = d2c
        tmpidx = 1
        for i in range(self._centroids.shape[0]):
            if sum(d2c == i):
                classes = numpy.unique(self._y[d2c == i])
                numClasses = classes.shape[0]
                if numClasses == 1:
                    self._shortcut[i] = classes[0]
                else:
                    tmple = preprocessing.LabelEncoder()
                    tmple.fit(self._le.transform(classes))
                    A, theta = trainLLM(numClasses, self._centroids[i], numpy.require(self._data[d2c == i], requirements='C'), tmple.transform(self._le.transform(self._y[d2c == i])), [0.99, 0.01])
                    self._As[i] = A
                    self._thetas[i] = theta
                    self._les[i] = tmple
                approved.append(i)
                tmpidx += 1
        # print approved
        # print self._As
        self._tmpapproved = approved
        self._centroids = self._centroids[approved]
        self._shortcut = self._shortcut[approved]
        self._As = [self._As[i] for i in approved]
        self._thetas = [self._thetas[i] for i in approved]
        self._les = [self._les[i] for i in approved]
        return self

    def predict(self, X):
        # implement shortcut of shortcut
        proba = self.predict_proba(X)
        idxs = numpy.argmax(proba, 1)
        return self._le.inverse_transform(idxs)

    def predict_proba(self, X):
        d2c = core.bmus(X, self._centroids)
        self._tmpd2c2 = d2c
        proba = numpy.zeros((X.shape[0], self.classes_.shape[0]))
        for idx, i in enumerate(X):
            if self._shortcut[d2c[idx]] != -1:
                ret = numpy.zeros(self.classes_.shape[0])
                ret[self._le.transform([self._shortcut[d2c[idx]]])[0]] = 1.
                proba[idx] = ret
            else:
                # proba[idx]=core.outputLLM(self.classes_.shape[0],self._As[d2c[idx]],self._thetas[d2c[idx]],i,self._centroids[d2c[idx]])
                # proba[idx][self._les[d2c[idx]].classes_]=normedOutputLLM(self._thetas[d2c[idx]],self._As[d2c[idx]],i,self._weights[d2c[idx]])#self._centroids[d2c[idx]]
                proba[idx][self._les[d2c[idx]].classes_] = normedOutputLLM(
                    self._thetas[d2c[idx]], self._As[d2c[idx]], i,
                    self._centroids[d2c[idx]])  # self._centroids[d2c[idx]]
        return proba

    _As = None
    _thetas = None
    _weights = None
    _le = None
    _les = None
    _tmpd2c = None
    _tmpd2c2 = None
    _tmpapproved = None
    _setupDone = False


class H2SOLbalanced(H2SOMClassifierLLM):
    def fit(self, X, y):
        self._setup(X, y)
        self.cluster(y)
        self._training(y)
        return self

    def cluster(self, y):
        _learningSteps = self._n_iter * self._data.shape[0]
        if self._globalSearch:
            # set initial solution to mean of data
            initial = numpy.mean(self._data, axis=0)
            self._centroids[0] = initial
            for i in self._childs[0]:
                self._centroids[i] = self._centroids[0]

            # train each ring
            for ringIdx, ring in enumerate(self._rings):
                # print 'ringIdx',ringIdx,ring
                cursigma = self._sigma[0]  # TODO modify sigma for each ring
                sigStep = (cursigma - self._sigma[1]) / _learningSteps

                curepsilon = self._epsilon[0]
                epsStep = (curepsilon - self._epsilon[1]) / _learningSteps

                counts = numpy.bincount(y.astype(int)).astype(float)
                tmpp = 1. / counts[counts.nonzero()] / self.classes_.shape[0]
                # tmpp /= numpy.sum(tmpp)
                p = numpy.zeros(self._data.shape[0])
                for idx, cl in enumerate(self.classes_):
                    p[y == cl] = tmpp[idx]
                s = numpy.random.choice(numpy.arange(0, self._data.shape[0]), _learningSteps, p=p).astype(numpy.int32)

                core.balanced_learning(s, self._data, self._centroids, _learningSteps,
                                       ring[0], ring[1], cursigma, sigStep, curepsilon,
                                       epsStep, self._pos)

                # init centroids for next ring
                if self._rings.index(ring) != (len(self._rings) - 1):
                    for i in range(ring[0], ring[1] + 1):
                        for child in self._childs[i]:
                            self._centroids[child] = self._centroids[i]
        else:
            core.h2sombeam_learning(
                self._data, self._centroids, _learningSteps, self._arch[0],
                self._arch[1], self._swidth, self._sigma[0], self._sigma[1],
                self._epsilon[0], self._epsilon[1])


class H2SOMClassifierKNN(H2SOMClassifier):
    def fit(self, X, y):
        self.classes_, self._indices = numpy.unique(y, return_inverse=True)
        self._childs = dict()
        self._rings = []
        self._pos = numpy.zeros((self.numNodes(self._arch), 2))
        if self._globalSearch:
            self.buildNetwork(self._arch)

        self._data = X
        self._centroids = numpy.zeros((self.numNodes(self._arch), X.shape[1]))
        self.cluster()
        self._le = preprocessing.LabelEncoder()
        self._le.fit(self.classes_)
        self._knns = []

        approved = []
        d2c = core.bmus(self._data, self._centroids)
        for i in range(self._centroids.shape[0]):
            if sum(d2c == i):
                neigh = sklearn.neighbors.KNeighborsClassifier(max(2, min(
                    5, sum(d2c == i))))
                neigh.fit(numpy.require(self._data[d2c == i],
                                        requirements='C'), self._le.transform(
                                            y[d2c == i]))
                self._knns.append(neigh)
                approved.append(i)
        self._centroids = self._centroids[approved]
        return self

    def predict(self, X):
        d2c = core.bmus(X, self._centroids)
        pred = numpy.zeros(X.shape[0])
        for idx, i in enumerate(X):
            pred[idx] = self._knns[d2c[idx]].predict(i)
        pred = pred.astype(numpy.int)
        return self._le.inverse_transform(pred)

    def predict_proba(self, X):
        d2c = core.bmus(X, self._centroids)
        proba = numpy.zeros((X.shape[0], self.classes_.shape[0]))
        for idx, i in enumerate(X):
            # proba[idx]=core.outputLLM(self.classes_.shape[0],self._As[d2c[idx]],self._thetas[d2c[idx]],i,self._centroids[d2c[idx]])
            proba[idx, self._knns[d2c[idx]].classes_
                  ] = self._knns[d2c[idx]].predict_proba(i)[0]
        return proba

    _le = None
    _knns = None


class pyH2SOM:
    def __init__(self, data, epsilon, sigma, learningSteps, arch, labels):
        self._data = data
        self._rings = []
        self._childs = dict()
        self._sigma = sigma
        self._epsilon = epsilon
        self._learningSteps = learningSteps
        self._arch = arch
        self._pos = numpy.zeros((self.numNodes(arch), 2))
        self._centroids = numpy.zeros((self.numNodes(arch), data.shape[1]))
        self._labels = labels
        self.buildNetwork(self._arch)

    def dumpParameters(self):
        print('Architecture\t', self._arch)
        print('Sigma\t\t', self._sigma)
        print('Epsilon\t\t', self._epsilon)
        print('learningSteps\t', self._learningSteps)

    def addRing(self, first, last, spread):
        iCurrent = last + 1
        self._neighbourList[last] += 1
        self._neighbourList[iCurrent] += 1
        for originID in range(first, last + 1):
            iNumToAdd = spread - self._neighbourList[originID]
            for j in range(iNumToAdd):
                nodetoadd = self.rotateNode(originID, iCurrent - 1)
                self._pos[iCurrent] = nodetoadd
                self._neighbourList[iCurrent] += 3
                self._neighbourList[originID] += 1
                iCurrent += 1
            if originID != last:
                self._neighbourList[iCurrent - 1] += 1
                self._neighbourList[originID + 1] += 1
        return iCurrent - 1

    def rotateNode(self, iCenter, iFrom):
        tNewPos = [0, 0]
        fX1 = self._pos[iCenter][0]
        fY1 = self._pos[iCenter][1]
        fX2 = self._pos[iFrom][0]
        fY2 = self._pos[iFrom][1]
        fU = 1. - fX1 * fX2 - fY1 * fY2
        fV = fX2 * fY1 - fX1 * fY2
        fQ = fU * fU + fV * fV
        fDx = fX2 - fX1
        fDy = fY2 - fY1
        fX2 = (fDx * fU + fDy * fV) / fQ
        fY2 = (-fDx * fV + fDy * fU) / fQ
        fTmp = self._fCos * fX2 - self._fSin * fY2
        fY2 = self._fSin * fX2 + self._fCos * fY2
        fX2 = fTmp
        fU = 1. + fX1 * fX2 + fY1 * fY2
        fV = -fX2 * fY1 + fX1 * fY2
        fQ = fU * fU + fV * fV
        fDx = fX2 + fX1
        fDy = fY2 + fY1
        tNewPos[0] = (fDx * fU + fDy * fV) / fQ
        tNewPos[1] = (-fDx * fV + fDy * fU) / fQ
        return tNewPos

    def cluster(self):
        # set initial solution to mean of data
        initial = numpy.mean(self._data, axis=0)
        self._centroids[0] = initial
        for i in self._childs[0]:
            self._centroids[i] = self._centroids[0]

        randlist = []
        count = collections.Counter(self._labels)
        mc = count.most_common(1)[0][1]
        for i in count:
            randlist += list(numpy.where(self._labels == i)[0])
            diff = mc - count[i]
            if diff:
                randlist += list(numpy.random.choice(numpy.where(
                    self._labels == i)[0], diff))
        # train each ring
        for ringIdx, ring in enumerate(self._rings):
            cursigma = self._sigma[0]
            sigStep = (cursigma - self._sigma[1]) / self._learningSteps

            curepsilon = self._epsilon[0]
            epsStep = (curepsilon - self._epsilon[1]) / self._learningSteps
            core.lbllearning(self._data, self._centroids, self._learningSteps,
                             ring[0], ring[1], cursigma, sigStep, curepsilon,
                             epsStep, numpy.array(randlist), self._pos)

            # for i in range(self._learningSteps):
            #   sig=self._data[numpy.random.choice(randlist)[0]]
            #   bmu=ring[0]+core.bmu(sig,self._centroids[ring[0]:ring[1]+1])
            #   core.adapt(sig,self._centroids,self._mapWidth,bmu,ring[0],ring[1],cursigma,curepsilon)  #ring[1]-1
            #   cursigma-=sigStep
            #   curepsilon-=epsStep

            # init centroids for next ring
            if self._rings.index(ring) != (len(self._rings) - 1):
                for i in range(ring[0], ring[1] + 1):
                    for child in self._childs[i]:
                        self._centroids[child] = self._centroids[i]

    def newNodes(self, arch):
        if arch[0] == 0:
            return 1
        if arch[0] == 1:
            return arch[1]
        if arch[0] == 2:
            return arch[1] * (arch[1] - 4)
        return self.newNodes([arch[0] - 1, arch[1]]) * (
            arch[1] - 4) - self.newNodes([arch[0] - 2, arch[1]])

    def numNodes(self, arch):
        if arch[0] == 0:
            return 1
        if arch[0] == 1:
            return arch[1] + 1
        return self.newNodes(arch) + self.numNodes([arch[0] - 1, arch[1]])

    def buildNetwork(self, arch):
        for ring in range(1, self._arch[0] + 1):
            self._rings.append([self.numNodes([ring - 1, arch[1]
                                               ]), self.numNodes([ring - 1, arch[1]]) +
                                self.newNodes([ring, arch[1]]) - 1])

        self._childs[0] = range(1, arch[1] + 1)
        cur = arch[1] + 1
        marker = arch[1]
        doubles = []
        for i in range(1, self.numNodes([arch[0] - 1, arch[1]])):
            if i == marker:
                self._childs[i] = [marker + 1] + range(cur, cur +
                                                       (arch[1] - 4))
                doubles += [marker + 1]
                marker = cur + (arch[1] - 5)
                cur += (arch[1] - 4)
            elif i in doubles:
                self._childs[i] = range(cur, cur + (arch[1] - 4))
                doubles += [cur + (arch[1] - 5)]
                cur += (arch[1] - 5)
            else:
                self._childs[i] = range(cur, cur + (arch[1] - 3))
                cur += (arch[1] - 4)
                doubles += [cur]

        # addGeometry
        fAngle = 2. * math.pi / self._arch[1]
        fRadius = math.sqrt(
            1.0 - 4.0 * math.pow(math.sin(math.pi / self._arch[1]), 2))
        self._fSin = math.sin(fAngle)
        self._fCos = math.cos(fAngle)
        self._neighbourList = numpy.zeros(self.numNodes(arch), numpy.int)
        self._neighbourList[0] = self._arch[1]
        # Add first ring
        for i in range(1, self._arch[1] + 1):
            tmp = [0, 0]
            tmp[0] = fRadius * math.cos(i * fAngle)
            tmp[1] = fRadius * math.sin(i * fAngle)
            self._pos[i] = tmp
            self._neighbourList[i] = 3

        # Add further rings
        iFirst = 1
        iLast = self._arch[1]
        for i in range(1, 3):
            iLastAdded = self.addRing(iFirst, iLast, self._arch[1])
            iFirst = iLast + 1
            iLast = iLastAdded

    _data = None
    _sigma = [None, None]
    _epsilon = [None, None]
    _learningSteps = None
    _arch = [None, None]
    _centroids = None
    _childs = None
    _rings = None
    _labels = None
    _pos = None
    _neighbourList = None
    _fSin = None
    _fCos = None
    _lbl = None


class pyH2SOMClassifier(pyH2SOM):
    def __init__(self, epsilon, sigma, learningSteps, arch):
        self._rings = []
        self._childs = dict()
        self._sigma = sigma
        self._epsilon = epsilon
        self._learningSteps = learningSteps
        self._arch = arch
        self._pos = numpy.zeros((self.numNodes(self._arch), 2))
        self.buildNetwork(self._arch)

    def fit(self, X, y, x):
        self._data = X
        self._labels = x
        self._centroids = numpy.zeros((self.numNodes(self._arch), X.shape[1]))
        self.cluster()
        self._lbl = numpy.zeros(self._centroids.shape[0])
        d2c = core.bmus(self._data, self._centroids)
        for i in range(self._centroids.shape[0]):
            mc = collections.Counter(y[d2c == i]).most_common(1)
            if mc:
                self._lbl[i] = mc[0][0]

    def predict(self, X):
        return self._lbl[core.bmus(X, self._centroids)]

    def get_params(self, deep=True):
        return {
            "epsilon": self._epsilon,
            "sigma": self._sigma,
            "learningSteps": self._learningSteps,
            "arch": self._arch,
            "labels": self._labels
        }

    def set_params(self, **parameters):
        self._epsilon = parameters['epsilon'
                                   ] if 'epsilon' in parameters else self._epsilon
        self._sigma = parameters['sigma'
                                 ] if 'sigma' in parameters else self._sigma
        self._learningSteps = parameters[
            'learningSteps'
        ] if 'learningSteps' in parameters else self._learningSteps
        self._arch = parameters['arch'] if 'arch' in parameters else self._arch
        self._labels = parameters['labels'
                                  ] if 'labels' in parameters else self._labels
        return self


class allDataAdaptiveH2SOM:
    def __init__(self, data, epsilon, sigma, learningSteps, rings, labels):
        self._data = data
        self._sigma = sigma
        self._epsilon = epsilon
        self._learningSteps = learningSteps
        self._mapWidth = math.acosh(
            1.0 + 2.0 *
            (math.sqrt(1.0 - 4.0 * math.pow(math.sin(math.pi / 10), 2.0)) *
             math.cos(2.0 * math.pi / 10) * math.sqrt(1.0 - 4.0 * math.pow(
                 math.sin(math.pi / 10), 2.0)) * math.cos(2.0 * math.pi / 10) +
             math.sqrt(1.0 - 4.0 * math.pow(math.sin(math.pi / 10), 2.0)) *
             math.cos(2.0 * math.pi / 10) * math.sqrt(1.0 - 4.0 * math.pow(
                 math.sin(math.pi / 10), 2.0)) * math.cos(2.0 * math.pi /
                                                          10)) /
            (1.0 -
             (math.sqrt(1.0 - 4.0 * math.pow(math.sin(math.pi / 10), 2.0)) *
              math.cos(2.0 * math.pi / 10) * math.sqrt(1.0 - 4.0 * math.pow(
                  math.sin(math.pi / 10), 2.0)) * math.cos(2.0 * math.pi / 10)
              + math.sqrt(1.0 - 4.0 * math.pow(math.sin(math.pi / 10), 2.0)) *
              math.cos(2.0 * math.pi / 10) * math.sqrt(1.0 - 4.0 * math.pow(
                  math.sin(math.pi / 10), 2.0)) * math.cos(2.0 * math.pi /
                                                           10))))
        self._centroids = numpy.zeros((1000, data.shape[1]))  # (self.numNodes([rings,10])
        self.buildNetwork(rings, 8)
        self._labels = labels

    def cluster(self):
        # set initial solution to mean of data
        initial = numpy.mean(self._data, axis=0)
        self._centroids[0] = initial
        for i in self._childs[0]:
            self._centroids[i] = self._centroids[0]
        curNode = 0

        # train each ring
        for ringIdx, ring in enumerate(self._rings):
            cursigma = self._sigma[0]  # TODO modify sigma for each ring
            sigStep = (cursigma - self._sigma[1]) / self._learningSteps

            curepsilon = self._epsilon[0] / (ringIdx + 1)
            epsStep = (curepsilon - self._epsilon[1]) / self._learningSteps
            core.learning(self._data, self._centroids, self._learningSteps,
                          self._mapWidth, ring[0], ring[1], cursigma, sigStep,
                          curepsilon, epsStep)

            # distmat=scipy.spatial.distance.cdist(self._data,self._centroids[ring[0]:ring[1]+1],'sqeuclidean')
            # idxs=numpy.array(map(numpy.argmin,distmat))+ring[0]

            distmat = scipy.spatial.distance.cdist(
                self._data, self._centroids[0:ring[1] + 1], 'sqeuclidean')
            idxs = numpy.array(map(numpy.argmin, distmat))

            # init centroids for next ring
            if self._rings.index(ring) != (len(self._rings) - 1):
                curNode = ring[1] + 1
                for j in range(ring[0], ring[1] + 1):
                    hist = scipy.stats.itemfreq(self._labels[idxs == j])[:, 1]
                    hist = (hist + 0.0) / sum(hist)
                    numNewNodes = sum(hist > 0.01)
                    if numNewNodes > 0:
                        curNode += numNewNodes
                        self._childs[j] = curNode + numpy.arange(numNewNodes)
                        self.subcluster(j, numpy.arange(
                            self._data.shape[0])[idxs == j], numNewNodes, 2)

                # set new Ring
                self._rings[ringIdx + 1] = [ring[1] + 1, curNode]
                # copy values for newNodes
                for i in range(ring[0], ring[1] + 1):
                    for child in self._childs[i]:
                        self._centroids[child] = self._centroids[i]

        # distmat=scipy.spatial.distance.cdist(self._data,self._centroids[0:self._rings[-1][1]+1],'sqeuclidean')
        # idxs=numpy.array(map(numpy.argmin,distmat))
        # whitelist=[]
        # for j in range(0,self._rings[-1][1]+1):
        #   hist=numpy.histogram(self._labels[idxs==j],[0,1,2,3,4,5,6,7,8,9,10])[0]
        #   hist=(hist+0.0)/sum(hist)
        #   if sum(hist>0.05)==1:
        #       whitelist.append(j)
        #
        # self._centroids=self._centroids[whitelist]

    def newNodes(self, arch):
        if arch[0] == 0:
            return 1
        if arch[0] == 1:
            return arch[1]
        if arch[0] == 2:
            return arch[1] * (arch[1] - 4)
        return self.newNodes([arch[0] - 1, arch[1]]) * (
            arch[1] - 4) - self.newNodes([arch[0] - 2, arch[1]])

    def numNodes(self, arch):
        if arch[0] == 0:
            return 1
        if arch[0] == 1:
            return arch[1] + 1
        return self.newNodes(arch) + self.numNodes([arch[0] - 1, arch[1]])

    def buildNetwork(self, rings, startNodes):
        self._rings.append([1, startNodes])
        for i in range(rings):
            self._rings.append([])
        self._childs[0] = range(1, startNodes + 1)

    _data = None
    _sigma = [None, None]
    _epsilon = [None, None]
    _learningSteps = None
    _arch = [None, None]
    _centroids = None
    _childs = dict()
    _rings = []
    _mapWidth = None
    _labels = None


class supervisedH2SOM:
    def __init__(self, data, epsilon, sigma, learningSteps, rings, labels):
        self._data = data
        self._sigma = sigma
        self._epsilon = epsilon
        self._learningSteps = learningSteps
        self._mapWidth = math.acosh(
            1.0 + 2.0 *
            (math.sqrt(1.0 - 4.0 * math.pow(math.sin(math.pi / 8), 2.0)) *
             math.cos(2.0 * math.pi / 8) * math.sqrt(1.0 - 4.0 * math.pow(
                 math.sin(math.pi / 8), 2.0)) * math.cos(2.0 * math.pi / 8) +
             math.sqrt(1.0 - 4.0 * math.pow(math.sin(math.pi / 8), 2.0)) *
             math.cos(2.0 * math.pi / 8) * math.sqrt(1.0 - 4.0 * math.pow(
                 math.sin(math.pi / 8), 2.0)) * math.cos(2.0 * math.pi / 8)) /
            (1.0 -
             (math.sqrt(1.0 - 4.0 * math.pow(math.sin(math.pi / 8), 2.0)) *
              math.cos(2.0 * math.pi / 8) * math.sqrt(1.0 - 4.0 * math.pow(
                  math.sin(math.pi / 8), 2.0)) * math.cos(2.0 * math.pi / 8) +
              math.sqrt(1.0 - 4.0 * math.pow(math.sin(math.pi / 8), 2.0)) *
              math.cos(2.0 * math.pi / 8) * math.sqrt(1.0 - 4.0 * math.pow(
                  math.sin(math.pi / 8), 2.0)) * math.cos(2.0 * math.pi / 8))))
        self._centroids = numpy.zeros((8 + 1, data.shape[1]))
        self.buildNetwork(8)
        self._maxRings = rings
        self._labels = labels

    def cluster(self):
        # set initial solution to mean of data
        initial = numpy.mean(self._data, axis=0)
        self._centroids[0] = initial
        for i in self._childs[0]:
            self._centroids[i] = self._centroids[0]

        # train each ring
        cursigma = self._sigma[0]  # TODO modify sigma for each ring
        sigStep = (cursigma - self._sigma[1]) / self._learningSteps

        curepsilon = self._epsilon[0]
        epsStep = (curepsilon - self._epsilon[1]) / self._learningSteps

        # for i in range(ring[0],ring[1]):
        core.learning(self._data, self._centroids, self._learningSteps,
                      self._mapWidth, self._rings[0][0], self._rings[0][1],
                      cursigma, sigStep, curepsilon, epsStep)
        distmat = scipy.spatial.distance.cdist(
            self._data,
            self._centroids[self._rings[0][0]:self._rings[0][1] + 1],
            'sqeuclidean')
        idxs = numpy.array(map(numpy.argmin, distmat)) + 1

        for j in range(self._rings[0][0], self._rings[0][1] + 1):
            hist = scipy.stats.itemfreq(self._labels[idxs == j])[:, 1]
            # hist=numpy.histogram(self._labels[idxs==j],[0,1,2,3,4,5,6,7,8,9,10])[0]
            hist = (hist + 0.0) / sum(hist)
            numNewNodes = sum(hist > 0.01)
            if numNewNodes > 0:
                self.subcluster(j, numpy.arange(
                    self._data.shape[0])[idxs == j], numNewNodes, 2)

    def subcluster(self, originID, dataSelect, numNewNodes, ring):
        if numNewNodes == 0:
            return
        if ring <= self._maxRings:
            tempCentroids = numpy.zeros(
                (numNewNodes, self._centroids.shape[1]))
            cursigma = numNewNodes  # TODO modify sigma for each ring
            sigStep = (cursigma - self._sigma[1]) / (50 * dataSelect.shape[0])

            curepsilon = self._epsilon[0] / (ring * ring)
            epsStep = (curepsilon - self._epsilon[1]) / (50 *
                                                         dataSelect.shape[0])
            core.learning(numpy.require(self._data[dataSelect],
                                        requirements='C'), tempCentroids, 50 *
                          dataSelect.shape[0], 1, 0, numNewNodes - 1, cursigma,
                          sigStep, curepsilon, epsStep)

            # fill child array
            self._childs[originID] = (self._centroids.shape[0] + 1
                                      ) + numpy.arange(numNewNodes)
            # add Centroids
            self._centroids = numpy.vstack((self._centroids, tempCentroids))

            # compute bmus with corresponding dists
            distmat = scipy.spatial.distance.cdist(
                self._data[dataSelect], tempCentroids, 'sqeuclidean')
            # get idxs of best match
            idxs = numpy.array(map(numpy.argmin, distmat))
            for j in range(numNewNodes):
                # hist=numpy.histogram(self._labels[idxs==j],[0,1,2,3,4,5,6,7,8,9,10])[0]
                tmp = self._labels[idxs == j]
                hist = 0.0
                if tmp.shape[0] != 0:
                    hist = scipy.stats.itemfreq(tmp)[:, 1]
                    hist = (hist + 0.0) / sum(hist)
                    numNewNodes = sum(hist > 0.15)
                    if max(hist) < 0.5:
                        numNewNodes = 2

                    if numNewNodes > 1:
                        self.subcluster(self._childs[originID][j],
                                        dataSelect[idxs ==
                                                   j], numNewNodes, ring + 1)

    def newNodes(self, arch):
        if arch[0] == 0:
            return 1
        if arch[0] == 1:
            return arch[1]
        if arch[0] == 2:
            return arch[1] * (arch[1] - 4)
        return self.newNodes([arch[0] - 1, arch[1]]) * (
            arch[1] - 4) - self.newNodes([arch[0] - 2, arch[1]])

    def numNodes(self, arch):
        if arch[0] == 0:
            return 1
        if arch[0] == 1:
            return arch[1] + 1
        return self.newNodes(arch) + self.numNodes([arch[0] - 1, arch[1]])

    def buildNetwork(self, maxNodes):
        self._rings.append([1, 1 + self.newNodes([1, maxNodes]) - 1])
        self._childs[0] = range(1, maxNodes + 1)

    _data = None
    _sigma = [None, None]
    _epsilon = [None, None]
    _learningSteps = None
    _centroids = None
    _childs = dict()
    _rings = []
    _mapWidth = None
    _maxRings = None


class NODEH2SOM:
    def __init__(self, data, epsilon, sigma, learningSteps, rings, minNodes,
                 maxNodes,
                 minBorder=0.1,
                 maxBorder=2.0):
        self._data = data
        self._sigma = sigma
        self._epsilon = epsilon
        self._learningSteps = learningSteps
        self._mapWidth = math.acosh(
            1.0 + 2.0 *
            (math.sqrt(1.0 - 4.0 * math.pow(math.sin(math.pi / maxNodes), 2.0))
             * math.cos(2.0 * math.pi / maxNodes) * math.sqrt(
                 1.0 - 4.0 * math.pow(math.sin(math.pi / maxNodes), 2.0)) *
             math.cos(2.0 * math.pi / maxNodes) + math.sqrt(
                 1.0 - 4.0 * math.pow(math.sin(math.pi / maxNodes), 2.0)) *
             math.cos(2.0 * math.pi / maxNodes) * math.sqrt(
                 1.0 - 4.0 * math.pow(math.sin(math.pi / maxNodes), 2.0)) *
             math.cos(2.0 * math.pi / maxNodes)) /
            (1.0 -
             (math.sqrt(1.0 - 4.0 * math.pow(math.sin(math.pi / maxNodes),
                                             2.0)) *
              math.cos(2.0 * math.pi / maxNodes) * math.sqrt(
                  1.0 - 4.0 * math.pow(math.sin(math.pi / maxNodes), 2.0)) *
              math.cos(2.0 * math.pi / maxNodes) + math.sqrt(
                  1.0 - 4.0 * math.pow(math.sin(math.pi / maxNodes), 2.0)) *
              math.cos(2.0 * math.pi / maxNodes) * math.sqrt(
                  1.0 - 4.0 * math.pow(math.sin(math.pi / maxNodes), 2.0)) *
              math.cos(2.0 * math.pi / maxNodes))))
        self._centroids = numpy.zeros((maxNodes + 1, data.shape[1]))
        self._nodes = numpy.zeros(self.numNodes(
            [rings, maxNodes]), numpy.dtype([('left', numpy.int),
                                             ('leftWeight', numpy.float64),
                                             ('right', numpy.int),
                                             ('rightWeight', numpy.float64)]))
        self.buildNetwork(maxNodes)
        self._minNodes = minNodes
        self._maxNodes = maxNodes
        self._curNode = maxNodes + 1
        self._minBorder = minBorder
        self._maxBorder = maxBorder
        self._maxRings = rings

    def cluster(self):
        # set initial solution to mean of data
        initial = numpy.mean(self._data, axis=0)
        self._centroids[0] = initial
        for i in self._childs[0]:
            self._centroids[i] = self._centroids[0]

        # train each ring
        cursigma = self._sigma[0]  # TODO modify sigma for each ring
        sigStep = (cursigma - self._sigma[1]) / self._learningSteps

        curepsilon = self._epsilon[0]
        epsStep = (curepsilon - self._epsilon[1]) / self._learningSteps

        # for i in range(ring[0],ring[1]):
        core.NODElearning(self._data, self._centroids, self._learningSteps,
                          self._mapWidth, self._rings[0][0], self._rings[0][1],
                          cursigma, sigStep, curepsilon, epsStep, self._nodes)
        distmat = scipy.spatial.distance.cdist(
            self._data,
            self._centroids[self._rings[0][0]:self._rings[0][1] + 1],
            'sqeuclidean')
        idxs = numpy.array(map(numpy.argmin, distmat)) + 1
        stress = numpy.zeros(self._rings[0][1] - self._rings[0][0] + 1)
        for j in range(self._rings[0][0], self._rings[0][1] + 1):
            stress[j - 1] = sum(distmat[idxs == j][:, j - 1])  # /sum(idxs==j)

        avgstress = numpy.median(stress)
        for j in range(self._rings[0][0], self._rings[0][1] + 1):
            numNewNodes = int(((stress[j - 1] / avgstress) - self._minBorder) /
                              (self._maxBorder - self._minBorder) *
                              (self._maxNodes - self._minNodes))
            if (stress[j - 1] / avgstress) < self._minBorder:
                numNewNodes = self._minNodes
            elif (stress[j - 1] / avgstress) > self._maxBorder:
                numNewNodes = self._maxNodes
            self.subcluster(j, numpy.arange(self._data.shape[0])[idxs == j],
                            numNewNodes, 2)

    def subcluster(self, originID, dataSelect, numNewNodes, ring):
        if numNewNodes == 0:
            return
        if ring <= self._maxRings:
            # create Centroids
            tempCentroids = numpy.require(numpy.repeat(
                self._centroids[originID], numNewNodes).reshape(
                    numNewNodes, self._centroids.shape[1]),
                requirements='C')
            # tempCentroids=numpy.zeros((numNewNodes,self._centroids.shape[1]))
            cursigma = numNewNodes  # TODO modify sigma for each ring
            sigStep = (cursigma - self._sigma[1]) / (50 * dataSelect.shape[0])

            curepsilon = self._epsilon[0]
            epsStep = (curepsilon - self._epsilon[1]) / (50 *
                                                         dataSelect.shape[0])
            core.learning(numpy.require(self._data[dataSelect],
                                        requirements='C'), tempCentroids, 50 *
                          dataSelect.shape[0], 1, 0, numNewNodes - 1, cursigma,
                          sigStep, curepsilon, epsStep)

            # fill child array
            self._childs[originID] = (self._centroids.shape[0]
                                      ) + numpy.arange(numNewNodes)

            # add Centroids
            self._centroids = numpy.vstack((self._centroids, tempCentroids))

            # compute bmus with corresponding dists
            distmat = scipy.spatial.distance.cdist(
                self._data[dataSelect], tempCentroids, 'sqeuclidean')
            # get idxs of best match
            idxs = numpy.array(map(numpy.argmin, distmat))
            # create stress array
            stress = numpy.zeros(numNewNodes)
            # fill stress array
            for j in range(numNewNodes):
                stress[j] = sum(distmat[idxs == j][:, j])  # /sum(idxs==j)

            # compute average stress
            avgstress = numpy.median(stress)
            if avgstress:
                for j in range(numNewNodes):
                    # compute number of new Nodes
                    numNewNodes = int((
                        (stress[j - 1] / avgstress) - self._minBorder) /
                        (self._maxBorder - self._minBorder) *
                        (self._maxNodes - self._minNodes))
                    if (stress[j - 1] / avgstress) < self._minBorder:
                        numNewNodes = self._minNodes
                    elif (stress[j - 1] / avgstress) > self._maxBorder:
                        numNewNodes = self._maxNodes
                    # recursively cluster other rings
                    self.subcluster(self._childs[originID][j],
                                    dataSelect[idxs ==
                                               j], numNewNodes, ring + 1)

    def newNodes(self, arch):
        if arch[0] == 0:
            return 1
        if arch[0] == 1:
            return arch[1]
        if arch[0] == 2:
            return arch[1] * (arch[1] - 4)
        return self.newNodes([arch[0] - 1, arch[1]]) * (
            arch[1] - 4) - self.newNodes([arch[0] - 2, arch[1]])

    def numNodes(self, arch):
        if arch[0] == 0:
            return 1
        if arch[0] == 1:
            return arch[1] + 1
        return self.newNodes(arch) + self.numNodes([arch[0] - 1, arch[1]])

    def buildNetwork(self, maxNodes):
        self._rings.append([1, 1 + self.newNodes([1, maxNodes]) - 1])
        self._childs[0] = range(1, maxNodes + 1)

        # init nodes for first ring
        for i in range(self._rings[0][0], self._rings[0][1]):
            self._nodes[i]['left'] = i - 1
            self._nodes[i]['right'] = i + 1
            self._nodes[i]['leftWeight'] = 1.0
            self._nodes[i]['rightWeight'] = 1.0
        self._nodes[self._rings[0][0]]['left'] = self._rings[0][1]
        self._nodes[self._rings[0][1]]['right'] = self._rings[0][0]

    _data = None
    _sigma = [None, None]
    _epsilon = [None, None]
    _learningSteps = None
    _centroids = None
    _childs = dict()
    _rings = []
    _mapWidth = None
    _nodes = None
    _maxRings = None
    _minNodes = None
    _maxNodes = None
    _curNode = None
    _minBorder = None
    _maxBorder = None
    _maxRings = None


class errH2SOM:
    def __init__(self, data, epsilon, sigma, learningSteps, arch):
        self._data = data
        self._sigma = sigma
        self._rings = []
        self._childs = dict()
        self._epsilon = epsilon
        self._learningSteps = learningSteps
        self._arch = arch
        self._mapWidth = math.acosh(
            1.0 + 2.0 *
            (math.sqrt(1.0 - 4.0 * math.pow(math.sin(math.pi / arch[1]), 2.0))
             * math.cos(2.0 * math.pi / arch[1]) * math.sqrt(
                 1.0 - 4.0 * math.pow(math.sin(math.pi / arch[1]), 2.0)) *
             math.cos(2.0 * math.pi / arch[1]) + math.sqrt(
                 1.0 - 4.0 * math.pow(math.sin(math.pi / arch[1]), 2.0)) *
             math.cos(2.0 * math.pi / arch[1]) * math.sqrt(
                 1.0 - 4.0 * math.pow(math.sin(math.pi / arch[1]), 2.0)) *
             math.cos(2.0 * math.pi / arch[1])) /
            (1.0 -
             (math.sqrt(1.0 - 4.0 * math.pow(math.sin(math.pi / arch[1]), 2.0))
              * math.cos(2.0 * math.pi / arch[1]) * math.sqrt(
                  1.0 - 4.0 * math.pow(math.sin(math.pi / arch[1]), 2.0)) *
              math.cos(2.0 * math.pi / arch[1]) + math.sqrt(
                  1.0 - 4.0 * math.pow(math.sin(math.pi / arch[1]), 2.0)) *
              math.cos(2.0 * math.pi / arch[1]) * math.sqrt(
                  1.0 - 4.0 * math.pow(math.sin(math.pi / arch[1]), 2.0)) *
              math.cos(2.0 * math.pi / arch[1]))))
        self._centroids = numpy.zeros((self.numNodes(arch), data.shape[1]))
        self._err = numpy.zeros(self.numNodes(arch))
        self._mqe = numpy.zeros(self.numNodes(arch))
        self._var = numpy.zeros(self.numNodes(arch))
        self.buildNetwork(self._arch)

    def cluster(self):
        # set initial solution to mean of data
        initial = numpy.mean(self._data, axis=0)
        self._centroids[0] = initial
        for i in self._childs[0]:
            self._centroids[i] = self._centroids[0]

        # train each ring
        for ringIdx, ring in enumerate(self._rings):
            cursigma = self._sigma[0]  # TODO modify sigma for each ring
            sigStep = (cursigma - self._sigma[1]) / self._learningSteps

            curepsilon = self._epsilon[0]
            epsStep = (curepsilon - self._epsilon[1]) / self._learningSteps
            core.ERRlearning(self._data, self._centroids, self._err,
                             self._learningSteps, self._mapWidth, ring[0],
                             ring[1], cursigma, sigStep, curepsilon, epsStep)

            idxs = ring[0] + core.bmus(self._data,
                                       self._centroids[ring[0]:ring[1] + 1])
            for i in range(ring[0], ring[1] + 1):
                if numpy.any(idxs == i):
                    self._var[i] = numpy.var(self._data[idxs == i])
                    self._mqe[i] = numpy.average(scipy.spatial.distance.cdist(
                        self._centroids[i].reshape(self._centroids[i].shape[0],
                                                   1).T, self._data[idxs == i],
                        'sqeuclidean'))
                else:
                    self._var[i] = 0
                    self._mqe[i] = 0

            # init centroids for next ring
            if self._rings.index(ring) != (len(self._rings) - 1):
                for i in range(ring[0], ring[1] + 1):
                    for child in self._childs[i]:
                        self._centroids[child] = self._centroids[i]

    def newNodes(self, arch):
        if arch[0] == 0:
            return 1
        if arch[0] == 1:
            return arch[1]
        if arch[0] == 2:
            return arch[1] * (arch[1] - 4)
        return self.newNodes([arch[0] - 1, arch[1]]) * (
            arch[1] - 4) - self.newNodes([arch[0] - 2, arch[1]])

    def numNodes(self, arch):
        if arch[0] == 0:
            return 1
        if arch[0] == 1:
            return arch[1] + 1
        return self.newNodes(arch) + self.numNodes([arch[0] - 1, arch[1]])

    def buildNetwork(self, arch):
        for ring in range(1, self._arch[0] + 1):
            self._rings.append([self.numNodes([ring - 1, arch[1]
                                               ]), self.numNodes([ring - 1, arch[1]]) +
                                self.newNodes([ring, arch[1]]) - 1])

        self._childs[0] = range(1, arch[1] + 1)
        cur = arch[1] + 1
        marker = arch[1]
        doubles = []
        for i in range(1, self.numNodes([arch[0] - 1, arch[1]])):
            if i == marker:
                self._childs[i] = [marker + 1] + range(cur, cur +
                                                       (arch[1] - 4))
                doubles += [marker + 1]
                marker = cur + (arch[1] - 5)
                cur += (arch[1] - 4)
            elif i in doubles:
                self._childs[i] = range(cur, cur + (arch[1] - 4))
                doubles += [cur + (arch[1] - 5)]
                cur += (arch[1] - 5)
            else:
                self._childs[i] = range(cur, cur + (arch[1] - 3))
                cur += (arch[1] - 4)
                doubles += [cur]

    _data = None
    _sigma = [None, None]
    _epsilon = [None, None]
    _learningSteps = None
    _arch = [None, None]
    _centroids = None
    _childs = None
    _rings = None
    _mapWidth = None
    _globalSearch = None
    _swidth = None
    _err = None


class SOM:
    def __init__(self, data, epsilon, sigma, learningSteps, arch):
        self._data = data
        self._sigma = sigma
        self._epsilon = epsilon
        self._learningSteps = learningSteps
        self._arch = arch
        self._centroids = numpy.zeros((arch[0] * arch[1], data.shape[1]))

    def fit(self, X, y):
        self.__init__(X, self._epsilon, self._sigma, self._learningSteps,
                      self._arch)
        self.cluster()
        self._lbl = numpy.zeros(self._centroids.shape[0])
        d2c = core.bmus(self._data, self._centroids)
        for i in range(self._centroids.shape[0]):
            mc = collections.Counter(y[d2c == i]).most_common(1)
            if mc:
                self._lbl[i] = mc[0][0]

    def predict(self, X):
        return self._lbl[core.bmus(X, self._centroids)]

    def dumpParameters(self):
        print('Architecture\t', self._arch)
        print('Sigma\t\t', self._sigma)
        print('Epsilon\t\t', self._epsilon)
        print('learningSteps\t', self._learningSteps)

    def cluster(self):
        core.som_learning(self._data, self._centroids, self._learningSteps,
                          self._arch[0], self._arch[1], self._sigma[0],
                          self._sigma[1], self._epsilon[0], self._epsilon[1])

    _data = None
    _sigma = [None, None]
    _epsilon = [None, None]
    _learningSteps = None
    _arch = [None, None]
    _centroids = None
    _lbl = None


class Kmeans:
    def __init__(self, k):
        self._k = k

    def fit(self, X, y):
        self._centroids = X[numpy.random.randint(0, X.shape[0], self._k)]
        self.cluster(X)
        self._lbl = numpy.zeros(self._centroids.shape[0])
        d2c = core.bmus(X, self._centroids)
        for i in range(self._centroids.shape[0]):
            mc = collections.Counter(y[d2c == i]).most_common(1)
            if mc:
                self._lbl[i] = mc[0][0]

    def predict(self, X):
        return self._lbl[core.bmus(X, self._centroids)]

    def dumpParameters(self):
        print('k\t\t\t', self._k)

    def cluster(self, X):
        core.kmeans_learning(X, self._centroids, self._k)

    _centroids = None
    _k = None
    _lbl = None


class NeuralGas:
    def __init__(self, data, k, learningSteps, lam, epsilon):
        self._data = data
        self._centroids = data[numpy.random.randint(0, data.shape[0], k)]
        self._k = k
        self._learningSteps = learningSteps
        self._lambda = lam
        self._epsilon = epsilon

    def fit(self, X, y):
        self.__init__(X, self._k, self._learningSteps, self._lambda,
                      self._epsilon)
        self.cluster()
        self._lbl = numpy.zeros(self._centroids.shape[0])
        d2c = core.bmus(self._data, self._centroids)
        for i in range(self._centroids.shape[0]):
            mc = collections.Counter(y[d2c == i]).most_common(1)
            if mc:
                self._lbl[i] = mc[0][0]

    def predict(self, X):
        return self._lbl[core.bmus(X, self._centroids)]

    def dumpParameters(self):
        print('k\t\t\t', self._k)
        print('Lambda\t\t', self._lambda)
        print('Epsilon\t\t', self._epsilon)
        print('learningSteps\t', self._learningSteps)

    def cluster(self):
        self._centroids = self._data[numpy.random.randint(
            0, self._data.shape[0], self._k)]
        curlambda = self._lambda[0]
        lamStep = (curlambda - self._lambda[1]) / self._learningSteps
        curepsilon = self._epsilon[0]
        epsStep = (curepsilon - self._epsilon[1]) / self._learningSteps
        core.ng_learning(self._data, self._centroids, self._k,
                         self._learningSteps, curlambda, lamStep, curepsilon,
                         epsStep)

    _data = None
    _centroids = None
    _k = None
    _learningSteps = None
    _lambda = [None, None]
    _epsilon = [None, None]
    _lbl = None


class awH2SOM:
    def __init__(self, data, epsilon, sigma, learningSteps, arch):
        if arch[0] < 2:
            print('Please choose the number of rings to be greater than 1.')
            exit(-1)
        self._data = data
        self._sigma = sigma
        self._epsilon = epsilon
        self._learningSteps = learningSteps
        self._arch = arch
        self.buildNetwork(self._arch)
        self._mapWidth = math.acosh(
            1.0 + 2.0 *
            (math.sqrt(1.0 - 4.0 * math.pow(math.sin(math.pi / arch[1]), 2.0))
             * math.cos(2.0 * math.pi / arch[1]) * math.sqrt(
                 1.0 - 4.0 * math.pow(math.sin(math.pi / arch[1]), 2.0)) *
             math.cos(2.0 * math.pi / arch[1]) + math.sqrt(
                 1.0 - 4.0 * math.pow(math.sin(math.pi / arch[1]), 2.0)) *
             math.cos(2.0 * math.pi / arch[1]) * math.sqrt(
                 1.0 - 4.0 * math.pow(math.sin(math.pi / arch[1]), 2.0)) *
             math.cos(2.0 * math.pi / arch[1])) /
            (1.0 -
             (math.sqrt(1.0 - 4.0 * math.pow(math.sin(math.pi / arch[1]), 2.0))
              * math.cos(2.0 * math.pi / arch[1]) * math.sqrt(
                  1.0 - 4.0 * math.pow(math.sin(math.pi / arch[1]), 2.0)) *
              math.cos(2.0 * math.pi / arch[1]) + math.sqrt(
                  1.0 - 4.0 * math.pow(math.sin(math.pi / arch[1]), 2.0)) *
              math.cos(2.0 * math.pi / arch[1]) * math.sqrt(
                  1.0 - 4.0 * math.pow(math.sin(math.pi / arch[1]), 2.0)) *
              math.cos(2.0 * math.pi / arch[1]))))
        self._centroids = numpy.zeros((self.numNodes(arch), data.shape[1]))

    def cluster(self):
        # set initial solution to mean of data
        initial = numpy.mean(self._data, axis=0)
        self._centroids[0] = initial
        for i in self._childs[0]:
            self._centroids[i] = self._centroids[0]

        # train each ring
        for ringIdx, ring in enumerate(self._rings):
            print('ringIdx', ringIdx, ring)
            cursigma = self._sigma[0]
            sigStep = (cursigma - self._sigma[1]) / self._learningSteps

            curepsilon = self._epsilon[0]
            epsStep = (curepsilon - self._epsilon[1]) / self._learningSteps

            core.learning(self._data, self._centroids, self._learningSteps,
                          self._mapWidth, ring[0], ring[1], cursigma, sigStep,
                          curepsilon, epsStep)

            # for i in range(self._learningSteps):
            #   sig=self._data[numpy.random.randint(0,self._data.shape[0])]
            #   bmu=ring[0]+core.bmu(sig,self._centroids[ring[0]:ring[1]+1])
            #   core.adapt(sig,self._centroids,self._mapWidth,bmu,ring[0],ring[1]-1,cursigma,curepsilon)
            #   cursigma-=sigStep
            #   curepsilon-=epsStep

            # init centroids for next ring
            if self._rings.index(ring) != (len(self._rings) - 1):
                for i in range(ring[0], ring[1] + 1):
                    for child in self._childs[i]:
                        self._centroids[child] = self._centroids[i]

        for i in range(len(self._centroids)):
            self._centroid2data[i] = []
        for idx, data in enumerate(self._data):
            self._centroid2data[core.bmu(data, self._centroids)].append(idx)
        for i in range(ring[0], ring[1]):
            tmp = self.subcluster(i)
            if tmp is not None:
                self._centroids = numpy.vstack((self._centroids, tmp))

    # def subcluster(self,root):
    #   #evaluate cluster size
    #   if len(self._centroid2data[root])>50:
    #       numNewNodes=2*math.log(len(self._centroid2data[root]))
    #       print root,numpy.std(self._data[self._centroid2data[root]]),numpy.var(self._data[self._centroid2data[root]]),len(self._centroid2data[root]),numpy.var(self._data[self._centroid2data[root]])/len(self._centroid2data[root])
    #       numNewNodes=numpy.var(self._data[self._centroid2data[root]])/len(self._centroid2data[root])
    #
    #       #build data matrix
    #       localdata=self._data[self._centroid2data[root]]
    #       # numNewNodes=10
    #       # localdata=numpy.random.rand(1000,768)
    #       km=Kmeans(localdata,3)
    #       km.cluster()
    #       return km._centroids
    #   return None

    def subcluster(self, root):
        # evaluate cluster size
        if len(self._centroid2data[root]) > 50:
            # build data matrix
            localdata = self._data[self._centroid2data[root]]
            # numNewNodes=10
            # localdata=numpy.random.rand(1000,768)

            numNodes = None
            cMax = 0.0
            for i in range(2, 50):
                km = Kmeans(localdata, i)
                km.cluster()

                lcentroid2data = dict()
                for j in range(len(km._centroids)):
                    lcentroid2data[j] = []
                for idx, j in enumerate(km._data):
                    bmu = core.bmu(j, km._centroids)
                    lcentroid2data[bmu].append(idx)

                cIndex = clusterValidation.calinskiHarabaszIndex(
                    self._data, lcentroid2data)
                if cIndex > cMax:
                    cMax = cIndex
                    numNodes = i
            if numNodes != 2:
                km = Kmeans(localdata, numNodes)
                km.cluster()
                return km._centroids
        return None

    def newNodes(self, arch):
        if arch[0] == 0:
            return 1
        if arch[0] == 1:
            return arch[1]
        if arch[0] == 2:
            return arch[1] * (arch[1] - 4)
        return self.newNodes([arch[0] - 1, arch[1]]) * (
            arch[1] - 4) - self.newNodes([arch[0] - 2, arch[1]])

    def numNodes(self, arch):
        if arch[0] == 0:
            return 1
        if arch[0] == 1:
            return arch[1] + 1
        return self.newNodes(arch) + self.numNodes([arch[0] - 1, arch[1]])

    def buildNetwork(self, arch):
        for ring in range(1, self._arch[0] + 1):
            self._rings.append([self.numNodes([ring - 1, arch[1]
                                               ]), self.numNodes([ring - 1, arch[1]]) +
                                self.newNodes([ring, arch[1]]) - 1])

        self._childs[0] = range(1, arch[1] + 1)
        cur = arch[1] + 1
        marker = arch[1]
        doubles = []
        for i in range(1, self.numNodes([arch[0] - 1, arch[1]])):
            if i == marker:
                self._childs[i] = [marker + 1] + range(cur, cur +
                                                       (arch[1] - 4))
                doubles += [marker + 1]
                marker = cur + (arch[1] - 5)
                cur += (arch[1] - 4)
            elif i in doubles:
                self._childs[i] = range(cur, cur + (arch[1] - 4))
                doubles += [cur + (arch[1] - 5)]
                cur += (arch[1] - 5)
            else:
                self._childs[i] = range(cur, cur + (arch[1] - 3))
                cur += (arch[1] - 4)
                doubles += [cur]

    _data = None
    _sigma = [None, None]
    _epsilon = [None, None]
    _learningSteps = None
    _arch = [None, None]
    _centroids = None
    _childs = dict()
    _rings = []
    _mapWidth = None
    _centroid2data = dict()
    _subnodes = []


class RareEventClassifier(BaseEstimator, ClassifierMixin):

    def __init__(self, dictsize=1000, dim=64, numNearestNeighbors=256, n_iter=10):
        self.K = numpy.random.rand(dictsize, dim)
        self.V = numpy.zeros(dictsize, numpy.int)
        self.A = numpy.ones(dictsize, numpy.int) * 10**12
        self.n_iter = n_iter
        self.numNearestNeighbors = numNearestNeighbors
        self.onn = sklearn.neighbors.NearestNeighbors(1, n_jobs=1, metric='cosine', algorithm='brute')

    def fit(self, X, y):
        X = sklearn.preprocessing.normalize(X)
        for i in range(int(self.n_iter * y.shape[0])):
            signal = numpy.random.randint(0, y.shape[0])
            q = X[signal].reshape(1, -1)
            v = y[signal]
            dists = scipy.spatial.distance.cdist(q, self.K, metric='cosine').flatten()
            idxs = numpy.argsort(dists[0:self.numNearestNeighbors])
            if numpy.all(self.V[idxs[0]] == v):  # check that
                self.K[idxs[0]] = (q + self.K[idxs[0]]) / numpy.linalg.norm(q + self.K[idxs[0]])
                self.A[idxs[0]] = 0
            else:
                # paper implements a random age old A
                nprime = numpy.argmax(self.A)
                self.K[nprime] = q
                self.V[nprime] = v
                self.A[nprime] = 0
        return self

    def predict(self, X):
        X = sklearn.preprocessing.normalize(X)
        self.onn.fit(self.K)
        _, idxs = self.onn.kneighbors(X)
        return self.V[idxs].flatten()

    # def predict_proba(self, X):
    #     self.onn.fit(K)
    #     dists, idxs = self.onn.kneighbors(X)
    #     confidence = sklearn.utils.extmath.softmax(dists * t)
    #     return V[idxs], confidence


class MemH2SOL(H2SOMClassifierLLM):

    def fit(self, X, y):
        self._rec = RareEventClassifier(dim=X.shape[1] * 2)
        X = sklearn.preprocessing.normalize(X)
        self._setup(X, y)
        self.cluster()
        cents = sklearn.preprocessing.normalize(self._centroids)
        # diff of X to cents
        d2c = core.bmus(X, cents)
        Xprime = (X - cents[d2c])
        # gradient of loss could also be used
        feats = numpy.hstack((Xprime, cents[d2c]))
        self._rec.fit(feats, y)
        self._rec.onn.fit(self._rec.K)
        _, idxs = self._rec.onn.kneighbors(feats)
        self.pfeats = numpy.hstack((cents[d2c], self._rec.K[idxs].reshape(-1, X.shape[1] * 2)))
        self._data = self.pfeats
        self._setup(self._data, y)
        self.cluster()
        self._training(y)
        return self

    def predict(self, X):
        X = sklearn.preprocessing.normalize(X)
        cents = numpy.require(sklearn.preprocessing.normalize(self._centroids)[:, :X.shape[1]], requirements='C')
        # diff of X to cents
        d2c = core.bmus(X, cents)
        Xprime = (X - cents[d2c])
        feats = numpy.hstack((Xprime, cents[d2c]))
        _, idxs = self._rec.onn.kneighbors(feats)
        X = numpy.hstack((X, self._rec.K[idxs].reshape(-1, X.shape[1] * 2)))
        return H2SOMClassifierLLM.predict(self, X)
