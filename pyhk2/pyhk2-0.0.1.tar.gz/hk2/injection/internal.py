
#===========================================================

class internal(object):
    INJECT_ATTR = '__inject__'
    
    class raiseOnMissing(object):
        pass
    
    @staticmethod
    def className(c):
        return c.__module__ + '.' + c.__name__
