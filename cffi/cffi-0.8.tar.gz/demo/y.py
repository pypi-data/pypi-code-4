import cffi

ffi = cffi.FFI()

ffi.new("char[]", 4)
