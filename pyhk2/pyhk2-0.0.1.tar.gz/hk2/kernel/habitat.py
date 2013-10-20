from interfaces import IStartup

from hk2.injection import Container, NoScope
from plugin_loaders.sysmod_plugin_loader import SysmodPluginLoader

from hk2.annotations import Service
from hk2.types import Annotations

import logging
log = logging.getLogger('hk2')

#===========================================================

class Habitat(object):
    def __init__(self, plugin_loader=None):
        """
        :type plugin_loader: IPluginLoader
        """
        log.debug("Initializing Habitat")

        self._loader = plugin_loader or SysmodPluginLoader()
        self._ioc = Container()
        self._services = set()
        self._contracts = set()
        self._servicesToContracts = {}

        self._scan()
        self._regInIoC()

    def _scan(self):
        _m, c, s = self._loader.scanPlugins()
        self._contracts = set(c)
        self._services = set(s)

        # Predefined
        self._contracts.add(IStartup)

        self._servicesToContracts = {}
        for s in self._services:
            cts = self._getServiceContracts(s, self._contracts)
            if not cts:
                raise Exception("Service '%s' does not implement any contracts" % (s))
            self._servicesToContracts[s] = cts

    def _regInIoC(self):
        self._ioc.bind(Habitat, self)

        for s, cts in self._servicesToContracts.iteritems():
            [annot] = filter(lambda x: isinstance(x, Service), Annotations.getAnnotations(s))
            scope = annot.scope or NoScope
            scope = scope()
            
            for c in cts:
                self._ioc.bind(c, s, scope)

    def _getServiceContracts(self, svc, contracts):
        return [c for c in contracts if issubclass(svc, c)]

    def getByContract(self, contract):
        return self._ioc.get(contract)

    def getAllByContract(self, contract):
        return self._ioc.getAll(contract)

    def getAllContracts(self):
        return self._contracts

    def getServicesByContract(self, contract):
        ret = []
        for s, c in self._servicesToContracts.iteritems():
            if contract in c:
                ret.append(s)
        return ret
