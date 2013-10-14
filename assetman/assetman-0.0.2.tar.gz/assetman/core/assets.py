# -*- coding: utf-8 -*-

import uuid

def lookup_by_type(asset_type):
	_asset_type_map = {
		'image': Image
	}

	try:
		return _asset_type_map[asset_type]
	except KeyError: pass
	
	return Asset

class Asset(object):

	def __init__(self, data=None, uuid=None):
		self.data = data
		self.mime_type = None
		self.meta_data = {}
		self.public = False
		self._uuid = uuid

	@property
	def uuid(self):
		if not self._uuid:
			self._uuid = uuid.uuid4()
		return self._uuid

	@property
	def asset_type(self):
		return self.meta_data['asset_type']

class Image(Asset):

	def __init__(self, data, height=0, width=0, mimetype=None):
		super(Image, self).__init__(data)
		self.mime_type = mimetype
		self.meta_data['height'] = height
		self.meta_data['width'] = width
		self.meta_data['asset_type'] = 'image'

	@property
	def height(self):
		return self.meta_data['height']

	@property
	def width(self):
		return self.meta_data['width']