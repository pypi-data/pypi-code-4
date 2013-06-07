#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
from PIL import Image, ImageOps

_DIR = os.path.dirname(os.path.abspath(__file__))
_MODELS_SUFFIX = "images/models/"
_MODELS = os.path.join(_DIR, _MODELS_SUFFIX)


def match(im):
    """
    Match single char image with all models, return matched value of the image.
    """
    diffs = []
    for model in os.listdir(_MODELS):
        diffs.append(match_file(im, model))
    diffs.sort()
    return diffs[0][1][0]


def match_file(im, model_name):
    """
    Match two captchas, calculate their differences, return diff and modelname.
    """
    diff = 0
    im = Image.open(im)
    model = Image.open(_MODELS + model_name)
    img = im.resize((15, 20))
    model = model.resize((15, 20))
    width, height = model.size
    imgp = img.load()
    modelp = model.load()
    for x in range(width):
        for y in range(height):
            if imgp[x, y] != modelp[x, y]:
                diff += 1
    return diff, model_name
