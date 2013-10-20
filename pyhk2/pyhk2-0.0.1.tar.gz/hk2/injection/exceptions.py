from internal import internal

#===========================================================

class InjectionError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

#===========================================================

class DeepInjectionError(InjectionError):
    def __init__(self, msg, ctx, while_resolving=None):
        nmsg = "%s.\nInjection path:\n%s" % (msg, self.getPath(ctx, while_resolving))
        InjectionError.__init__(self, nmsg)

    def getPath(self, ctx, while_resolving):
        path = self.getPathElems(ctx, while_resolving)

        ret = []
        for i, (ip, binding) in enumerate(path):
            ct = internal.className(ip.type)
            mult = '*' if ip.multi else ''
            resolv = " as '%s'" % (binding) if binding else ''
            ret.append("%d. Resolving %s%s%s" % (i + 1, ct, mult, resolv))
        return '\n'.join(ret)

    def getPathElems(self, ctx, while_resolving):
        resolve = []
        while ctx:
            resolve.append((ctx.resolving, ctx.binding))
            ctx = ctx.parent
        resolve = list(reversed(resolve))
        if while_resolving:
            resolve.append((while_resolving, None))
        return resolve
