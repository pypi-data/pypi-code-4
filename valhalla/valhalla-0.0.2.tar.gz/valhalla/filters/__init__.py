from importlib import import_module

__all__ = [
	'strings',
	'numerical',
	'web'
]

def lookup(name):
	mod, pre, post = [None for i in xrange(3)]
	
	for m in __all__:
		mod_name = 'valhalla.filters.%s' % m
		mod = import_module(mod_name)
		if hasattr(mod, name):
			break
	
	try:
		pre = mod._prehook
		if name in mod._disable_prehook:
			pre = None
	except AttributeError: pass

	try:
		post = mod._posthook
		if name in mod._disable_posthook:
			post = None
	except AttributeError: pass

	return (getattr(mod, name), pre, post)