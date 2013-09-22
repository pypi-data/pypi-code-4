"""Temporarily modify callable behaviour and object attributes.	
"""

import new
import uuid

from types import TypeType
from functools import wraps, partial
from inspect import getmembers, ismethod, getargspec
from copy import copy

__version__ = '0.2.1'

_stubbed_callables = []
_modified_objects = []

def get_stubbed():
	'Return the collection of all stubbed callables'
	return _stubbed_callables

def get_modified():
	'Return the collection of all modified objects'
	return _modified_objects

def stub_bound_function(target, repl):
	"""Stub out the behaviour of a bound function, `target`, with `repl`.

	The parent object of `target` is looked up. Then, a `stub` function is
	created based on the behaviour of `repl` that will be used as the
	replacement for `target`. The `stub` function has `unstub` and `unstubbed`
	functions added to it using the unstubbed behaviour of `target`. Finally,
	the `stub` function is assigned to the name of `target` on it's parent
	object.

	.. note::

		It is not necessary to have a `self` argument for `repl` when
		stubbing out an instance method. If `repl` has one less positional
		argument than `target`, the `self` argument is automagically supplied.

	.. note::

		It is permissible to provide a `repl` function with **less** arguments
		than `target`. In this case, positional arguments are matched in order,
		with any missing parameters receiving ``None`` instead. If
		keyword-arguments are missing from `repl` then they are automagically
		replaced with ``None`` or the default value specified by `target` if one
		is available.

	.. warning::

		It is an error to provide a `repl` function with more arguments than
		`target`. Doing so will raise a ``TypeError``.
	"""
	_orig = target
	_self = target.im_self

	bf_argnames = getargspec(target)[0]
	mf_argnames, args, kwargs, defs = getargspec(repl)

	assert_compatible(target, repl)

	if hasattr(target, '_unstubbing_stack'):
		target._unstubbing_stack.append((target.unstub, target.unstubbed, target))
		t = target._unstubbing_stack[-1][2]
	else:
		t = target

	@wraps(t)
	def __f(*_args, **_kwargs):
		firstArgIsImSelf = _args[0] == _self
		stubbedFunctionArglistStartsWithSelf = (bf_argnames and bf_argnames[0] == 'self')
		stubFunctionArglistDoesNotStartWithSelf = (not mf_argnames or mf_argnames[0] != 'self')
		argListLengthsDiffer = len(bf_argnames) != len(mf_argnames)

		if (not args) and (not kwargs) and firstArgIsImSelf and stubFunctionArglistDoesNotStartWithSelf and argListLengthsDiffer:
			_args = _args[1:]

		return repl(*_args, **_kwargs)

	__f._old_func_code = __f.func_code

	def unstub():
		__f.func_code = __f._old_func_code

		if __f._unstubbing_stack:
			p = __f._unstubbing_stack.pop()

			if hasattr(p[2], '_unstubbing_stack'):
				p = list(p)
				p[2] = p[2].im_func.func_code

			__f.unstub, __f.unstubbed, __f._old_func_code = p
		else:
			del __f.unstub
			del __f.unstubbed
			del __f._unstubbing_stack

			_modified_objects.remove(target)

		if hasattr(target.im_self, target.__name__):
			setattr(target.im_self, target.__name__, target)
		else:
			setattr(target.im_class, target.__name__, target)

	def unstubbed(*args, **kwargs):
		if args and args[0] == target.im_self:
			args = args[1:]
		return _orig(*args, **kwargs)

	__f.unstub = unstub
	__f.unstubbed = unstubbed
	__f._unstubbing_stack = []

	def get_fname(_self, target):
		for name, val in getmembers(_self):
			if ismethod(val) and val == target:
				return name
		return None

	fname = get_fname(_self, target) or target.__name__

	if hasattr(target, 'im_class') and target.im_self is None:
		stubbed = __f
		setattr(target.im_class, fname, stubbed)
	else:
		stubbed = new.instancemethod(__f, target.im_self, target.im_self.__class__)
		setattr(target.im_self, fname, stubbed)

	_modified_objects.append(target)

	return stubbed

def __add_unstubbed_function(target, closure=None):
	if not closure:
		closure = target.func_code.co_cellvars

	_orig = new.function(target._old_func_code, target.func_globals, closure=closure)
	varnames, varargs, varkw, cdefaults = getargspec(target)

	def unstubbed(*args, **kwargs):
		varnames, varargs, varkw, defaults = getargspec(_orig)
		defdict = dict(zip(varnames or [], cdefaults or []))

		if varnames: # This function takes a number of variables
			if len(args) == len(varnames): # We probably have all the values we need
				pass
			else: # We are probably missing kwarg values, let's check
				"""
				Python is a bit weird and this deserves a little note here:

				Any arguments that have a name in the function definition contribute to the
				varnames collection. On the other hand, in some cases it appears that
				even though an argument is declared as a keyword argument with a default value
				it does not appear in the `varkw` collection, nor does the default value
				(which must be `None` for this to happen) show up in the `defaults` collection.

				If this makes your head hurt come and talk to me... we can take aspirin together.
				"""
				for n in varnames:
					if not defaults and len(args) <= varnames.index(n):
						#kwargs[n] = None
						pass

					if not n in kwargs and n in defdict:
						kwargs[n] = defdict[n]
		else:
			#print 'No default values for params: ', getargspec(_orig)
			pass

		return _orig(*args, **kwargs)

	target.unstubbed = unstubbed

