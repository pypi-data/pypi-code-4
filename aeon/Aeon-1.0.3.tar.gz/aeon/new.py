from functools import wraps

class FooClass(object):
    def fooMethod(self, fn):
        def decorator(fn):
            @wraps(fn)
            def decorated_function(*args, **kwargs):
                print "1"
                ret = fn(*args, **kwargs)
                print "2"
                return ret
            return decorated_function
        return decorator

foo = FooClass()

@foo.fooMethod()
def hello():
    print "hello"

print hello()
