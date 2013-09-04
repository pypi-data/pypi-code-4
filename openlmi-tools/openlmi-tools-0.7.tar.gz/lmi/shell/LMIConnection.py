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

import os
import sys
import atexit
import pywbem
import readline
import urlparse

import OpenSSL.SSL

from LMIBaseClient import LMIBaseClient
from LMIShellClient import LMIShellClient
from LMINamespace import LMINamespaceRoot
from LMIInstance import LMIInstance
from LMIReturnValue import LMIReturnValue
from LMISubscription import LMISubscription

from LMIExceptions import LMIIndicationError

from LMIUtil import lmi_raise_or_dump_exception
from LMIUtil import lmi_get_use_exceptions
from LMIUtil import lmi_set_use_exceptions

def __lmi_raw_input(prompt, use_echo=True):
    """
    Reads a string from the standard input.

    Arguments:
        prompt -- string with a prompt before the input begins
        use_echo -- bool flag, which indicates, if to echo the input on the command line
    """
    if not sys.stdout.isatty() and sys.stderr.isatty():
        # read the input with prompt printed to stderr
        def get_input(prompt):
            sys.stderr.write(prompt)
            return raw_input()
        stream = sys.stderr
    else:
        # read the input with prompt printed to stdout
        # NOTE: raw_input uses stdout only if the readline module is imported
        get_input = raw_input
        stream = sys.stdout
    if not sys.stderr.isatty() and not sys.stdout.isatty():
        LOG.warn('both stdout and stderr are detached from terminal,'
            ' using stdout for prompt')
    if not use_echo:
        os.system("stty -echo")
    try:
        result = get_input(prompt)
    except EOFError, e:
        if not use_echo:
            os.system("stty echo")
        stream.write("\n")
        return None
    except KeyboardInterrupt, e:
        if not use_echo:
            os.system("stty echo")
        raise e
    if not use_echo:
        os.system("stty echo")
        stream.write("\n")
    if result:
        cur_hist_len = readline.get_current_history_length()
        if cur_hist_len > 1:
            readline.remove_history_item(cur_hist_len - 1)

    return result

def connect(hostname, username="", password="", **kwargs):
    """
    Returns a LMIConnection object with provided hostname and credentials.

    Arguments:
        hostname -- uri of the CIMOM
        username -- account, under which, the CIM calls will be performed
        password -- user's password

    Keyword Arguments:
        interactive -- flag indicating, if the LMIShell client is running in the
            interactive mode; default value is False.
        use_cache -- flag indicationg, if the LMIShell client should use cache for
            CIMClass objects. This saves a lot's of communication, if there is
            often the LMIShellClient._get_class_names() or ._get_class() call
            issued. Default value is True.
        key_file -- string containing path to x509 key file; default value is None
        cert_file -- string containing path to x509 cert file; default value is None
        verify_server_cert -- flag indicating, whether a server side certificate
            needs to be verified, if SSL used; default value is True.
        prompt_prefix -- string prefixing username and password prompts in case
            the user is asked for credentials. Default value is empty string.
    """
    # Set remaining arguments
    interactive = kwargs.pop("interactive", False)
    use_cache = kwargs.pop("use_cache", True)
    key_file = kwargs.pop("key_file", None)
    cert_file = kwargs.pop("cert_file", None)
    verify_server_cert = kwargs.pop("verify_server_cert", True)
    prompt_prefix = kwargs.pop("prompt_prefix", "")
    if kwargs:
        raise TypeError("connect() got an unexpected keyword arguments: %s" % ", ".join(kwargs.keys()))

    connection = None
    netloc = urlparse.urlparse(hostname).netloc
    destination = netloc if netloc else hostname
    if os.getuid() == 0 and destination in ("localhost", "127.0.0.1", "::1") and \
            os.path.exists("/var/run/tog-pegasus/cimxml.socket") and \
            not username and not password:
        connection = LMIConnection(hostname, None, None, interactive=interactive,
            use_cache=use_cache, conn_type=LMIBaseClient.CONN_TYPE_PEGASUS_UDS,
            verify_server_cert=verify_server_cert)
        if not connection.verify_credentials():
            connection = None
    if connection is None:
        if interactive and not key_file and not cert_file:
            try:
                if not username:
                    username = __lmi_raw_input(prompt_prefix+"username: ", True)
                if not password:
                    password = __lmi_raw_input(prompt_prefix+"password: ", False)
            except KeyboardInterrupt, e:
                sys.stdout.write("\n")
                return None
        connection = LMIConnection(hostname, username, password, interactive=interactive,
            use_cache=use_cache, conn_type=LMIBaseClient.CONN_TYPE_WBEM,
            key_file=key_file, cert_file=cert_file, verify_server_cert=verify_server_cert)
        if not connection.verify_credentials():
            return None
    return connection

