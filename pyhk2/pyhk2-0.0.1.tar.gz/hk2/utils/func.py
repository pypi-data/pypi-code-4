
#===========================================================
# Lambdas
#===========================================================

def get_el(i):
    def _getter_(x):
        return x[i]
    return _getter_

def get_attr(n):
    def _getter_(x):
        return getattr(x, n)
    return _getter_

#===========================================================
# Iteration
#===========================================================

def foreach(f, seq):
    for el in seq:
        f(el)

def count(seq, pred=None):
    c = 0
    for i in seq:
        if not pred or pred(i):
            c += 1
    return c

#===========================================================
# Mutation
#===========================================================

def group_by(key, seq, val=None):
    ret = {}
    val = val or (lambda x: x)
    for el in seq:
        k = key(el)
        l = ret.get(k, [])
        l.append(val(el) if val else el)
        ret[k] = l
    return ret

