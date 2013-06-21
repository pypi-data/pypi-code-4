from __future__ import absolute_import, unicode_literals

import random
import itertools

from . import six

def bytes(n):
	"""
	Returns n random bytes

	>>> res = list(bytes(5))
	>>> assert len(res) == 5
	>>> assert all(len(b) == 1 for b in res)
	"""
	bytes = (random.randint(0,255) for i in itertools.count())
	bytes = itertools.islice(bytes, n)
	return (six.int2byte(i) for i in bytes)
