import json
import os
import sys

from os import path
from string import Formatter
from types import NoneType

class ConfigError(Exception):
	pass

class ConfigInitError(ConfigError):
	pass

class ConfigFormattingError(ConfigError):
	pass

class LookupError(ConfigError):
	pass

# this is just used as an identifier for the case when a scalar value hasn't been inherited in a MultiValue
class NothingInherited(object):
	pass

class ConfigFormatter(Formatter):
	def get_field(self, field_name, args, kwargs):
		if len(args) != 2:
			raise ConfigFormattingError('while formatting "{}", expected 2 arguments'.format(field_name))
		kvReplaceContexts = args[0] # stack of replacement contexts (KeyValue instances)
		options = args[1] # replacement option set
		for kvReplacement in kvReplaceContexts:
			if not isinstance(kvReplacement, KeyValue):
				raise ConfigFormattingError('while formatting "{}", invalid replacement context, expected KeyValue instance, got: {}'.format(field_name, kvReplacement))

		first, rest = field_name._formatter_field_name_split()
		rest = [x for x in rest] # convert the iterator into a list so we can reuse it

		obj = None
		foundName = False

		# try resolving from the top of the context stack
		for kvReplacement in reversed(kvReplaceContexts):
			try:
				# iterate through the name for the local KeyValue resolver
				obj, kvResolver = kvReplacement.resolveName(first, iter(rest), options)
			except LookupError:
				continue # getting a LookupError is normal when the name being resolved isn't in the first context
			foundName = True
			break

		if not foundName:
			raise LookupError('while formatting "{}", could not resolve name'.format(field_name))

		if isinstance(obj, basestring):
			# format this string using whatever did the resolving as the topmost context
			# Formatter functions appear to be reentrant (reuse self, but use new parameters)
			obj = self.format(obj, [kvReplaceContexts[0], kvResolver], options)

		return obj, first

class MultiValue(object):
	# semi-hacky - set allowableTypes at the end of the file to allow KeyValue to be in the set, too
	allowableTypes = None

	def __init__(self, key, values, inheritedValue):
		self.key = key
		self.values = {}
		self.default = None
		foundDefault = False
		optionSets = set()
		for valueOptions, value in values:
			# check the type of the value
			valueType = type(value)
			if valueType not in self.allowableTypes:
				raise ConfigInitError('key {}: invalid value type: {} (value: {})'.format(self.key, valueType, value))
			# if the option set is empty, set it aside as the default
			if len(valueOptions) == 0:
				if foundDefault:
					# multiple default values (field name without option strings) aren't allowed (this is possible if passing args to a KeyValue through the **kwargs method)
					raise ConfigInitError('key {}: multiple default values found'.format(self.key))
				self.default = value
				foundDefault = True
			else:
				# check other values to see if the same set of options is listed twice, raise ConfigInitError if so
				if valueOptions in optionSets:
					raise ConfigInitError('key {}: option set specified multiple times: {}'.format(self.key, valueOptions))
				self.values[valueOptions] = value
			# remember that we found this set
			optionSets.add(valueOptions)
		# if the inherited value is a MultiValue, copy its values here
		if isinstance(inheritedValue, MultiValue):
			# NOTE: this copies the values over, so changes in the inherits object after this point won't propagate
			for valueOptions, value in inheritedValue.values.iteritems():
				# if this value option set was not specified already, copy it from the inherited value
				if valueOptions not in optionSets:
					self.values[valueOptions] = value
					optionSets.add(valueOptions)
			# copy the default value over, too
			if not foundDefault:
				self.default = inheritedValue.default
				foundDefault = True
		else:
			# this was just a value of some kind, so it must be intended to be the default
			if not foundDefault and inheritedValue is not NothingInherited:
				# if we didn't have a default already, use this value
				self.default = inheritedValue
				foundDefault = True
		if not foundDefault:
			raise ConfigInitError('key {}: no default value found'.format(self.key))

	@classmethod
	def create(self, key, values, inheritedValue):
		# this is a simple value if there is no inherited value,
		# only one (option set, value) tuple is present, and
		# its option set is empty
		if inheritedValue is NothingInherited and len(values) == 1 and len(values[0][0]) == 0:
			return values[0][1]
		else:
			return MultiValue(key, values, inheritedValue)

	def selectValue(self, options):
		# if there aren't any options, just return the default
		if options is None or len(options) == 0:
			return self.default
		# if there is an exact option set match, use that value
		try:
			return self.values[options]
		except KeyError:
			pass
		# otherwise, find the best match
		bestMatch = None
		bestMatchCount = 0
		foundTie = None
		# scan all subsets
		for valueOptions, value in self.values.iteritems():
			if valueOptions < options:
				# pick the value with the largest intersection
				matchingOptions = options & valueOptions
				matchCount = len(matchingOptions)
				if 0 == matchCount:
					# skip non-matching sets
					continue
				if matchCount > bestMatchCount:
					bestMatch = value
					bestMatchCount = matchCount
					foundTie = None
				elif matchCount == bestMatchCount:
					# if a tie is found, remember this condition (don't raise
					# an exception immediately in case there is another set
					# that matches better
					foundTie = matchCount
		if foundTie is not None:
			raise LookupError('key {}: multiple candidate values found matching {} option(s)'.format(self.key, foundTie))
		# if no candidates found, return default
		if 0 == bestMatchCount:
			return self.default
		else:
			return bestMatch

