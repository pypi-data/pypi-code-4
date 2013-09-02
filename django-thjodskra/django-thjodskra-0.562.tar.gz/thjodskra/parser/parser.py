#encoding: utf-8
import sys
from .dates import ssn2dob

def parse( line, definition, lang='en' ):
	module = sys.modules[__name__]
	f = getattr( module, 'parse_line_%s'%lang )
	return f( line, definition )

def fixdob( data, dob_field, ssn_field ):
	if data.has_key(dob_field) and data[dob_field] is None:
		data[dob_field] = ssn2dob( data[ssn_field] )
	return data
	
def parse_line_is( line, definition ):
	out = {}
	for key, en, length, f in definition:
		out[key] = f( line[:length].decode('iso-8859-1').encode('utf-8').strip() )
		line = line[length:]
	
	return fixdob( out, 'faedingardagur', 'kennitala' )

def parse_line_en( line, definition ):
	out = {}
	for isl, key, length, f in definition:
		out[key] = f( line[:length].decode('iso-8859-1').encode('utf-8').strip() )
		line = line[length:]
	
	return fixdob( out, 'date_of_birth', 'ssn' )