#!/usr/bin/env python
#-*- coding:utf-8 -*-

#captcha url: https://auth.szu.edu.cn/cas.aspx/

from PIL import Image, ImageOps
from rmnoise import rmnoise
from edge_detection import find_edges
from match import match
import os

_DIR = os.path.dirname(os.path.abspath(__file__))
_CROPS_SUFFIX = "images/crops/"
_CROPS = os.path.join(_DIR, _CROPS_SUFFIX)


def cleanup():
    """
    clean up crops.
    """
    for img_file in os.listdir(_CROPS):
        os.remove(_CROPS + img_file)


def preprocess(im):
    """
    do preprocessing.
    """
    im = Image.open(im)
    gray = ImageOps.grayscale(im)
    biim = gray.point(lambda i: i < 230 and 1 or 255)
    return biim


def cutcaptcha(im, edges):
    """
    cut images using edges.
    """
    for e in edges:
        xim = im.crop(e)
        of = _CROPS + "char" + str(edges.index(e)) + ".png"
        xim.save(of)


def matchcapthca():
    """
    generate captcha.
    """
    captcha = ""
    for n in range(len(os.listdir(_CROPS))):
        char = match(_CROPS + "char" + str(n) + ".png")
        captcha += str(char)
    return captcha


def captcha_regonize(im):
    """
    Run captcha regonization.
    """
    cleanup()
    img = rmnoise(preprocess(im))
    edges = find_edges(img)
    cutcaptcha(img, edges)
    captcha = matchcapthca()
    return captcha

if __name__ == "__main__":
    image = "crszu/images/captcha/gencheckcode.png"
    print captcha_regonize(image)
