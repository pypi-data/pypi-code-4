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

import rlcompleter

from LMIReturnValue import LMIReturnValue
from LMIConstantValues import LMIConstantValues
from LMINamespace import LMINamespace
from LMINamespace import LMINamespaceRoot
from LMIClass import LMIClass
from LMIInstance import LMIInstance
from LMIInstanceName import LMIInstanceName
from LMIMethod import LMIMethod
from LMIConnection import LMIConnection

class LMICompleter(rlcompleter.Completer):
    """
    This LMIShell completer, which is used in the interactive mode, provides
    tab-completion for user friendliness.
    """
    LMI_CLASSES = (
        LMINamespace,
        LMIClass,
        LMIInstance,
        LMIInstanceName,
        LMIMethod,
        LMIConstantValues,
        LMIReturnValue
    )

    def __init__(self, namespace=None):
        """
        Constructs a LMICompleter object.

        Arguments:
            namespace -- dictionary, where to perform a completion. If unspecified, the
                default namespace where completions are performed is __main__ (technically,
                __main__.__dict__).
        """
        rlcompleter.Completer.__init__(self, namespace)
        self._last_complete = []

    def __complete_object_methods(self, obj, text):
        """
        Returns a list of strings of all object methods.

        Arguments:
            obj -- an object, on which the method completion is performed
            text -- string to be completed
        """
        result = filter(lambda m: not m.startswith("_") \
            and callable(getattr(obj, m)) \
            and m.lower().startswith(text), dir(obj))
        return result

    def __complete_object_properties(self, obj, text):
        """
        Returns a list of string of all object properties.

        Arguments:
            obj -- an object, on which the property completion is performed
            text -- string to be completed
        """
        result = filter(lambda m: not m.startswith("_") \
            and not callable(getattr(obj, m)) \
            and m.lower().startswith(text), dir(obj))
        return result

    def _callable_postfix(self, val, word):
        """
        Returns a string with opening parentheses, if the value provided is callable.

        Arguments:
            val -- object, which is checked, if it is callable
            word -- modified input string, which has opening parentheses appended
        """
        if hasattr(val, '__call__') and not isinstance(val, LMICompleter.LMI_CLASSES):
            word = word + "("
        return word

    def complete(self, text, state):
        """
        Returns a completed string.

        Arguments:
            text -- string to be completed.
            state -- order number of the completion, see rlcompleter
        """
        if not text:
            return ("\t", None)[state]
        if state > 0:
            return self._last_complete[state]
        self._last_complete = []
        members = text.split(".")
        if members[0] in self.namespace:
            cmd = ".".join(members[0:-1])
            to_complete = members[-1].lower()
            expr = eval(cmd, self.namespace)
            methods = self.__complete_object_methods(expr, to_complete)
            properties = self.__complete_object_properties(expr, to_complete)
            if isinstance(expr, (LMIConnection, LMINamespaceRoot)):
                for n in expr.namespaces:
                    if n.lower().startswith(to_complete):
                        self._last_complete.append(cmd + "." + n)
                methods = [x for x in methods if x not in expr.namespaces]
            elif isinstance(expr, LMINamespace):
                for c in expr.classes():
                    if c.lower().startswith(to_complete):
                        self._last_complete.append(cmd + "." + c)
            elif isinstance(expr, LMIClass):
                for v in expr.valuemap_properties():
                    if v.lower().startswith(to_complete):
                        self._last_complete.append(cmd + "." + v + "Values")
            elif isinstance(expr, LMIInstance):
                expr_methods = expr.methods()
                if expr_methods:
                    if to_complete and to_complete in "syn":
                        self._last_complete.append(cmd + ".Sync")
                    else:
                        sync_prefix = ""
                        if to_complete.startswith("sync"):
                            sync_prefix = "Sync"
                            to_complete = to_complete[4:]
                        for m in expr_methods:
                            if m.lower().startswith(to_complete):
                                self._last_complete.append(cmd + "." + sync_prefix + m + "(")
                        to_complete = sync_prefix + to_complete
                for p in expr.properties():
                    if p.lower().startswith(to_complete):
                        self._last_complete.append(cmd + "." + p)
            elif isinstance(expr, LMIInstanceName):
                for p in expr.key_properties():
                    if p.lower().startswith(to_complete):
                        self._last_complete.append(cmd + "." + p)
            elif isinstance(expr, LMIMethod):
                for p in expr.valuemap_parameters():
                    if p.lower().startswith(to_complete):
                        self._last_complete.append(cmd + "." + p + "Values")
            elif isinstance(expr, LMIConstantValues):
                for v in expr.values():
                    if v.lower().startswith(to_complete):
                        self._last_complete.append(cmd + "." + v)
            elif isinstance(expr, LMIReturnValue):
                for p in expr.properties():
                    if p.lower().startswith(to_complete):
                        self._last_complete.append(cmd + "." + p)
            self._last_complete.extend(cmd + "." + m + "(" for m in methods)
            self._last_complete.extend(cmd + "." + p for p in properties)
            return self._last_complete[state]
        return rlcompleter.Completer.complete(self, text, state)
