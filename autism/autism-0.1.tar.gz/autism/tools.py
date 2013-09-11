# coding: utf-8

import importlib

def import_plugin(plugin_spec):
	""" Return symbol specified using a plugin specification in plugin_spec

	Plugin Specifications
	---------------------

	A plugin specification is a string or a list or a tuple which defines
	a module and an optional symbol and an optional expression. A normalized
	plugin specification is a plugin specification as a tuple with three parts,
	where the last two optional can be None.

	Examples:

	('a')    Non-normal plugin specification, which will load the module a
	         and return it
	('a', None, None) The normalized version of the previous
	'a'      The same plugin specification defined as string
	
	('a', 'b', 'c') Normalized plugin specification which will load the module
	                a, search for the attribute b and return
									  eval("a.b.c")
	'a:b.c'         String-version of the previous

	('a', 'b', None) Normalized plugin specification which will load the module
	                 a and return the attribute b
	'a:b'            String-version of the previous
	"""
	if isinstance(plugin_spec, str) or isinstance(plugin_spec, unicode):
		new_spec = [None, None, None]
		tokens = plugin_spec.split(":", 1)
		new_spec[0] = tokens[0]
		if len(tokens) > 1:
			tokens = tokens[1].split(".", 1)
			new_spec[1] = tokens[0]
			if len(tokens) > 1:
				new_spec[2] = tokens[1]
		plugin_spec = tuple(new_spec)
	elif isinstance(plugin_spec, tuple) or isinstance(plugin_spec, list):
		plugin_spec = list(plugin_spec)
		plugin_spec.extend([None] * (3 - len(plugin_spec)))
		plugin_spec = tuple(plugin_spec)
	else:
		raise ValueError("Invalid plugin specification: {0!r}".format(plugin_spec))

	plugin = None
	plugin = importlib.import_module(plugin_spec[0])

	if plugin_spec[1] is not None:
		plugin = getattr(plugin, plugin_spec[1])
	
	if plugin_spec[2] is not None:
		plugin = eval("plugin.{}".format(plugin_spec[2]))
	
	return plugin
