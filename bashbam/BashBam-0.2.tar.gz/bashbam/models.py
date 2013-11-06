class Script():
	name = None;
	path = None;
	origin = None;

	def __unicode__(self):
		return self.name

	def __init__(self=None, name=None, path=None, origin=None):
		self.name = name
		self.path = path
		self.origin = origin

class Gist():
	id = None
	name = None
	raw_url = None

	def __unicode__(self):
		return name if name else id

	def __init__(self, id, raw_url=None, name=None):
		self.id = id
		self.raw_url = raw_url
		self.name = name
