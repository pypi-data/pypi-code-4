# Copyright Matthew Henderson 2013.
# Created Tue Mar 26 10:02:38 GMT 2013
# Last updated: Tue Mar 26 10:51:51 GMT 2013

def extension(P, w, t, e):
    """
    If P is a (w,t,e)-KF-SPLS then this function returns an extension of P.
    In other words, if D is returned then P.update(D) is a
    (w+2, t-2, e)-KF-PLS.

    P - a KF-SPLS
    w - wing dimension
    t - tail dimension
    e - tether dimension
    """
    if w==4:
        return {5:2,6:5,13:5,14:6,21:1,22:8,29:6,30:7,33:2,34:5,35:1,\
                36:6,37:8,41:5,42:6,43:8,44:7,46:2}
    else:
        return {7:6,8:8,15:8,16:7,23:2,24:3,31:1,32:2,39:7,40:4,47:4,\
                48:1,49:6,50:8,51:2,52:1,53:7,54:4,55:3,57:8,58:7,59:3,\
                60:2,61:4,62:1,64:6}

def complete(P, w, t, e):
    """
    If P is a completable KF-SPLS then this function will return a completion
    of P. Raises an exception when P is incompletable.
    """
    if w==P.size():
        return P
    else:
        P.extend(extension(P, w, t, e))
        return complete(P, w + 2, t - 2, e)

