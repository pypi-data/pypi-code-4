from hk2.kernel.interfaces import IPluginLoader
from hk2.kernel.module_scanner import ModuleScanner

import sys

#===========================================================

class SysmodPluginLoader(IPluginLoader):
    """Scans currently imported modules"""
    def getPlugins(self):
        return sys.modules.keys()

    def scanPlugins(self):
        scanner = ModuleScanner()
        modules = []
        contracts = []
        services = []

        for m in list(sys.modules.itervalues()):
            if m:
                c, s = scanner.scan(m)
                if c or s:
                    modules.append(m)
                    contracts.extend(c)
                    services.extend(s)

        return modules, contracts, services
