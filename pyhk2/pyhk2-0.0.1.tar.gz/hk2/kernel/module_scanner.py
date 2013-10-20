from hk2.types import Annotations
from hk2.annotations import Contract, Service

from interfaces import IModuleScanner

import logging
log = logging.getLogger('hk2')

#===========================================================

class ModuleScanner(IModuleScanner):
    def scan(self, module):
        contracts = [c for c, a in Annotations.getAnnotatedClasses(module, Contract)]
        services = [c for c, a in Annotations.getAnnotatedClasses(module, Service)]
        return contracts, services
