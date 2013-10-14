# -*- coding: utf-8 -*-

from assetman.core import Assetman
from assetman.core.assets import Asset, Image


def init(key, secret, bucket):
	return Assetman(key, secret, bucket)

def create_blob(data):
	return Asset(data)

def create_image(data, height, width, mimetype):
	return Image(data, height, width, mimetype)
