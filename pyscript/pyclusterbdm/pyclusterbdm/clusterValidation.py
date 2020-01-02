import scipy
import scipy.spatial
import numpy
import sys
import core
import math
import sklearn.utils.multiclass
import sklearn.metrics

# Sources:
#           cmartin: Visual data mining in intrinsic hierarchical complex biodata, C.Martin 2009
#           jherold: A data mining approach for high-content fluorescence microscopy images of tissue samples, J.Herold 2010
#           prousse: Silhouettes: A graphical aid to the interpretation and validation of cluster analysis, P Rousseeuw 1987
#           and respective original papers


# cmartin
def __intraClusterHelper(data, clusterIdxMap):
    intraVariance = 0.0
    for i in clusterIdxMap:
        if len(clusterIdxMap[i]):
            avg = numpy.mean(data[clusterIdxMap[i]], 0)
            intraVariance += numpy.sum(scipy.spatial.distance.cdist(
                data[clusterIdxMap[i]], avg.reshape(avg.shape[0], 1).T,
                metric='sqeuclidean'))
    return intraVariance


# cmartin
def __interClusterHelper(data, clusterIdxMap):
    interVariance = 0.0
    wholeaverage = numpy.mean(data, 0)
    for i in clusterIdxMap:
        if len(clusterIdxMap[i]):
            avg = numpy.mean(data[clusterIdxMap[i]], 0)
            interVariance += len(
                clusterIdxMap[i]) * scipy.spatial.distance.sqeuclidean(
                    avg, wholeaverage)
    return interVariance


# cmartin
# maximize  #valid
def ratio(data, clusterIdxMap):
    return (__interClusterHelper(data, clusterIdxMap) / len(clusterIdxMap)) / (
        __intraClusterHelper(data, clusterIdxMap) / data.shape[0])


# jherold
# maximize  #valid
def calinskiHarabaszIndex(data, clusterIdxMap):
    return (__interClusterHelper(data, clusterIdxMap) / (
        len(clusterIdxMap) - 1)) / (__intraClusterHelper(data, clusterIdxMap) /
                                    (data.shape[0] - len(clusterIdxMap)))


# jherold
# maximize
def indexI(data, clusterIdxMap, p=1):
    wholeaverage = numpy.mean(data, 0)
    avgs = numpy.zeros((len(clusterIdxMap), data.shape[1]))
    for idx, i in enumerate(clusterIdxMap):
        avgs[idx] = numpy.mean(data[clusterIdxMap[i]], 0)
    dk = max(scipy.spatial.distance.pdist(avgs))
    ek = __intraClusterHelper(data, clusterIdxMap)
    e1 = numpy.sum(scipy.spatial.distance.cdist(wholeaverage.reshape(
        1, wholeaverage.shape[0]), data))
    return math.pow(e1 / ek * dk / len(clusterIdxMap), p)


# cmartin
# minimize
def seperation(data, clusterIdxMap):
    avgs = numpy.zeros((len(clusterIdxMap), data.shape[1]))
    for idx, i in enumerate(clusterIdxMap):
        avgs[idx] = numpy.mean(data[clusterIdxMap[i]], 0)
    seperation = 0.0
    normFactor = 0
    for idx1, i in enumerate(clusterIdxMap):
        for idx2, j in enumerate(clusterIdxMap):
            if (idx1 != idx2):
                seperation += len(clusterIdxMap[i]) * len(
                    clusterIdxMap[j]) * scipy.spatial.distance.sqeuclidean(
                        avgs[idx1], avgs[idx2])
                normFactor += len(clusterIdxMap[i]) * len(clusterIdxMap[j])
    return seperation / normFactor


# prousse
#[-1,1] 1 is good -1 is bad         #valid
def silhouetteWidth(data, clusterIdxMap, avg=True):
    sws = core.silhouetteWidth(data, clusterIdxMap)
    if avg:
        return numpy.average(sws)
    else:
        return sws


# jherold
# minimize  #valid
def daviesBouldinIndex(data, clusterIdxMap):
    wcs = numpy.zeros(len(clusterIdxMap))
    rk = numpy.zeros(len(clusterIdxMap))

    avgs = numpy.zeros((len(clusterIdxMap), data.shape[1]))
    for idx, i in enumerate(clusterIdxMap):
        avgs[idx] = numpy.mean(data[clusterIdxMap[i]], 0)

    for i in clusterIdxMap:
        wcs[i] = numpy.sum(scipy.spatial.distance.cdist(avgs[i].reshape(
            1, avgs[i].shape[0]), data[clusterIdxMap[i]])) / len(
                clusterIdxMap[i])

    for i in clusterIdxMap:
        tmp = 0.0
        for j in clusterIdxMap:
            if i != j:
                tmp = max((wcs[i] + wcs[j]) / scipy.spatial.distance.euclidean(
                    avgs[i], avgs[j]), tmp)
        rk[i] = tmp
    return numpy.sum(rk) / len(clusterIdxMap)

    # jherold
    # maximize      #valid
