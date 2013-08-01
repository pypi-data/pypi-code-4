import gc
import sys
import cffi

def make_callback():
    container = [data]
    callback = ffi.callback('int()', lambda: len(vars(container)))
    container.append(callback)
    # Ref cycle: callback -> lambda (closure) -> container -> callback
    return callback

ffi = cffi.FFI()
data = 'something'
initial_refcount = sys.getrefcount(data)
callback = make_callback()
assert sys.getrefcount(data) == initial_refcount + 1
del callback
gc.collect()
assert sys.getrefcount(data) == initial_refcount  # Fails, data is leaked
