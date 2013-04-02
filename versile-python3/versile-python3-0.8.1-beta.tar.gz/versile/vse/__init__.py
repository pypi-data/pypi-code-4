# Copyright (C) 2011 Versile AS
# 
# This file is part of Versile Python.
# 
# Versile Python is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.
#
# Other Usage
# Alternatively, this file may be used in accordance with the terms
# and conditions contained in a signed written agreement between you
# and Versile AS.
#
# Versile Python implements Versile Platform which is a copyrighted
# specification that is not part of this software.  Modification of
# the software is subject to Versile Platform licensing, see
# https://versile.com/ for details. Distribution of unmodified
# versions released by Versile AS is not subject to Versile Platform
# licensing.
#

"""Top module for :term:`VSE` framework implementation."""


from versile.internal import _vexport
from versile.common.util import VObjectIdentifier
from versile.orb.module import VModuleResolver

__all__ = ['VSEResolver']
__all__ = _vexport(__all__)


class VSEResolver(VModuleResolver):
    """Resolver for :term:`VSE` entities.
    
    :param modules: modules added to :term:`VSE` modules
    :type  modules: list, tuple
    
    """

    # Global configuration of lazy conversion to VArrayOf... types
    _lazy_arrays = False
    
    def __init__(self, modules=tuple()):
        mod_cls_list = self._load_modules()
        mods = []
        for ModCls in mod_cls_list:
            mods.append(ModCls())
        mods.extend(modules)
        super(VSEResolver, self).__init__(modules=mods)

    @classmethod
    def add_imports(cls):
        """Make all :term:`VSE` modules available as global imports."""
        cls._load_modules()

    @classmethod
    def lazy_arrays(cls):
        """Gets globally set lazy array conversion status.

        :returns: True if lazy conversion set, otherwise False
        :rtype:   bool
        
        """
        return cls._lazy_arrays

    @classmethod
    def enable_lazy_arrays(cls, status=True):
        """Enables or disables lazy arrays globally.

        :param status: if True enables lazy arrays, if False disables
        :type  status: bool
        
        Enabling lazy arrays causes
        :class:`versile.orb.entity.VEntity` lazy conversion to inspect
        elements of tuple structures for type and value, and when
        possible lazy convert to the appropriate VArrayOf... VSE
        type. Enabling or disabling lazy arrays takes effect globally.
        
        """
        cls._lazy_arrays = status
        
    @classmethod
    def _load_modules(cls):
        """Returns list of all :term:`VSE` module classes."""
        from versile.vse.container import VContainerModule
        from versile.vse.native.module import VNativeModule
        from versile.vse.stream import VStreamModule
        from versile.vse.util import VUtilityModule
        return (VContainerModule, VStreamModule, VNativeModule, VUtilityModule)
    