class KeyValue(object):
	keyOptionNameSeparator = '__'
	ignoreKeyPrefix = '_'

	def __init__(self, inherits=None, **kwargs):
		if inherits is None or isinstance(inherits, KeyValue):
			self.inherits = inherits
		else:
			raise ConfigInitError('inherits parameter: KeyValue instance expected')
		# TODO: pass 0, do a full traversal of contents of each field, converting MultiValues (or rewrite this to recursively descend)
		# parse options, pass 1, gather similar options
		self.fields = {}
		for key, value in kwargs.items():
			# split all keys to find applicable option strings, put them in buckets
			keyOptions = key.split(self.keyOptionNameSeparator)
			keyName = keyOptions.pop(0)
			if self.fields.has_key(keyName):
				self.fields[keyName].append((frozenset(keyOptions), value))
			else:
				self.fields[keyName] = [(frozenset(keyOptions), value)]
		# pass 2, convert to fields to MultiValue if necessary
		for key, values in self.fields.items():
			# NOTE: this returns scalar values directly, not a MultiValue instance
			inheritedValue = getattr(self.inherits, key) if self.inherits is not None and self.inherits.hasField(key) else NothingInherited
			self.fields[key] = MultiValue.create(key, values, inheritedValue)

	def __getattribute__(self, name):
		try:
			return object.__getattribute__(self, 'fields')[name]
		except KeyError:
			return super(KeyValue, self).__getattribute__(name)

	def hasField(self, key):
		return self.fields.has_key(key)

	def __convertValue(self, input, options, replacements):
		# non-public helper function to recurse into dict structures
		outputValue = None
		# if this is a multivalue instance, pick the best option to use
		value = input.selectValue(options) if isinstance(input, MultiValue) else input
		valueIsTuple = isinstance(value, tuple)
		if isinstance(value, KeyValue):
			outputValue = value.convertToDict(options, replacements)
		elif valueIsTuple or isinstance(value, list):
			outputValue = []
			# iterate through the list, converting each value as necessary
			for subValue in value:
				outputValue.append(self.__convertValue(subValue, options, replacements))
			# if the value was a tuple, convert it to one before returning
			if valueIsTuple:
				outputValue = tuple(outputValue)
		elif isinstance(value, dict):
			outputValue = {}
			for subKey, subValue in value.items():
				if not subKey.startswith(self.ignoreKeyPrefix):
					outputValue[subKey] = self.__convertValue(subValue, options, replacements)
		elif isinstance(value, str):
			# replace string references if desired
			if replacements is None:
				outputValue = value
			else:
				# use custom Formatter instance to replace strings
				# start search at local object
				outputValue = ConfigFormatter().format(value, [replacements, self], options)
		elif isinstance(value, int) or isinstance(value, bool) or isinstance(value, float) or value is None:
			# just pass these types through
			outputValue = value
		else:
			# type is unknown, raise an error
			# TODO: should it just include the value instead?
			raise ConfigError('unknown type found for value: {} (type: {})'.format(value, type(value)))
		return outputValue

	def convertToDict(self, options=None, replacements=None):
		# put fields to export here
		output = {} if self.inherits is None else self.inherits.convertToDict(options, replacements)
		# traverse field structure, recursing into other KeyValue items when found
		for key, value in self.fields.items():
			# skip copying anything that starts with ignoreKeyPrefix
			if key.startswith(self.ignoreKeyPrefix):
				continue
			# now convert the value to its output format
			output[key] = self.__convertValue(value, options, replacements)
		return output

	def resolveName(self, initialKey, otherKeys, options=None):
		lookupObject = None
		resolver = self
		try:
			# check fields for initial key
			try:
				lookupObject = self.fields[initialKey]
			except KeyError:
				# look in inherits object if it wasn't in this one
				if self.inherits is not None:
					lookupObject = self.inherits.fields[initialKey]
				else:
					raise
			# now process fields one at a time, resolving the object along the way
			foundKeyValue = False
			while not foundKeyValue:
				# resolve any MultiValue objects here before looking up sub-items
				if isinstance(lookupObject, MultiValue):
					lookupObject = lookupObject.selectValue(options)
				try:
					isAttribute, nextFieldSelector = otherKeys.next()
				except StopIteration:
					break
				if isAttribute:
					# attribute access via dot notation, e.g. a.b.c
					if isinstance(lookupObject, dict):
						# allowing alternate lookup method for dicts (can use dot notation rather than index notation)
						lookupObject = lookupObject[nextFieldSelector]
					elif isinstance(lookupObject, KeyValue):
						# delegate the rest of the resolving to this KeyValue object
						lookupObject, resolver = lookupObject.resolveName(nextFieldSelector, otherKeys, options)
						foundKeyValue = True
					else:
						lookupObject = getattr(lookupObject, nextFieldSelector)
				else:
					lookupObject = lookupObject[nextFieldSelector]
		except:
			raise LookupError()
		return (lookupObject, resolver)

