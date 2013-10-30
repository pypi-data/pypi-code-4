"""
	A collection of filesystem related commands.
"""
import os, re

def find( path, name_regex = None, include_dirs = True, include_files = True ):
	"""
		Creates an iterator of files.
		
		@param path: which path to iterate
		@param name_regex: optional regex string compared against basename of file
		@return: a generator for the matched files
	"""
	c_name_regex = re.compile(name_regex) if name_regex != None else None
	
	def check_name(name):
		if c_name_regex != None:
			return c_name_regex.match( name )
		return True
		
	walker = os.walk( path, followlinks = True )
	def filter_func():
		for root, dirs, files in walker:
			if include_dirs and check_name( os.path.basename(root) ):
				yield root
				
			if include_files:
				for item in filter(check_name,files):
					yield os.path.join( root, item )
	
	return filter_func()
