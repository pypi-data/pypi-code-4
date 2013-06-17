# Celestial Software Getopt wrapper for old getopt
import Csys, os, os.path, sys, re, stat

__version__ = "0.1"

__doc__ = (
'''
Wrapper for old getopt similar to the perl Getopts.pm
''')

from getopt import getopt

class _OldOption(Csys.CSClass): #{
	_attributes = dict(
		key		= '',
		val		= False,
		isBool	= True,
	)
	def __init__(self, key, isBool): #{
		'''opt is a tuple'''
		Csys.CSClass.__init__(self)
		self.key = key
		self.isBool = isBool
		if not isBool: self.val = []
	#}
#} _OldOption

class Getopts(Csys.CSClassBase): #{
	def __init__(self, optstring, args=None): #{
		if args is None: args = sys.argv[1:]
		# This one must be set first
		cols = self._cols = {}
		self.argsIn = args[:]
		self.optstring = optstring
		i = 0
		while i < len(optstring): #{
			chr = optstring[i]
			try: #{{
				isBool = optstring[i+1] != ':'
			#}
			except IndexError: #{
				isBool = True
			#}}
			i += 2 - int(isBool)
			option = cols[chr] = _OldOption(chr, isBool)
		#}
		(opts, args) = getopt(args, optstring)
		self.args = args
		options = {}
		for opt, val in opts: #{
			opt = opt[1:]
			option = cols[opt]
			if option.isBool: #{{
				option.val = True
			#}
			else: #{
				option.val.append(val)
			#}}
		#}
	#} __init__

	def __getattr__(self, name): #{
		if name.startswith('_'): return self.__dict__.get(name)
		cols = self._cols
		try: #{{
			attr = self._cols[name]
			return attr.val
		#}
		except IndexError: #{
			raise AttributeError
		#}
	#} __getattr__

	def __setattr__(self, name, val): #{
		if name.startswith('_'): #{
			object.__setattr__(self, name, val)
			return
		#}
		attr = self._cols.get(name)
		if attr is None: #{
			object.__setattr__(self, name, val)
		#}
		elif not hasattr(attr, 'isBool'): #{
			object.__setattr__(self, name, val)
		#}
		elif attr.isBool: #{
			attr.val = val
		#}
		else: #{
			attr.val.append(val)
		#}
	#} __setattr__

	def __delattr__(self, name): #{
		cols = self.__dict__
		if name in cols['_cols']: #{
			del cols['_col'][name]
		#}
		elif name in self.__dict__: #{
			del self.__dict__[name]
		#}
		else: #{
			raise AttributeError
		#}}

	#} __getattr__

	def update(self, otherOptions): #{
		self._cols.update(otherOptions._cols)
	#} update

#} class Getopts

if __name__ == '__main__': #{
	testargs = ['-v', '-ps10', '-ps12', '/etc/termcap', '/etc/passwd']
	options = Getopts('nNo:vVp:P:', testargs)
	print options.dumpAttrs()
	print 'opt_v: ', options.v
	print 'opt_p: ', options.p
	print options.args
	# logger.write('%s', opts.dumpAttrs())
	sys.exit(0)
#}


