from echo import items
from echo import eql

# Sample EQL Query
query_eql= eql.Query("http://blog-uat.nj.com/")

print "Search Query for items..."
print items.search(query_eql)
print

print "Count Query for items..."
print items.count(query_eql)
print

# Using eql.Query:
uri_path="http://blog-uat.nola.com/"
print "eql.Query to items..."
q = eql.Query(uri_path, uri_filter='scope')
print repr(q)
print items.search(q)
print

