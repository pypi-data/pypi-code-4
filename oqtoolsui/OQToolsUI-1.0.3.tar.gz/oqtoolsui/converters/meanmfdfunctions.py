__author__ = 'orhan'

from openquake.hazardlib.mfd.truncated_gr import TruncatedGRMFD
from openquake.hazardlib.mfd.evenly_discretized import EvenlyDiscretizedMFD


__MFD_DELTA = 0.2


def computeMeanMfd(record, minMag):
    maxMags = __getMaxMagnitudeValues(record)

    if len(maxMags) == 0:
        raise Exception("Ignoring source " + record["IDAS"] + " because no max. magnitude found")

    maxMagWeights = __getMaxMagnitudeWeights(record)

    if len(maxMagWeights) != len(maxMags):
        raise Exception("Ignoring source " + record["IDAS"]
                        + " number of maximum magnitude values != to number of maximum magnitude weights!")

    aVal = float(record["A"])
    bVal = float(record["B"])

    if bVal < 0.0:
        raise Exception("b value cannot be negative")

    return __computeMeanMagFreqDist(maxMags, maxMagWeights, aVal, bVal, 1.0, minMag)


def __getSerialValues(record, keyPrefix):
    maxMags = []
    for i in xrange(1, 5):
        key = keyPrefix + str(i)
        if record.has_key(key):
            val = float(record[key])
            if val > 0.0:
                maxMags.append(val)
        else:
            break

    return maxMags


def __getMaxMagnitudeValues(record):
    return __getSerialValues(record, 'MAXMAG0')


def __getMaxMagnitudeWeights(record):
    return __getSerialValues(record, 'WMAXMAG0')


def __computeMeanMagFreqDist(maxMags, maxMagWeights, a, b, weightAB, minMag):
    rMinMag = round(minMag / __MFD_DELTA) * __MFD_DELTA
    rMinMag += __MFD_DELTA / 2
    rMinMag = round(rMinMag, 2)

    roundedMaxMags = [0.0] * len(maxMags)

    for i in xrange(len(maxMags)):
        roundedMaxMags[i] = round(maxMags[i] / __MFD_DELTA) * __MFD_DELTA
        roundedMaxMags[i] -= __MFD_DELTA / 2
        roundedMaxMags[i] = round(roundedMaxMags[i], 2)

    zipped = zip(maxMags, roundedMaxMags, maxMagWeights)

    occurrenceRates = []

    result = EvenlyDiscretizedMFD(rMinMag, __MFD_DELTA, )
    for val in zipped:
        mfd = TruncatedGRMFD()