class Config(KeyValue):
	def convertToDict(self, *args, **kwargs):
		# shortcut to pass self as a replacement
		if not kwargs.has_key('replacements'):
			kwargs['replacements'] = self
		return KeyValue.convertToDict(self, *args, **kwargs)

	def convertToJson(self, options=None, replaceStrings=True, prettyJson=False, indent=4):
		return json.dumps(
			self.convertToDict(options, replacements=self if replaceStrings else None),
			indent=indent if prettyJson else None,
			separators=(',', ': ' if prettyJson else ':')
			)

def import_config_module(moduleName, nameIsPyFile=True):
	configModule = None
	if nameIsPyFile:
		# treating the input parameter as a filename
		inputpath = path.abspath(moduleName)
		if not path.isfile(inputpath):
			raise RuntimeError('input file does not exist: {}'.format(moduleName))
		# get the path of the input file
		inputFileDir, inputFile = path.split(inputpath)
		moduleName = path.splitext(inputFile)[0]
	else:
		# use the current directory as the path in case the module is a file in the local directory
		inputFileDir = os.getcwd()
	# save the current path
	oldPath = sys.path[:]
	# add the module's directory to the path
	sys.path.insert(0, inputFileDir)
	# and import the module
	__import__(moduleName, level=0)
	configModule = sys.modules[moduleName]
	# restore the old path
	sys.path[:] = oldPath
	return configModule

def get_configs_from_module(module):
	configInstances = {}
	for key in dir(module):
		obj = module.__getattribute__(key)
		if isinstance(obj, Config):
			configInstances[key] = obj
	return configInstances

def get_config_from_module(module, name):
	return get_configs_from_module(module)[name]

def make_multi_key(*args):
	return KeyValue.keyOptionNameSeparator.join(args)

# semi-hacky - set allowableTypes at the end of the file to allow KeyValue to be in the set, too
if MultiValue.allowableTypes is None:
	MultiValue.allowableTypes = frozenset([str, unicode, int, float, bool, NoneType, dict, list, tuple, KeyValue])
