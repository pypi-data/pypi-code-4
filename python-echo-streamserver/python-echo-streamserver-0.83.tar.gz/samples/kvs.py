from echo import kvs

class Sample(object):
    value = 3.14

    def __repr__(self):
        return "Sample(%r)" % self.value

# Add a sample thing...
## thing = 3.14
thing = {'eat': 'food', 'pay': 15.00, 'sample': Sample(), }
key = u'mine'
print "put result: %r" % kvs.put(key, thing)

# Read that thing...
got_thing = kvs.get(key)
print "What's the sample value? %r" % got_thing['sample'].value
print "get result: %r is %r" % (type(got_thing), got_thing)

# Delete that thing...
print "delete result: %r" % kvs.delete(key)

# Is it really gone? Read that thing...
print "Is deleted thing gone? get: %r" % kvs.get(key, raise_not_found=False)

