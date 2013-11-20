"""Generic utility functions to

* write variables and tuples to file
* write and read setting from a file
* modify and create tuples.

"""
import itertools as it
import time

from ..lib.six.moves import configparser as cp


def write_var_to_file(text_file, var):
	text_file.write(str(var) + '\n')


def write_tuple_to_file(text_file, tuple_):
	line = ''
	separator = ','
	new_line = '\n'

	for item in tuple_:
		line += str(item)
		line += separator

	# delete the last separator
	if len(line) > 0:
		line = line[:-1]

	line += new_line
	text_file.write(line)


def write_settings(filename, section, mapped_values):
	"""Write ``mapped_values`` at ``section`` in settings file at ``filename``.

	:param filename: settings file
	:type filename: str
	:param section: settings section
	:type section: str
	:param mapped_values: values to write
	:type mapped_values: dict

	Example:

	>>> write_settings('test.cfg', 'mySection', {'a_key': 1.1111, 'another_key': False})

	"""
	config = cp.RawConfigParser()
	config.add_section(section)

	for key in mapped_values.keys():
		config.set(section, key, mapped_values[key])

	with open(filename, 'w') as configfile:
		config.write(configfile)


def read_settings(filename, section):
	"""Read ``section`` from settings file at ``filename``.

	:param filename: settings file
	:type filename: str
	:param section: settings section
	:type section: str
	:return: settings section dictionary
	:rtype: dict

	Example:

	>>> read_settings('test.cfg', 'mySection')
	{'a_key': 1.1111, 'another_key': False}

	"""
	config = cp.RawConfigParser()
	config.read(filename)

	return dict(config.items(section))


def insert_in_tuple(tuple_, index, item_):
	tuple_to_list = list(tuple_)
	tuple_to_list.insert(index, item_)
	return tuple(tuple_to_list)


def nested_iterable_to_tuple(iterable_):
	return tuple(it.chain.from_iterable(iterable_))


def get_current_epoch_time():
	"""Return the current time in seconds since the Epoch.

	Fractions of a second may be present if the OS provides them
	(UNIX-like do).

	:return: number of seconds since the Epoch
	:rtype: float

	"""
	return time.time()
