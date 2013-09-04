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

class LMIDeletedObjectError(Exception):
    """
    Raised, when there is an attempt to access properties on deleted LMIInstance object.
    """

class LMIUnknownParameterError(Exception):
    """
    Raised, when there is a method call issued and unknown method parameter is provided.
    """

class LMIUnknownPropertyError(Exception):
    """
    Raised, when there is an attempt to create instance with unknown property provided.
    """

class LMIMethodCallError(Exception):
    """
    Raised, when an error occurs within method call.
    """

class LMISynchroMethodCallError(Exception):
    """
    Raised, when an error occurs within synchronized method call.
    """

class LMISynchroMethodCallFilterError(Exception):
    """
    Raised, when the LMIShell can not find necessary static filter for synchronous method call.
    """

class LMINoPagerError(Exception):
    """
    Raised, when tere is no default pager like less or more.
    """

class LMIIndicationError(Exception):
    """
    Raised, if an error occurs while subscribing to/removing an indication.
    """

class LMIIndicationListenerError(Exception):
    """
    Raised, if there is an error while starting/stopping indication listener.
    """

class LMIHandlerNamePatternError(Exception):
    """
    Raised when the pattern string does not contain minimum
    replacable characters.
    """

class LMIFilterError(Exception):
    """
    Raised, when a filter error occurs, mostly when filter object is missing.
    """

class LMIClassNotFound(AttributeError):
    """
    Raised, when trying to access missing class in cim namespace.
    """
    def __init__(self, namespace, class_name):
        AttributeError.__init__(self, 'no such class "%s" in "%s" namespace' %
                (class_name, namespace))

class LMINamespaceNotFound(AttributeError):
    """
    Raised, when trying to access not existing namespace from connnection
    or namespace object.
    """
    def __init__(self, namespace, *args):
        AttributeError.__init__(self, 'no such namespace "%s"' %
                "/".join([namespace] + list(args)))