def dunnIndex(data, clusterIdxMap):
    diam = numpy.zeros(len(clusterIdxMap))
    clusterdist = numpy.zeros((len(clusterIdxMap), len(clusterIdxMap)))
    for i in clusterIdxMap:
        diam[i] = numpy.max(scipy.spatial.distance.cdist(
            data[clusterIdxMap[i]], data[clusterIdxMap[i]]))
        for j in clusterIdxMap:
            clusterdist[i, j] = clusterdist[j, i] = numpy.min(
                scipy.spatial.distance.cdist(data[clusterIdxMap[i]],
                                             data[clusterIdxMap[j]]))
    clusterdist[numpy.diag_indices_from(clusterdist)] = sys.float_info.max
    return numpy.min(clusterdist / numpy.max(diam))


def confusion_matrix(y_true, y_pred, labels=None):
    if labels is None:
        labels = sklearn.utils.multiclass.unique_labels(y_true, y_pred)
    else:
        labels = numpy.asarray(labels)

    n_labels = labels.size
    label_to_ind = dict((y, x) for x, y in enumerate(labels))
    # convert yt, yp into index
    y_pred = numpy.array([label_to_ind.get(x, n_labels + 1) for x in y_pred])
    y_true = numpy.array([label_to_ind.get(x, n_labels + 1) for x in y_true])
    ind = numpy.logical_and(y_pred < n_labels, y_true < n_labels)
    y_pred = y_pred[ind]
    y_true = y_true[ind]
    CM = numpy.zeros((n_labels, n_labels), dtype="int")
    for i in range(len(y_pred)):
        CM[y_pred[i]][y_true[i]] += 1
    return CM, labels


def rejectionf1scorer(y, y_pred, **kwargs):
    r_pos = ~(numpy.array(y_pred) == -1)
    y_pred = numpy.array(y_pred)[r_pos]
    y_true = numpy.array(y)[r_pos]
    return sklearn.metrics.f1_score(y_true, y_pred, **kwargs)


def classification_report(y_true, y_pred, labels=None, target_names=None):
    r_pos = ~(numpy.array(y_pred) == -1)
    rsum = sum(~r_pos)
    y_pred = numpy.array(y_pred)[r_pos]
    y_true = numpy.array(y_true)[r_pos]

    if labels is None:
        labels = sklearn.utils.multiclass.unique_labels(y_true, y_pred)
    else:
        labels = numpy.asarray(labels)

    last_line_heading = 'weighted avg'
    very_last_line_heading = 'avg'
    very_very_last_line_heading = 'rejects'

    if target_names is None:
        width = len(last_line_heading)
        target_names = ['{0}'.format(l) for l in labels]
    else:
        width = max(len(cn) for cn in target_names)
        width = max(width, len(last_line_heading))

    headers = ["precision", "recall", "f1-score", "support"]
    fmt = '%% %ds' % width  # first column: class name
    fmt += '  '
    fmt += ' '.join(['% 9s' for _ in headers])
    fmt += '\n'

    headers = [""] + headers
    report = fmt % tuple(headers)
    report += '\n'

    p, r, f1, s = sklearn.metrics.precision_recall_fscore_support(
        y_true, y_pred,
        labels=labels,
        average=None)

    for i, label in enumerate(labels):
        values = [target_names[i]]
        for v in (p[i], r[i], f1[i]):
            values += ["{0:0.2f}".format(v)]
        values += ["{0}".format(s[i])]
        report += fmt % tuple(values)

    report += '\n'

    # compute averages
    values = [last_line_heading]
    for v in (numpy.average(p,
                            weights=s), numpy.average(r,
                                                      weights=s),
              numpy.average(f1,
                            weights=s)):
        values += ["{0:0.2f}".format(v)]
    values += ['{0}'.format(numpy.sum(s))]
    report += fmt % tuple(values)

    values = [very_last_line_heading]
    for v in (numpy.average(p), numpy.average(r), numpy.average(f1)):
        values += ["{0:0.2f}".format(v)]
    values += ['{0}'.format(numpy.sum(s))]
    report += fmt % tuple(values)

    values = [very_very_last_line_heading, "", "", "", "{0}".format(rsum)]
    report += fmt % tuple(values)

    return report
