#encoding: utf-8
import sys

def parse( line, definition, lang='en' ):
	module = sys.modules[__name__]
	f = getattr( module, 'parse_line_%s'%lang )
	return f( line, definition )
	
def parse_line_is( line, definition ):
	out = {}
	for key, en, length, f in definition:
		out[key] = f( line[:length].decode('iso-8859-1').encode('utf-8').strip() )
		line = line[length:]
	return out

def parse_line_en( line, definition ):
	out = {}
	for isl, key, length, f in definition:
		out[key] = f( line[:length].decode('iso-8859-1').encode('utf-8').strip() )
		line = line[length:]
	return out