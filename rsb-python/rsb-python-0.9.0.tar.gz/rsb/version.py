__version__ = '0.9.0'
__commit__ = 'g6cfa45b'

def getVersion():
    """
    Returns a descriptive string for the version of RSB.
    """
    return "%s-%s" % (__version__, __commit__)