def assert_compatible(f, repl):
	# Check that we have the same number of args
	fargspec = getargspec(f)

	if hasattr(repl, 'func_code'):
		rargspec = getargspec(repl)
	else: # This is a bound function, get the argspec of the code object
		rargspec = getargspec(repl.__call__.im_func)

	flen = len(fargspec[0])
	rlen = len(rargspec[0])

	if fargspec.args and (rargspec.varargs or rargspec.keywords):
		return

	if rargspec.args and (fargspec.varargs or fargspec.keywords):
		return

	if not fargspec.args and rargspec.args == ['self']:
		return

	if 'self' not in fargspec.args and 'self' in rargspec.args:
		rlen -= 1

	if flen < rlen:
		if hasattr(f, '_unstubbing_stack'):
			msg = 'The replacement function cannot take more parameters than the function it replaces; check your stubbing stack'
		else:
			msg = 'The replacement function cannot take more parameters than the original'
		raise ValueError(msg + '; wanted %s parameters (%s) but found %s in the replacement (%s)' % (flen, ', '.join(fargspec.args), rlen, ', '.join(rargspec.args)))

def stub_unbound_function(target, repl):
	"""Stub out the behaviour of an unbound function, `target`, with `repl`.

	The function's code objec ``func_code`` is replaced.

	.. note::

		It is permissible to provide a `repl` function with **less** arguments
		than `target`. In this case, positional arguments are matched in order,
		with any missing parameters receiving ``None`` instead. If
		keyword-arguments are missing from `repl` then they are automagically
		replaced with ``None`` or the default value specified by `target` if one
		is available.

	.. note::
		
		If you stub out a function on a class, the changes will propagate to all
		instances of the class.

	.. warning::

		It is an error to provide a `repl` function with more arguments than
		`target`. Doing so will raise a ``TypeError``.
		
	"""
	assert_compatible(target, repl)

	if hasattr(target, '_unstubbing_stack'):
		target._unstubbing_stack.append((target.unstub, target.unstubbed, target._old_func_code))
	else:
		target._unstubbing_stack = []

	target._old_func_code = target.func_code

	def unstub():
		target.func_code = target._old_func_code

		if target._unstubbing_stack:
			target.unstub, target.unstubbed, target._old_func_code = target._unstubbing_stack.pop()
		else:
			del target.unstub
			del target.unstubbed
			del target._unstubbing_stack

			get_stubbed().remove(target)

	if isinstance(repl, partial):
		repl = repl.func
	elif not hasattr(repl, 'func_code'):
		_repl = repl.__call__.im_func
		_self = repl.__call__.im_self

		def wrapper(*args, **kwargs):
			return _repl(_self, *args, **kwargs)

		repl = wrapper


	fcode = copy(repl.func_code)

	from byteplay import Code, LOAD_GLOBAL, LOAD_DEREF

	co = Code.from_code(fcode)
	co.filename = fcode.co_filename
	co.firstlineno = fcode.co_firstlineno

	if fcode.co_freevars:
		uid = str(uuid.uuid4())
		mangle_name = lambda x: '%s_%s' % (x, uid.replace('-', '_'))

		co.code = [(LOAD_GLOBAL, mangle_name(x[1])) if x[0] == LOAD_DEREF else x for x in co.code]

		for fv, cell in zip(co.freevars, repl.func_closure):
			unmangled = fv
			fv = mangle_name(fv)
			target.func_globals.update({fv: cell.cell_contents})

	co.freevars = []

	for i, obj in enumerate(target.func_code.co_freevars):
		co.freevars.append(str(uuid.uuid4()))

	target.func_code = co.to_code()

	if target.func_closure and repl.func_closure and len(target.func_closure) <= len(repl.func_closure):
		__add_unstubbed_function(target, closure=repl.func_closure)
	else:
		__add_unstubbed_function(target, closure=target.func_closure)

	target.unstub = unstub
	get_stubbed().append(target)

	return target

