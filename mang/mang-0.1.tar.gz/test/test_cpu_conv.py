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
from cudamat import cudamat_conv as cm_conv

from mang.edge import MaxPoolingEdge
from mang import cpu_conv

if __name__ == '__main__':
    # testing max-pooling routines
    x_size = 64
    ratio = 4
    n_channel = 16
    n_filter = 16
    y_size = x_size / 2 * 3
    x_pixels = x_size ** 2 * n_channel
    o_pixels = x_pixels / (ratio ** 2)
    o_size = x_size / ratio
    RGB_MAX = 255.

    img = Image.open("suzy.jpg").convert("L").resize((x_size, y_size),
                                                     Image.ANTIALIAS)
    arr = np.asarray(img)[:x_size, :x_size] / RGB_MAX
    arr = np.array(arr, dtype=np.float32, order="F")
    img_cropped = Image.fromarray(np.uint8(arr * RGB_MAX))
    img_cropped.save("suzy_cropped.png")
    arr_rep = np.zeros((x_size, x_size, n_filter), dtype=np.float32, order="F")
    for i in xrange(16):
        arr_rep[:, :, i] = arr
    arr_vec = arr_rep.reshape((1, x_pixels), order="F")
    arr_cm = cm.empty((1, x_pixels))
    arr_cm.overwrite(np.array(arr_vec))
    out_cm = cm.empty((1, o_pixels))

    option = {"ratio": ratio, }
    e = MaxPoolingEdge((x_size, x_size, n_channel),
                       (o_size, o_size, n_channel), option)
    e.init_training({"batch_size": 1})
    e.up(arr_cm, out_cm)
    out_gpu = out_cm.asarray().reshape((o_size, o_size, n_channel), order="F")

    out_cpu = cpu_conv.max_pool(arr_vec, n_channel, ratio, ratio)
    out_cpu = out_cpu.reshape((o_size, o_size, n_channel), order="F")

    for i in xrange(n_channel):
        img_up = Image.fromarray(np.uint8(out_gpu[:, :, i] * RGB_MAX))
        img_up.save("suzy_up_%d.png" % i)

        img_up = Image.fromarray(np.uint8(out_cpu[:, :, i] * RGB_MAX))
        img_up.save("suzy_up_cpu_%d.png" % i)

    # testing response-normalization
    p_cm = cm.empty(arr_cm.shape)
    out_cm = cm.empty(arr_cm.shape)
    norm_size = 8
    add_scale = 1.
    pow_scale = 1.

    cm_conv.ResponseNorm(arr_cm, p_cm, out_cm, n_channel, norm_size,
                         add_scale, pow_scale)
    out_gpu = out_cm.asarray()
    p_gpu = p_cm.asarray()
    (out_cpu, p_cpu) = \
        cpu_conv.response_normalization(arr_vec, n_channel, norm_size,
                                        add_scale, pow_scale)

    out_gpu = out_gpu.reshape((x_size, x_size, n_channel), order="F")
    out_cpu = out_cpu.reshape((x_size, x_size, n_channel), order="F")

    p_gpu = p_gpu.reshape((x_size, x_size, n_channel), order="F")
    p_cpu = p_cpu.reshape((x_size, x_size, n_channel), order="F")

    min_val = out_gpu.min()
    out_gpu -= min_val
    max_val = out_gpu.max()
    out_gpu /= max_val

    out_cpu -= min_val
    out_cpu /= max_val

    min_val = p_gpu.min()
    p_gpu -= min_val
    max_val = p_gpu.max()
    p_gpu /= max_val

    p_cpu -= min_val
    p_cpu /= max_val

    for i in xrange(n_channel):
        img_up = Image.fromarray(np.uint8(out_gpu[:, :, i] * RGB_MAX))
        img_up.save("suzy_rnorm_%d.png" % i)

        img_up = Image.fromarray(np.uint8(out_cpu[:, :, i] * RGB_MAX))
        img_up.save("suzy_rnorm_cpu_%d.png" % i)

        img_up = Image.fromarray(np.uint8(p_gpu[:, :, i] * RGB_MAX))
        img_up.save("suzy_p_%d.png" % i)

        img_up = Image.fromarray(np.uint8(p_cpu[:, :, i] * RGB_MAX))
        img_up.save("suzy_p_cpu_%d.png" % i)



    # testing on a color image for convolution
    n_channel = 3
    filter_size = 4
    stride = 2
    o_size = (x_size - filter_size) / stride + 1

    filters = np.random.randn(n_filter, n_channel * filter_size ** 2)
    img = Image.open("suzy.jpg").resize((x_size, y_size), Image.ANTIALIAS)
    arr = np.asarray(img)[:x_size, :x_size, :] / RGB_MAX
    arr = np.array(arr, dtype=np.float32, order="F")
    img_cropped = Image.fromarray(np.uint8(arr * RGB_MAX))
    img_cropped.save("suzy_color_cropped.png")
    arr_vec = arr.reshape((1, x_size ** 2 * n_channel), order="F")
    o_cm = cm.empty((1, o_size ** 2 * n_filter))

    arr_cm = cm.empty((1, x_size ** 2 * n_channel))
    arr_cm.overwrite(arr_vec)
    filter_cm = cm.empty((n_filter, filter_size ** 2 * n_channel))
    filter_cm.overwrite(filters)
    cm_conv.convUp(arr_cm, filter_cm, o_cm, o_size, 0, stride, n_channel)
    o_gpu = o_cm.asarray()
    o_gpu = o_gpu.reshape((o_size, o_size, n_filter), order="F")

    o_cpu = cpu_conv.conv_up(arr_vec, filters, n_channel, stride)
    o_cpu = o_cpu.reshape((o_size, o_size, n_filter), order="F")

    for i in xrange(n_filter):
        tmp = o_cpu[:, :, i]
        tmp -= tmp.min()
        tmp /= tmp.max()
        img_up = Image.fromarray(np.uint8(tmp * RGB_MAX))
        img_up.save("suzy_conv_cpu_%d.png" % i)

        tmp = o_gpu[:, :, i]
        tmp -= tmp.min()
        tmp /= tmp.max()
        img_up = Image.fromarray(np.uint8(tmp * RGB_MAX))
        img_up.save("suzy_conv_gpu_%d.png" % i)

        tmp = filters[i]
        tmp -= tmp.min()
        tmp /= tmp.max()
        tmp_ch = tmp.reshape((filter_size, filter_size, n_channel),
                             order="F")
        for j in xrange(n_channel):
            img_up = Image.fromarray(np.uint8(tmp_ch[:, :, j] * RGB_MAX))
            img_up.save("filters_%d_%d.png" % (i, j))
