
from spyne.util.xml import parse_schema_file

print parse_schema_file('XMLSchema.xsd', files={'http://www.w3.org/XML/1998/namespace': 'xml.xsd'})
