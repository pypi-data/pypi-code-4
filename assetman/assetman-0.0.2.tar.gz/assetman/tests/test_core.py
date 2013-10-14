# -*- coding: utf-8 -*-

from nose.tools.trivial import assert_is_none, assert_is_not_none, assert_is_instance, assert_equals

from boto.s3.connection import S3Connection

from assetman.tests import TEST_KEY, TEST_SECRET, TEST_BUCKET
from assetman.core import Assetman
from assetman.core.assets import Asset

def test_assetman():
	a = Assetman(TEST_KEY, TEST_SECRET, TEST_BUCKET)

	assert_is_none(a._connection)
	ctx = a.connection
	assert_is_instance(ctx, S3Connection)

	asset = Asset('my sweet data')
	a.save_asset(asset)
	assert_is_not_none(asset.uuid)

	retrieved = a.get_asset(asset.uuid)

	assert_equals(asset.uuid, retrieved.uuid)

	a.delete_asset(asset.uuid)

	assert_is_none(a.get_asset(asset.uuid))