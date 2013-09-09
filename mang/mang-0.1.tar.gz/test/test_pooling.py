#!/usr/bin/python
#coding=utf-8

"""
test_pooling
~~~~~~~~~~~~

Test max-pooling routine of cudamat-conv.

.. moduleauthor:: Yoonseop Kang <e0engoon@gmail.com>

"""
import Image
import numpy as np

import cudamat as cm

from mang.edge import MaxPoolingEdge

if __name__ == '__main__':
    img = Image.open("suzy.jpg").convert("L").resize((64, 96),
                                                     Image.ANTIALIAS)
    arr = np.asarray(img)[:64, :64] / 255.
    arr = np.array(arr, dtype=np.float32, order="F")
    img_cropped = Image.fromarray(np.uint8(arr * 255.))
    img_cropped.save("suzy_cropped.png")
    arr_rep = np.zeros((64, 64, 16), dtype=np.float32, order="F")
    for i in xrange(16):
        arr_rep[:, :, i] = arr
    arr_cm = cm.empty((1, 65536))
    arr_cm.overwrite(np.array(arr_rep.reshape((1, 65536), order="F")))
    out_cm = cm.empty((1, 16 ** 3))

    option = {"ratio": 4, }
    e = MaxPoolingEdge((64, 64, 16), (16, 16, 16), option)
    e.up(arr_cm, out_cm)
    out = out_cm.asarray().reshape((16, 16, 16), order="F")
    for i in xrange(16):
        img_up = Image.fromarray(np.uint8(out[:, :, i] * 255.))
        img_up.save("suzy_up_%d.png" % i)

    arr_vec = arr_cm.asarray()

    dx = cm.empty((1, 65536))
    do = cm.empty((1, 16 ** 3))
    do.assign(out_cm)
    e.down(do, dx, out_cm, arr_cm)

    dn = dx.asarray().reshape((64, 64, 16), order="F")
    for i in xrange(16):
        img_dn = Image.fromarray(np.uint8(dn[:, :, i] * 255.))
        img_dn.save("suzy_dn_%d.png" % i)
