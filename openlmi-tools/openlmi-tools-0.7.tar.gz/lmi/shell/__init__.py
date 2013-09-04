# Copyright (C) 2012-2013 Peter Hatina <phatina@redhat.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""
LMIShell
"""

__version__ = "0.7"

from LMIExceptions import *
from LMIUtil import LMIPassByRef
from LMIIndication import LMIIndication
from LMIIndicationListener import LMIIndicationListener
from LMIReturnValue import LMIReturnValue
from LMIBaseClient import LMIBaseClient
from LMIShellClient import LMIShellClient
from LMIShellConfig import LMIShellConfig
from LMIShellOptions import LMIShellOptions
from LMISubscription import LMISubscription
from LMINamespace import LMINamespace
from LMINamespace import LMINamespaceRoot
from LMIConstantValues import LMIConstantValues
from LMIClass import LMIClass
from LMIInstanceName import LMIInstanceName
from LMIMethod import LMIMethod
from LMIInstance import LMIInstance
from LMIConnection import LMIConnection

from LMIConnection import connect

# Register LMI wrapper classes into a LMIObjectFactory  to avoid circular dependency
# between those classes.
from LMIObjectFactory import LMIObjectFactory
LMIObjectFactory().register(LMINamespace)
LMIObjectFactory().register(LMINamespaceRoot)
LMIObjectFactory().register(LMIClass)
LMIObjectFactory().register(LMIInstance)
LMIObjectFactory().register(LMIInstanceName)
LMIObjectFactory().register(LMIMethod)

# LMIConsole depends on LMIObjectFactory and needs to be imported after
# LMIObjectFactory has all wrapper classes registered.
from LMIConsole import LMIConsole
