"""
Usefull profiling decorators and WSGI middleware.
"""
__all__ = ['timecall', 'wsgi_profile', 'memory_profile', 'line_profile', 'coverage']

from functools import wraps
from logging import info

try:
    from linesman.middleware import make_linesman_middleware as wsgi_profile
except ImportError:
    pass

try:
    from memory_profiler import profile as memory_profile
except ImportError:
    pass

try:
    from line_profiler import profile as line_profile
except ImportError:
    try:
        from pprofile import Profile

        def line_profile(f, match = None):
            @wraps(f)
            def wrapper(*args, **argd):
                try:
                    profiler = Profile()
                    with profiler:
                        return f(*args, **argd)
                finally:
                    fdict = profiler.file_dict
                    for path in fdict.iterkeys():
                        if 'python' in path:
                            del fdict[path]
                    profiler.print_stats()
            return wrapper
    except ImportError:
        pass

try:
    from profilehooks import profile
except ImportError:
    try:
        from pstats import Stats

        try:
            from cProfile import Profile
        except ImportError:
            from profile import Profile

        def profile(f, immediate = True):
            @wraps(f)
            def wrapper(*args, **argd):
                profiler = Profile()
                try:
                    profiler.enable()
                    return f(*args, **argd)
                finally:
                    profiler.disable()
                    stats = Stats(profiler)
                    stats.strip_dirs()
                    stats.sort_stats('cumulative')
                    stats.print_stats(f.__name__)
            return wrapper
    except ImportError:
        pass

try:
    from profilehooks import timecall
except ImportError:
    from time import time
    def timecall(f, immediate = True):
        @wraps(f)
        def wrapper(*args, **argd):
            try:
                start = time()
                return f(*args, **argd)
            finally:
                print "Execution time: %s s (%s)" % (time() - start, f)
        return wrapper

try:
    from profilehooks import coverage
except ImportError:
    pass
