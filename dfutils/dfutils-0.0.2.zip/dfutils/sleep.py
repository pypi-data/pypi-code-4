from twisted.internet import defer


def ensure_reactor(reactor):
    """Given None, import and return reactor from twisted.internet.
    Otherwise, return the argument."""
    if reactor: return reactor

    from twisted.internet import reactor
    return reactor

    
def sleep_df(secs, reactor=None):
    """Return a Deferred which fires in the given number of seconds."""
    reactor = ensure_reactor(reactor)
    
    df = defer.Deferred()     
    reactor.callLater(secs, df.callback, None)
    return df
