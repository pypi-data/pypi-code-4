

class check(object):

    """
    Wrap function in try/except
    
    Return True with error message (with prefix) if raise Exception, otherwise return False and empty string
    """

    def __init__(self, prefix):
        self.prefix = prefix

    def __call__(self, fn):

        def wrapped(*args):
            try:
                fn(*args)
            except Exception, e:
                return True, '<b>%s:</b> %s' % (self.prefix, e)
            else:
                return False, ''

        return wrapped
