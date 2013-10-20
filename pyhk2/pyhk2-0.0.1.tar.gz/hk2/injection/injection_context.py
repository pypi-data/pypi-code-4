from internal import internal
from injectors import InjectorFactory
from exceptions import InjectionError, DeepInjectionError

import logging
log = logging.getLogger('hk2')

#===========================================================

class InjectionContext(object):
    def __init__(self, bindings, binding, resolving, parent=None):
        """:type bindings: Bindings"""
        log.debug("Resolving dependencies for '%s'", binding)

        self.binds = bindings
        self.binding = binding
        self.resolving = resolving
        self.parent = parent

        self.checkCyclic()

        self.activator = binding.activator
        self.injectors = InjectorFactory.getInstanceInjectors(binding)

        self.activator_deps = self.collectDependencies(self.activator)
        self.other_deps = [self.collectDependencies(inj) for inj in self.injectors]

    def activate(self):
        log.debug("Activating the '%s'", self.binding)

        activator_deps = self.activateDependencies(self.activator_deps)
        inst = self.binding.scope.get(self.binding, activator_deps)
        self.inject(inst)

        log.debug("'%s' activated as '%s'", self.binding, inst)
        return inst

    def inject(self, inst):
        other_deps = [self.activateDependencies(deps) for deps in self.other_deps]
        for inj, deps in zip(self.injectors, other_deps):
            inj.inject(inst, deps)

    def collectDependencies(self, injector):
        ips = injector.getDependencies()

        deps = []
        for ip in ips:
            try:
                if not ip.multi:
                    bound = self.binds.get(ip.type)
                    ctx = InjectionContext(self.binds, bound, ip, self)
                    deps.append((ip, ctx))
                else:
                    bound = self.binds.getAll(ip.type)
                    ctxz = [InjectionContext(self.binds, b, ip, self) for b in bound]
                    deps.append((ip, ctxz))
            except DeepInjectionError:
                raise
            except InjectionError, iex:
                raise DeepInjectionError(iex.message, self, ip)

        return deps

    def activateDependencies(self, deps):
        ret = []
        for ip, dep in deps:
            if not ip.multi:
                ret.append(dep.activate())
            else:
                ret.append([ctx.activate() for ctx in dep])
        return ret

    def checkCyclic(self):
        ctx = self.parent
        while ctx:
            if self.resolving.type == ctx.resolving.type:
                raise DeepInjectionError("Cyclic dependency on '%s'"
                                         % (internal.className(self.resolving.type)), self)
            ctx = ctx.parent
