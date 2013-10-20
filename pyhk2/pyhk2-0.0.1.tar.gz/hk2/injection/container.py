from bindings import Bindings, InstanceBinding
from injection_context import InjectionContext
from exceptions import InjectionError
from internal import internal
from inject import inject_param, allof
from scopes import NoScope

import logging
log = logging.getLogger('hk2')

#===========================================================

class Container(object):
    def __init__(self, bindings=None):
        self._binds = bindings or Bindings()

    def bind(self, what, to=None, scope=None):
        return self._binds.bind(what, to, scope)

    def get(self, what, default=internal.raiseOnMissing):
        ret = default
        try:
            log.debug("Resolving '%s'", what)

            ip = inject_param(what)
            bound = self._binds.get(what)

            ctx = InjectionContext(self._binds, bound, ip)
            ret = ctx.activate()
        except InjectionError:
            if default == internal.raiseOnMissing:
                raise

        log.debug("IoC '%s' resolved to '%s'", what, ret)
        return ret

    def getAll(self, what):
        log.debug("Resolving all '%s'", what)

        ip = inject_param(allof(what))
        bound = self._binds.getAll(what)

        ctxz = [InjectionContext(self._binds, b, ip) for b in bound]
        ret = [ctx.activate() for ctx in ctxz]

        log.debug("IoC '%s' resolved to '%s'", what, ret)
        return ret

    def inject(self, into):
        log.debug("Injecting dependencies into '%s'", into)
        ip = inject_param(into.__class__)
        ctx = InjectionContext(self._binds, InstanceBinding(into, NoScope), ip)
        ctx.inject(into)
