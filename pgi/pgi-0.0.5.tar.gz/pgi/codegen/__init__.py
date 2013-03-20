# Copyright 2012,2013 Christoph Reiter
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

BACKENDS = []

try:
    from pgi.codegen.cffi_backend import CFFIBackend
except ImportError:
    pass
else:
    BACKENDS.append(CFFIBackend)

from pgi.codegen.ctypes_backend import CTypesBackend
BACKENDS.append(CTypesBackend)

ACTIVE_BACKENDS = BACKENDS[:]


def set_backend(name=None):
    """Set a prefered ffi backend (cffi, ctypes).

    set_backend() -- default
    set_backend("cffi") -- cffi first, others as fallback
    set_backend("ctypes") -- ctypes first, others as fallback
    """

    possible = list(BACKENDS)
    if name is None:
        names = []
    else:
        names = name.split(",")
    for name in reversed(names):
        for backend in BACKENDS:
            if backend.NAME == name:
                possible.remove(backend)
                possible.insert(0, backend)
                break
        else:
            raise LookupError("Unkown backend: %r" % name)

    ACTIVE_BACKENDS[:] = possible
