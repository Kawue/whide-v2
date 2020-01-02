import numpy
import os
import gzip
import struct


def loadData(filename):
    fileName, fileExtension = os.path.splitext(filename)
    if fileExtension == '.npz':
        d = numpy.load(filename)
        return d['data'], d['output']
    if fileExtension == '.npy':
        with open(filename) as f:
            return numpy.load(f), numpy.load(f)
    if fileExtension == '.ml':
        return readML(filename)
    if fileExtension == '.mmz':
        return readMMZ(filename)
    return None, None


def loadMultiData(filenames, reportsizes=False):
    sizes = []
    if len(filenames):
        alldata, alllabels = loadData(filenames[0])
        for f in filenames[1:]:
            tmpdata, tmplabels = loadData(f)
            sizes.append(tmpdata.shape[0])
            alldata = numpy.vstack((alldata, tmpdata))
            alllabels = numpy.vstack((alllabels, tmplabels))
        if reportsizes:
            return alldata, alllabels, sizes
        else:
            return alldata, alllabels
    else:
        return None, None


def loadFolder(folder, reportsizes=False):
    filelist = []
    for file in os.listdir(folder):
        if file.endswith(".npy") or file.endswith('.npz') or file.endswith(
                '.ml') or file.endswith('.mmz'):
            filelist.append(folder + "/" + file)
    return loadMultiData(filelist, reportsizes)


def loadListDataofFolder(folder):
    filelist = []
    for file in os.listdir(folder):
        if file.endswith(".npy") or file.endswith('.npz'):
            filelist.append(folder + "/" + file)
    data = []
    labels = []
    for f in filelist:
        tmpdata, tmplabels = loadData(f)
        data.append(tmpdata)
        labels.append(tmplabels)
    return data, labels


def readMMZ(filename, reportsizes=False):
    dataType = {
        0: {"symbol": "d",
            "size": 8},
        1: {"symbol": "f",
            "size": 4},
        2: {"symbol": "i",
            "size": 4},
        3: {"symbol": "q",
            "size": 8}
    }
    f = gzip.open(filename, 'rb')
    bmaliType = f.read(1)
    struct.unpack("B", bmaliType)[0]
    bdataType = f.read(1)
    idataType = struct.unpack("B", bdataType)[0]

    bmaliType = f.read(1)
    struct.unpack("B", bmaliType)[0]
    bdataType = f.read(1)
    odataType = struct.unpack("B", bdataType)[0]

    bitems = f.read(8)
    items = struct.unpack("q", bitems)[0]
    bidim = f.read(8)
    idim = struct.unpack("q", bidim)[0]
    bodim = f.read(8)
    odim = struct.unpack("q", bodim)[0]

    inp = numpy.zeros((items, idim))
    outp = numpy.zeros((items, odim))

    for i in range(items):
        for j in range(idim):
            bItm = f.read(dataType[idataType]['size'])
            itm = struct.unpack(dataType[idataType]['symbol'], bItm)[0]
            inp[i, j] = itm
        for j in range(odim):
            bItm = f.read(dataType[odataType]['size'])
            itm = struct.unpack(dataType[odataType]['symbol'], bItm)[0]
            outp[i, j] = itm
    f.close()
    if reportsizes:
        return inp, outp, items
    return inp, outp


def readML(filename, reportsizes=False):
    f = gzip.open(filename, 'rb')

    bBuff = f.read(4)
    iBuff = struct.unpack("i", bBuff)[0]
    f.read(iBuff)

    bitems = f.read(4)
    items = struct.unpack("i", bitems)[0]
    bBuff = f.read(4)
    iBuff = struct.unpack("i", bBuff)[0]
    bidim = f.read(4)
    idim = struct.unpack("i", bidim)[0]
    bodim = f.read(4)
    odim = struct.unpack("i", bodim)[0]

    bBuff = f.read(4)
    iBuff = struct.unpack("i", bBuff)[0]
    f.read(iBuff)

    if items == 0 or idim == 0:
        return None

    #fast numpy way
    record_dtype = numpy.dtype([('inp', 'f4', (idim, )), ('outp', 'f4',
                                                          (odim, ))])
    data = numpy.fromstring(f.read(), dtype=record_dtype, count=items)
    f.close()
    if reportsizes:
        return data['inp'].astype('float64'), data['outp'].astype(
            'float64'), items
    return data['inp'].astype('float64'), data['outp'].astype('float64')
