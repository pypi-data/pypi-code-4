try:
    profile
except NameError:
    def profile(func):
        try:
            from cProfile import Profile
        except ImportError:
            from profile import Profile

        import functools

        @functools.wraps(func)
        def wrapper(*args, **argd):
            prof = Profile()
            try:
                return prof.runcall(func, *args, **argd)
            finally:
                prof.print_stats()

        return wrapper