def stub_attributes(target, **attributes):
	"""Stub out old attribute values on `target` with new ones.

	The strategy is to subclass the class of `target` in order to add
	a stubbing property that returns the new value for the attribute.

	Each stubbed-out attribute has `unstubbed` and `unstub` functions that
	allow access to the original value of the attribute as well as enabling
	fine-grained control of which attributes are stubbed.

	>>> from stub import stub
	>>> class A(object):
	...     def __init__(self):
	...         self.x = 5
	...
	>>> a = A()
	>>> stub(a, x=6)
	>>> a.x
	6
	>>> a.x.unstubbed()
	5

	.. note::

		Additional stubbing of attributes will simply add more property
		descriptors to the same subclass.

	.. warning::
		It is an error to attempt to stub out attributes on instances of
		old-style classes. A ``TypeError`` will be raised if this occurs.

	.. warning::

		It is an error to supply keyword arguments that do not match attributes
		of `target`. A ``TypeError`` will be raised if this occurs.
	"""

	if type(target.__class__) != TypeType: # This is not a new-style class
		raise TypeError('Stubbing attributes is not supported on old-style classes')

	if [a for a in attributes if a not in dir(target)]: # One or more of the attributes to be stubbed are not "real"
		raise TypeError('Stubbing simulated attributes is not supported')

	if '_subtype' not in target.__class__.__name__:
		target._old_class = target.__class__

		def unstub(self):
			target.__class__ = target._old_class
			if '_subtype' not in target.__class__.__name__:
				_modified_objects.remove(target)

		klass = new.classobj('%s_subtype' % type(target).__name__, (type(target),), {'unstub': unstub})
		target.__class__ = klass

		# Make sure calls to unstub_all will restore this object
		_modified_objects.append(target)
	else:
		klass = target.__class__

	# We have builders for a bunch of functions so that the definition of
	# those functions doesn't close over the variables used here.

	# We have an unstub builder so that the definition of `unstub`
	# doesn't close over `klass` and `aname`
	def unstub_builder(kl, name):
		def unstub(self):
			delattr(kl, name)
		return unstub

	# We have a getter builder so that the definition of the
	# getter doesn't close over `avalue`
	def getter_builder(x):
		def getter(self):
			return x
		return getter

	def unstubbed_builder(name):
		def unstubbed(self):
			if name in target._old_class.__dict__:
				return target._old_class.__dict__[name].__get__(target, target._old_class)
			elif hasattr(target._old_class, name):
				return getattr(target._old_class, name).fget
			else:
				return target.__dict__[name]
		return unstubbed

	for aname, avalue in attributes.items():
		vklass = new.classobj('%s_replacement' % type(avalue).__name__, (type(avalue),), {'unstubbed': unstubbed_builder(aname), 'unstub': unstub_builder(klass, aname)})
		avalue = vklass(avalue)
		setattr(klass, aname, property(getter_builder(avalue)))

def stub(target, *repl, **attributes):
	"""Stub out callable objects and/or attributes on objects.

	Call `unstub` on the object/attribute to remove the stubbing behaviour;
	the `unstubbed` function on the callable calls through to the original
	function code.

	.. warning::

		It is an error to attempt to provide both a `repl` function *and*
		`attributes` to be stubbed. A ``ValueError`` will be raised if this
		occurs.

	.. warning::

		It is an error to provide neither a `repl` function nor `attributes` to
		be stubbed. A ``ValueError`` will be raised if this occurs.

	"""
	if repl and attributes:
		raise ValueError('You cannot stub both the function code and the attribute access for an object in the same operation')

	if repl: # We are trying to stub the implementation of a callable
		repl = repl[0]

		if hasattr(target, 'im_self'): # We are trying to stub out a bound function
			return stub_bound_function(target, repl)
		elif hasattr(target, 'func_code'): # We are trying to stub out an unbound function
			return stub_unbound_function(target, repl)
	elif attributes: # We are trying to stub the access to one or more attributes
		stub_attributes(target, **attributes)
	else: # People are crazy and shouldn't be allowed to run with sharp objects
		raise ValueError('You must provide a replacement function or attribute value')

def unstub_all():
	'Unstubs all stubbed functions and objects'

	for obj in get_stubbed()[:] + _modified_objects[:]:
		while hasattr(obj, 'unstub'):
			obj.unstub()

def same_args(f_tocopy):
	def decorator(f_target):
		from byteplay import Code

		co = Code.from_code(f_target.func_code)
		co.args, co.varargs, co.varkwargs, defaults = getargspec(f_tocopy)

		co.varargs = 1 if co.varargs else 0
		co.varkwargs = 1 if co.varkwargs else 0

		if f_target.func_closure:
			f = new.function(co.to_code(), f_tocopy.func_globals, argdefs=defaults, closure=f_target.func_closure)
		else:
			f = new.function(co.to_code(), f_tocopy.func_globals, argdefs=defaults)

		return f
	return decorator

from stubbing.expect import CallExpecterMixin