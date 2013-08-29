from twisted.internet import defer


def branch_df(df):
    """Return a deferred which fires with the values that `df` fires, yet
    whose return values don't affect `df`'s chain. Mostly used with
    @defer.inlineCallbacks, since yielding a deferred inside an inlined
    generator kills its value."""
    branch = defer.Deferred()
    def dfDone(val):
        branch.callback(val)
        return val
    def dfFail(fail):
        branch.errback(fail)
        return fail
    df.addCallbacks(dfDone, dfFail)
    return branch
