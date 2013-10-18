from echo import items
from echo.items.mux_api import MuxRequest
from pprint import pprint

# sample EQL string
query_eql="scope:http://blog-uat.nj.com/*"

# "Search Query for items..."
search = MuxRequest(query_eql)

# "Count Query for items..."
count = MuxRequest(query_eql, api_method='count')

# Form list of them for Mux API...
requests = [ search, count ]

print "Mux API requests..."
print items.mux(requests)
print

