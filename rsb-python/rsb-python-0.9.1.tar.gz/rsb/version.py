__version__ = '0.9.1'
__commit__ = 'g0321f20'

def getVersion():
    """
    Returns a descriptive string for the version of RSB.
    """
    return "%s-%s" % (__version__, __commit__)