class LMIConnection(object):
    """
    Class representing a connection object. Each desired connection to separate CIMOM
    should have its own connection object created. This class provides an entry point to
    the namespace/classes/instances/methods hierarchy present in the LMIShell.
    """
    def __init__(self, hostname, username="", password="", **kwargs):
        """
        Constructs a LMIConnection object.

        Arguments:
            hostname -- uri of the CIMOM
            username -- account, under which, the CIM calls will be performed
            password -- user's password

        Keyword Arguments:
            interactive -- flag indicating, if the LMIShell client is running in the
                interactive mode; default value is False
            use_cache -- flag indicationg, if the LMIShell client should use cache for
                CIMClass objects. This saves a lot's of communication, if there is
                often the LMIShellClient._get_class_names() or ._get_class() call
                issued. Default value is True.
            conn_type -- type of connection; can be of 2 values:
                LMIBaseClient.CONN_TYPE_WBEM -- WBEM connection,
                LMIBaseClient.CONN_TYPE_PEGASUS_UDS -- applicable only for Tog-Pegasus
                    CIMOM, it uses unix socket for the connection; default value is
                    CONN_TYPE_WBEM
            key_file -- string containing path to x509 key file; default value is None
            cert_file -- string containing path to x509 cert file; default value is None
            verify_server_cert -- flag indicating, whether a server side certificate
                needs to be verified, if SSL used; default value is True
        """
        # Set remaining arguments
        interactive = kwargs.pop("interactive", False)
        use_cache = kwargs.pop("use_cache", True)
        conn_type = kwargs.pop("conn_type", LMIBaseClient.CONN_TYPE_WBEM)
        key_file = kwargs.pop("key_file", None)
        cert_file = kwargs.pop("cert_file", None)
        verify_server_cert = kwargs.pop("verify_server_cert", True)
        if kwargs:
            raise TypeError("__init__() got an unexpected keyword arguments: %s" % ", ".join(kwargs.keys()))

        self._client = LMIShellClient(hostname, username, password, interactive=interactive,
            use_cache=use_cache, conn_type=conn_type, key_file=key_file, cert_file=cert_file,
            verify_server_cert=verify_server_cert)
        self._indications = {}
        # Register LMIConnection.__unsubscribe_all_indications() to be called at LMIShell's exit.
        atexit.register(lambda: self.__unsubscribe_all_indications())

    def __repr__(self):
        """
        Returns a pretty string for the object.
        """
        return "%s(uri='%s', user='%s'...)" % (self.__class__.__name__,
            self._client.hostname, self._client.username)

    @property
    def hostname(self):
        """
        Property returning a CIMOM hostname.
        """
        return self._client._hostname

    @property
    def namespaces(self):
        """
        Property returning a list of all available namespaces from the LMIConnection
        object.
        """
        return ["root"]

    @property
    def root(self):
        """
        Property returning a LMINamespaceRoot object; root namespace object.
        """
        return LMINamespaceRoot(self)

    def print_namespaces(self):
        """
        Prints out all available namespaces.
        """
        sys.stdout.write("root\n")

    def clear_cache(self):
        """
        Clears the cache.
        """
        self._client._cache.clear()

    def use_cache(self, active=True):
        """
        Sets a bool flag, which defines, if the LMIShell should use a cache.

        Arguments:
            active -- bool flag, if the cache should be used
        """
        self._client._cache.active = active

    def verify_credentials(self):
        """
        Verifies credentials by performing a "dummy" GetClass() call on
        SomeNonExistingClass. Provided credentials are OK, if the LMIShell obtains
        CIMError exception with the flag CIM_ERR_NOT_FOUND set. Otherwise, the should
        receive AuthError. Returns True, if provided credentials are OK.
        """
        use_exceptions = lmi_get_use_exceptions()
        try:
            lmi_set_use_exceptions(True)
            self._client._get_class("SomeNonExistingClass")
        except pywbem.cim_operations.CIMError, e:
            if e.args[0] == pywbem.cim_constants.CIM_ERR_NOT_FOUND:
                return True
            lmi_raise_or_dump_exception(e)
            return False
        except pywbem.cim_http.AuthError, e:
            lmi_raise_or_dump_exception(e)
            return False
        except OpenSSL.SSL.Error, e:
            lmi_raise_or_dump_exception(e)
            return False
        finally:
            lmi_set_use_exceptions(use_exceptions)
        return True

    def subscribe_indication(self, **kwargs):
        """
        Subscribes to an indication. Indication is formed by 3 objects, where 2 of them
        (filter and handler) can be provided, if the LMIShell should not create those 2 by itself.
        The return type is LMIReturnValue with bool flag, which indicates, if the
        subscription was successful.

        Note: Currently the call registers atexit hook, which auto-deletes all subscribed
        indications by the LMIShell.

        Arguments:
            Filter -- if provided, the LMIInstance object will be used instead of
                creating a new one; optional
            Handler -- if provided, the LMIInstance object will be used instead of
                creating a new one; optional
            Query -- string containing a query for the indications filtering
            QueryLanguage -- string of a query language; eg. WQL, or DMTF:CQL
            Name -- string of indication name
            CreationNamespace -- string of the creation namespace
            SubscriptionCreationClassName -- string of the subscription object class name
            Permanent -- bool flag, if to preserve the created subscription on LMIShell's
                quit

        Arguments for filter object created by the LMIShell:
            FilterCreationClassName -- string of the creation class name of the filter object
            FilterSystemCreationClassName -- string of the system creation class name of the filter object
            FilterSourceNamespace -- string of a local namespace where the indications originate

        Arguments for handler object created by the LMIShell:
            HandlerCreationClassName -- string of the creation class name of the handler object
            HandlerSystemCreationClassName -- string of the system creation name of the handler object
            Destination -- string representing destination uri, where the indications should
                be delivered
        """
        try:
            cim_filter_provided = "Filter" in kwargs
            if cim_filter_provided:
                filt = kwargs["Filter"]
                cim_filter = None
                if isinstance(filt, LMIInstance):
                    cim_filter = filt._cim_instance
                elif isinstance(filt, pywbem.CIMInstance):
                    cim_filter = filt
                else:
                    errorstr = "Filter argument accepts instances of CIMInstance or LMIInstance"
                    lmi_raise_or_dump_exception(LMIIndicationError(errorstr))
                    return LMIReturnValue(rval=False, errorstr=errorstr)
            else:
                cim_filter_props = {
                    "CreationClassName" : kwargs["FilterCreationClassName"],
                    "SystemCreationClassName" : kwargs["FilterSystemCreationClassName"],
                    "SourceNamespace" : kwargs["FilterSourceNamespace"],
                    "SystemName" : self._client.hostname,
                    "Query" : kwargs["Query"],
                    "QueryLanguage" : kwargs["QueryLanguage"],
                    "Name" : kwargs["Name"] + "-filter"
                }
                (cim_filter, _, errorstr) = self._client._create_instance(
                    kwargs["FilterCreationClassName"], kwargs["CreationNamespace"],
                    cim_filter_props)
                if not cim_filter:
                    lmi_raise_or_dump_exception(LMIIndicationError(errorstr))
                    return LMIReturnValue(rval=False, errorstr=errorstr)
            cim_handler_provided = "Handler" in kwargs
            if cim_handler_provided:
                cim_handler = kwargs["Handler"]._cim_instance
            else:
                cim_handler_props = {
                    "CreationClassName" : kwargs["HandlerCreationClassName"],
                    "SystemCreationClassName" : kwargs["HandlerSystemCreationClassName"],
                    "SystemName" : self._client.hostname,
                    "Destination" : kwargs["Destination"] + "/" + kwargs["Name"],
                    "Name" : kwargs["Name"] + "-handler"
                }
                (cim_handler, _, errorstr) = self._client._create_instance(
                    kwargs["HandlerCreationClassName"], kwargs["CreationNamespace"],
                    cim_handler_props)
                if not cim_handler:
                    if not "Filter" in kwargs:
                        self._client._delete_instance(cim_filter.path)
                    lmi_raise_or_dump_exception(LMIIndicationError(errorstr))
                    return LMIReturnValue(rval=False, errorstr=errorstr)
            cim_subscription_props = {
                "Filter" : cim_filter.path,
                "Handler" : cim_handler.path
            }
            (cim_subscription, _, errorstr) = self._client._create_instance(
                kwargs["SubscriptionCreationClassName"], kwargs["CreationNamespace"],
                cim_subscription_props)
            if not cim_subscription:
                if not "Filter" in kwargs:
                    self._client._delete_instance(cim_filter.path)
                if not "Handler" in kwargs:
                    self._client._delete_instance(cim_handler.path)
                lmi_raise_or_dump_exception(LMIIndicationError(errorstr))
                return LMIReturnValue(rval=False, errorstr=errorstr)
            # XXX: Should we auto-delete all the indications?
            permanent = kwargs.get("Permanent", True)
            self._indications[kwargs["Name"]] = LMISubscription(
                self._client,
                (cim_filter, not cim_filter_provided),
                (cim_handler, not cim_handler_provided),
                cim_subscription,
                permanent)
        except KeyError, e:
            errorstr = "Not all necessary parameters provided, missing: %s" % e
            lmi_raise_or_dump_exception(LMIIndicationError(errorstr))
            return LMIReturnValue(rval=False, errorstr=errorstr)
        return LMIReturnValue(rval=True)

    def unsubscribe_indication(self, name):
        """
        Unsubscribes an indication. Returns LMIReturnValue with bool flag, which
        indicates, whether the indication was successfuly unsubscribed.

        Arguments:
            name -- string containing an indication name
        """
        if not name in self._indications:
            errorstr = "No such indication"
            lmi_raise_or_dump_exception(LMIIndicationError(errorstr))
            return LMIReturnValue(rval=False, errorstr=errorstr)
        indication = self._indications.pop(name)
        indication.delete()
        return LMIReturnValue(rval=True)

    def __unsubscribe_all_indications(self):
        """
        Unsubscribes all the indications, which were not marked as Permanent.
        """
        def delete_subscription(subscription):
            if subscription.permanent:
                return
            subscription.delete()
        map(lambda obj: delete_subscription(obj), self._indications.values())
        self._indications = {}

    def unsubscribe_all_indications(self, atexit_call=False):
        """
        Unsubscribes all the indications. This call ignores "Permanent" flag,
        which may be provided in LMIConnection.subscribe_indication(), and
        deletes all the subscribed indications.
        """
        map(lambda obj: obj.delete(), self._indications.values())
        self._indications = {}

    def print_subscribed_indications(self):
        """
        Prints out all the subscribed indications.
        """
        for i in self._indications.keys():
            sys.stdout.write("%s\n" % i)

    def subscribed_indications(self):
        """
        Returns a list of all the subscribed indications.
        """
        return self._indications.keys()
