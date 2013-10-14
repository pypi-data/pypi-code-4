# -*- coding: utf-8 -*-

from nose.tools.trivial import assert_is_instance, assert_equal
from os import path
from wand.image import Image as WandImage

from assetman import init, create_blob, create_image
from assetman.core import Assetman
from assetman.core.assets import Asset, Image
from assetman.tests import TEST_KEY, TEST_SECRET, TEST_BUCKET

def test_init():
	am = init(TEST_KEY, TEST_SECRET, TEST_BUCKET)
	assert_is_instance(am, Assetman)

def test_create_blob():
	b = create_blob('some random data')
	assert_is_instance(b, Asset)

def test_create_image():
	with WandImage(filename=path.join(path.dirname(__file__), 'fixtures/faceoff.jpg')) as image:
		i = create_image(image.make_blob(), image.height, image.width, image.mimetype)
		assert_is_instance(i, Image)