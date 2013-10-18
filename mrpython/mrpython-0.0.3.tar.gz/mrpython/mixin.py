# -*- coding: utf-8 -*-


class DictInterface(object):

	_dict_attrs = ()

	@property
	def as_dict(self):
		return self.to_dict()

	def to_dict(self, only=[]):	

		def _obj_to_dict(o, limit=[]):
			names = o._dict_attrs or filter(lambda x: not x.startswith('_'), vars(o))
			if limit:
				names = list(set(limit).intersection(set(names)))
			return {k: getattr(o, k) for k in names}

		def _walk(o, parents=[], limit=[]):
			c = {}
			d = _obj_to_dict(o, limit)
			for attr, value in d.iteritems():
				if isinstance(value, DictInterface):
					if value is o:
						continue
					if value in parents:
						continue
					parents.append(o)
					c[attr] = _walk(value, parents)
				else:
					c[attr] = value
			return c

		
		return _walk(self, limit=only)