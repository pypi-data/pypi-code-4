from echo import users
from pprint import pprint

# Get an existing user URL...
user_d = users.get("http://connect-uat.nj.com/user/amurphre/index.html")
pprint(user_d, indent=4)

# Show poco account #0:
account_d = user_d['poco']['entry']['accounts'][0]
print
pprint(account_d, indent=4)

# Convert poco account #0 into User object:
class User(object):
    def __init__(self, user_json):
        try:
            account_d = user_d['poco']['entry']['accounts'][0]
            for k,v in account_d.items():
                setattr(self,  k, v)
        except:
            pass

print
u = User(user_d)
print dir(u)
print

# Update or insert a "poco" user...
poco_d = {'poco': {'totalResults': 1, 'startIndex': 0, 'itemsPerPage': 1, 'entry': {'accounts': [{'username': 'John', 'identityUrl': 'http://example.com/users/john', 'emails': [{'primary': 'true', 'value': 'johnQpublic@example.com'}]}, {'identityUrl': 'http://john.foobar.com/'}], 'id': 'f4062c6a6cef2a871161c5974f1daf0d'}}, 'echo': {'state': 'Untouched'}}

r = users.update("http://example.com/users/john", "poco", poco_d['poco'])
print "Updated POCO record for user..."
pprint(r)
print

