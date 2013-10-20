from hk2.kernel.interfaces import IPluginLoader
from hk2.kernel.module_scanner import ModuleScanner

import hk2.utils.func as fn

import os
import logging
log = logging.getLogger('hk2')

#===========================================================

PLUGIN_FILE = '__plugin__.py'

#===========================================================

class FilePluginLoader(IPluginLoader):
    def __init__(self, scan_dirs=None):
        self._import_root = os.path.abspath('.')
        self._scan_dirs = scan_dirs or []
        self._scan_files = []

        self._plugin_dirs = []
        self._moduleScanner = ModuleScanner()

    def addDir(self, path):
        if os.path.isdir(path):
            self._scan_dirs.append(path)

    def addAllInDir(self, path):
        dirs = [path] if isinstance(path, basestring) else path
        subdirs = [os.path.join(d, ls) for d in dirs for ls in os.listdir(d)]
        fn.foreach(self.addDir, subdirs)

    def addModuleFile(self, path):
        if self._isModuleCandidate(path):
            self._scan_files.append(path)

    def setImportRoot(self, path):
        self._import_root = os.path.abspath(path)

    def getPlugins(self):
        if len(self._plugin_dirs) == 0:
            self._plugin_dirs = self._searchPlugins()

        return self._plugin_dirs

    def scanPlugins(self):
        modules = []
        contracts = []
        services = []

        for p in self.getPlugins():
            for m in self._getPluginModules(p):
                module = self._loadModule(m)
                if module:
                    cts, svc = self._moduleScanner.scan(module)
                    if cts or svc:
                        modules.append(module)
                        contracts.extend(cts)
                        services.extend(svc)

        for m in self._scan_files:
            module = self._loadModule(m)
            if module:
                cts, svc = self._moduleScanner.scan(module)
                modules.append(module)
                contracts.extend(cts)
                services.extend(svc)

        return modules, contracts, services

    def _searchPlugins(self):
        return [d for d in self._scan_dirs if self._isPluginDir(d)]

    def _isPluginDir(self, path):
        pf = os.path.join(path, PLUGIN_FILE)
        return os.path.isfile(pf)

    def _getPluginModules(self, plugin_dir):
        candidate_modules = [os.path.join(plugin_dir, ld) for ld in os.listdir(plugin_dir)]
        return [cm for cm in candidate_modules if self._isModuleCandidate(cm)]

    def _isModuleCandidate(self, path):
        _d, fn = os.path.split(path)
        base, ext = os.path.splitext(fn)
        return os.path.isfile(path) and not base.startswith('__') and ext == '.py'

    def _loadModule(self, module_path):
        module_import = self._pathToImport(module_path)
        try:
            module = __import__(module_import)
            module = self._navigateToModule(module_import, module)
            return module
        except:
            log.exception("Error wile scanning module '%s'" % (module_import))
            return None

    def _pathToImport(self, path):
        absp = os.path.abspath(path)
        rel = os.path.relpath(absp, self._import_root)
        return os.path.splitext(rel)[0].replace(os.sep, '.')

    def _navigateToModule(self, import_path, root):
        navi = import_path.split('.')
        if len(navi) == 1:
            return root
        module = root
        for n in navi[1:]:
            module = module.__dict__[n]
        return module
