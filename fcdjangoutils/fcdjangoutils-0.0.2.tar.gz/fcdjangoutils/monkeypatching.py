def patch(cls):
    def patch(fn):
        setattr(cls, fn.func_name, fn)
    return patch

