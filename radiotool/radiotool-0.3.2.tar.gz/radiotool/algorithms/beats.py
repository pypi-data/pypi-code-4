
import fractions

import numpy as N
from scipy.signal import resample, lfilter

def tempo(song):
    # port of http://labrosa.ee.columbia.edu/projects/coversongs/
    d = song.all_as_mono()

    tmean = 120.0
    tsd = 3.0

    sro = 8000.
    swin = 256.
    shop = 32.
    nmel = 40.
    sgsrate = sro / shop
    acmax = int(round(4 * sgsrate))

    D = 0

    # calculate onsetenv
    sr = song.samplerate
    if sr != sro:
        gg = fractions.gcd(sro, sr)
        d = resample(d, len(d) / sr * sro)
        sr = sro

    D = specgram(d, swin, sr, swin, swin - shop)

    mlmx = fft2melmx(swin, sr, nmel)[0]
    D = 20 * N.log10(N.maximum(1e-10, mlmx[:, :swin / 2 + 1].dot(N.abs(D))))

    D = N.maximum(D, N.max(D) - 80)

    mm = N.mean(N.maximum(0, N.diff(D.T).T), axis=0)
    eelen = len(mm)

    onsetenv = lfilter([1, -1], [1, -0.99], mm)

    # end of onsetenv calculation block

    maxdur = 90
    maxcol = N.minimum(N.around(maxdur * sgsrate), len(onsetenv))

    xcr = xcorr(onsetenv[:maxcol], onsetenv[:maxcol], maxlags=acmax)[0]

    rawxcr = xcr[acmax:acmax * 2 + 1]

    xcrwin = N.exp(-.5 * N.power(N.log(60 * sgsrate / N.arange(acmax + 1) / 0.1 / tmean) / N.log(2) * tsd, 2))

    xcr = rawxcr * xcrwin
    print xcr[154]

    xpks = localmax(xcr).astype(int)

    print min(N.where(xcr < 0)[0])

    xpks[:min(N.where(xcr < 0)[0])] = 0
    maxpk = N.max(xcr[N.where(xpks == 1)[0]])

    # startpd = N.where(xcr[xpks] == N.max(xcr[xpks]))[0][0]

    startpd = N.where(xcr * xpks == N.max(xcr * xpks))[0][0]

    print startpd

    t = 60. / (startpd / sgsrate)

    candpds = N.around([.33, .5, 2, 3] * startpd)
    candpds = N.where(candpds < acmax)[0]

    vv = N.max(xcr[candpds])
    xx = N.argmax(xcr[candpds])

    print "vv", vv
    print "xx", xx

    startpd2 = candpds[xx]
    vvm = xcr[startpd]
    pratio = vvm / (vvm + vv)

    t = [60. / (startpd / sgsrate), 60. / (startpd2 / sgsrate), pratio]

    if t[1] < t[0]:
        tmp = t[1]
        t[1] = t[0]
        t[0] = tmp

    return t




def specgram(x, n=256., sr=1., w=None, ov=None):
    s = len(x)
    if w is None:
        w = n
    if ov is None:
        ov = w / 2.

    h = w - ov

    halflen = w / 2.
    halff = n / 2.
    acthalflen = min(halff, halflen)

    halfwin = 0.5 * (1 + N.cos(N.pi * N.arange(halflen + 1) / halflen))
    win = N.zeros(n)
    win[halff:halff + acthalflen] = halfwin[:acthalflen]
    win[halff - acthalflen + 1:halff + 1] = halfwin[:acthalflen][::-1]

    c = 0

    ncols = 1 + N.fix((s - n) / h)
    d = N.zeros((1 + n / 2, ncols))

    for b in N.arange(0, s - n + h, h):
        u = win * x[b:b + n]
        t = N.fft.fft(u).T
        d[:, c] = t[:1 + n / 2]
        c += 1

    # tt = N.arange(0, s - n + h, h) / sr
    # ff = N.arange(0, n / 2 + 1) * sr / n

    return d


def fft2melmx(nfft, sr=8000, nfilts=0, width=1.0, minfrq=0,
              maxfrq=None, htkmel=0, constamp=False):
    if maxfrq is None:
        maxfrq = sr / 2

    if nfilts == 0:
        nfilts = N.ceil(hz2mel(maxfrq, htkmel) / 2)

    wts = N.zeros((nfilts, nfft))

    fftfrqs = N.arange(nfft / 2 + 1) / nfft * sr

    minmel = hz2mel(minfrq, htkmel)
    maxmel = hz2mel(maxfrq, htkmel)
    binfrqs = mel2hz(minmel + N.arange(nfilts + 2) /
                     (nfilts + 1) * (maxmel - minmel),
                     htkmel)

    # binbin = N.around(binfrqs / sr * (nfft - 1))

    for i in N.arange(nfilts):
        fs = binfrqs[i:i + 3]
        fs = fs[1] + width * (fs - fs[1])

        loslope = (fftfrqs - fs[0]) / (fs[1] - fs[0])
        hislope = (fs[2] - fftfrqs) / (fs[2] - fs[1])

        wts[i, :nfft / 2 + 1] = N.maximum(0, N.minimum(loslope, hislope))

    if not constamp:
        wts = N.diag(2. / (binfrqs[2:nfilts + 2] - binfrqs[:nfilts])).dot(wts)

    wts[:, nfft / 2 + 1:nfft] = 0

    return wts, binfrqs


def mel2hz(z, htk=False):
    try:
        len(z)
    except:
        z = N.array([z])
    if htk:
        f = 700. * (N.power(10., z / 2595.) - 1)
    else:
        f_0 = 0.
        f_sp = 200 / 3.
        brkfrq = 1000.
        brkpt = (brkfrq - f_0) / f_sp
        logstep = N.exp(N.log(6.4) / 27.)
        linpts = (z < brkpt)

        f = N.zeros(N.shape(z))

        f[linpts] = f_0 + f_sp * z[linpts]
        f[linpts == False] = brkfrq *\
            N.exp(N.log(logstep) * (z[linpts == False] - brkpt))
    return f


def hz2mel(f, htk=False):
    try:
        len(f)
    except:
        f = N.array([f])
    if htk:
        z = 2595. * N.log10(1 + f / 700.)
    else:
        f_0 = 0
        f_sp = 200 / 3.
        brkfrq = 1000.
        brkpt = (brkfrq - f_0) / f_sp
        logstep = N.exp(N.log(6.4) / 27.)

        linpts = (f < brkfrq)

        z = N.zeros(N.shape(f))

        z[linpts] = (f[linpts] - f_0) / f_sp
        z[linpts == False] = brkpt +\
            (N.log(f[linpts == False] / brkfrq)) / N.log(logstep)

    return z


def xcorr(x, y, normed=False, maxlags=10, **kwargs):
        # from matplotlib.pyplot

        Nx = len(x)
        if Nx != len(y):
            raise ValueError('x and y must be equal length')

        c = N.correlate(x, y, mode=2)

        if normed:
            c /= N.sqrt(N.dot(x, x) * N.dot(y, y))

        if maxlags is None:
            maxlags = Nx - 1

        # if maxlags >= Nx or maxlags < 1:
        #     raise ValueError('maxlags must be None or strictly '
        #                      'positive < %d' % Nx)

        lags = N.arange(-maxlags, maxlags + 1)
        c = c[Nx - 1 - maxlags:Nx + maxlags]

        return c, lags


def localmax(x):
    y = N.empty(N.shape(x), dtype=N.bool)
    y[0] = False
    y[-1] = False
    y[1:-1] = N.logical_and(x[1:-1] > x[:-2], x[1:-1] > x[2:])
    return y
