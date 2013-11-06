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
from LMIExceptions import LMINamespaceNotFound

from LMIUtil import lmi_raise_or_dump_exception
from LMIUtil import lmi_get_use_exceptions
from LMIUtil import lmi_set_use_exceptions

def __lmi_raw_input(prompt, use_echo=True):
    """
    Reads a string from the standard input.

    :param string prompt: input prompt
    :param bool use_echo: whether to echo the input on the command line
    :returns: input string
    :raises: :py:exc:`EOFError`
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

def connect(uri, username="", password="", **kwargs):
    """
    Creates a connection object with provided URI and credentials.

    :param string uri: URI of the CIMOM
    :param string username: account, under which, the CIM calls will be performed
    :param string password: user's password

    :param bool interactive: flag indicating, if the LMIShell client is running in the
        interactive mode; default value is False.
    :param bool use_cache: flag indicating, if the LMIShell client should use cache for
        :py:class:`CIMClass` objects. This saves lot's of communication, if there are
        :func:`EnumerateInstances` and :func:`EnumerateClasses` intrinsic methods often
        issued. Default value is True.
    :param string key_file: path to x509 key file; default value is None
    :param string cert_file: path to x509 cert file; default value is None
    :param bool verify_server_cert: flag indicating, whether a server side certificate
        needs to be verified, if SSL used; default value is True.
    :param string prompt_prefix: username and password prompt prefix in case the user is
        asked for credentials. Default value is empty string.
    :returns: :py:class:`LMIConnection` object or None, if LMIShell does not use
        exceptions
    :raises: :py:exc:`pywbem.AuthError`

    **NOTE:** If interactive is set to True, LMIShell will:

    * prompt for username and password, if missing and connection via
      Unix socket can not be established.
    * use pager for the output of: :py:meth:`.LMIInstance.doc`,
      :py:meth:`.LMIClass.doc`, :py:meth:`.LMIInstance.tomof` and
      :py:meth:`.LMIMethod.tomof`

    **Usage:** :ref:`startup_connection`.
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
    netloc = urlparse.urlparse(uri).netloc
    destination = netloc if netloc else uri
    if os.getuid() == 0 and destination in ("localhost", "127.0.0.1", "::1") and \
            os.path.exists("/var/run/tog-pegasus/cimxml.socket") and \
            not username and not password:
        connection = LMIConnection(uri, None, None, interactive=interactive,
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
        connection = LMIConnection(uri, username, password, interactive=interactive,
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

    :param string uri: URI of the CIMOM
    :param string username: account, under which, the CIM calls will be performed
    :param string password: user's password
    :param bool interactive: flag indicating, if the LMIShell client is running
      in the interactive mode; default value is False.
    :param bool use_cache: flag indicating, if the LMIShell client should use cache for
        CIMClass objects. This saves lot's of communication, if there are
        :func:`EnumerateInstances` and :func:`EnumerateClasses` intrinsic methods often
        issued. Default value is True.
    :param conn_type: type of connection; can be of 2 values:

        * :py:attr:`LMIBaseClient.CONN_TYPE_WBEM` -- WBEM connection,
        * :py:attr:`LMIBaseClient.CONN_TYPE_PEGASUS_UDS` -- applicable only for
          Tog-Pegasus CIMOM, it uses Unix socket for the connection; default value is
          :py:attr:`LMIBaseClient.CONN_TYPE_WBEM`
    :param string key_file: path to x509 key file; default value is None
    :param string cert_file: path to x509 cert file; default value is None
    :param bool verify_server_cert: flag indicating, whether a server side certificate
        needs to be verified, if SSL used; default value is True

    **NOTE:** If interactive is set to True, LMIShell will:

    * prompt for username and password, if missing and connection via
      Unix socket can not be established.
    * use pager for the output of: :py:meth:`.LMIInstance.doc`, :py:meth:`.LMIClass.doc`,
      :py:meth:`.LMIInstance.tomof` and :py:meth:`.LMIMethod.tomof`
    """
    def __init__(self, uri, username="", password="", **kwargs):
        # Set remaining arguments
        interactive = kwargs.pop("interactive", False)
        use_cache = kwargs.pop("use_cache", True)
        conn_type = kwargs.pop("conn_type", LMIBaseClient.CONN_TYPE_WBEM)
        key_file = kwargs.pop("key_file", None)
        cert_file = kwargs.pop("cert_file", None)
        verify_server_cert = kwargs.pop("verify_server_cert", True)
        if kwargs:
            raise TypeError("__init__() got an unexpected keyword arguments: %s" % ", ".join(kwargs.keys()))

        self._client = LMIShellClient(uri, username, password, interactive=interactive,
            use_cache=use_cache, conn_type=conn_type, key_file=key_file, cert_file=cert_file,
            verify_server_cert=verify_server_cert)
        self._indications = {}
        # Register LMIConnection.__unsubscribe_all_indications() to be called at LMIShell's exit.
        atexit.register(lambda: self.__unsubscribe_all_indications())

    def __repr__(self):
        """
        :returns: pretty string for the object.
        """
        return "%s(URI='%s', user='%s'...)" % (self.__class__.__name__,
            self._client.uri, self._client.username)

    @property
    def uri(self):
        """
        :returns: URI of the CIMOM
        :rtype: string
        """
        return self._client.uri

    @property
    def namespaces(self):
        """
        :returns: list of all available namespaces

        **Usage:** :ref:`namespaces_available_namespaces`.
        """
        return ["root"]

    @property
    def root(self):
        """
        :returns: :py:class:`.LMINamespaceRoot` object for *root* namespace
        """
        return LMINamespaceRoot(self)

    def print_namespaces(self):
        """
        Prints out all available namespaces.
        """
        sys.stdout.write("root\n")

    def get_namespace(self, namespace):
        """
        :param string namespace: namespace path (eg. `root/cimv2`)
        :returns: :py:class:`LMINamespace` object
        :raises: :py:exc:`.LMINamespaceNotFound`
        """
        def get_namespace_priv(namespace, namespace_path):
            if not namespace_path:
                return namespace
            ns = namespace_path.pop(0)
            return get_namespace_priv(getattr(namespace, ns), namespace_path)

        namespace_path = namespace.split("/")
        ns = namespace_path.pop(0)
        if not ns in self.namespaces:
            raise LMINamespaceNotFound(ns)
        return get_namespace_priv(getattr(self, ns), namespace_path)

    def clear_cache(self):
        """
        Clears the cache.
        """
        self._client._cache.clear()

    def use_cache(self, active=True):
        """
        Sets a bool flag, which defines, if the LMIShell should use a cache.

        :param bool active: whether the LMIShell's cache should be used
        """
        self._client._cache.active = active

    def verify_credentials(self):
        """
        Verifies credentials by performing a "dummy" :func:`GetClass` call on
        "SomeNonExistingClass". Provided credentials are OK, if the LMIShell
        obtains :py:exc:`pywbem.CIMError` exception with the flag
        ``CIM_ERR_NOT_FOUND`` set. Otherwise, the should receive
        :py:exc:`pywbem.AuthError`.

        :returns: True if provided credentials are OK; False otherwise
        """
        try:
            use_exceptions = lmi_get_use_exceptions()
            lmi_set_use_exceptions(True)
            try:
                self._client._get_class("SomeNonExistingClass")
            except:
                raise
            finally:
                lmi_set_use_exceptions(use_exceptions)
        except pywbem.cim_operations.CIMError, e:
            if e.args[0] == pywbem.cim_constants.CIM_ERR_NOT_FOUND:
                return True
            lmi_raise_or_dump_exception(e)
        except pywbem.cim_http.AuthError, e:
            lmi_raise_or_dump_exception(e)
        except OpenSSL.SSL.Error, e:
            lmi_raise_or_dump_exception(e)
        return False

    def subscribe_indication(self, **kwargs):
        """
        Subscribes to an indication. Indication is formed by 3 objects, where 2 of them
        (filter and handler) can be provided, if the LMIShell should not create those 2 by itself.

        **NOTE:** Currently the call registers :py:mod:`atexit` hook, which auto-deletes
        all subscribed indications by the LMIShell.

        :param dictionary kwargs: parameters for the indication subscription

            * **Filter** (*LMIInstance*) -- if provided, the
              :py:class:`LMIInstance` object will be used instead of creating a new one;
              optional
            * **Handler** (*LMIInstance*) -- if provided, the :py:class:`LMIInstance`
              object will be used instead of creating a new one; optional
            * **Query** (*string*) -- string containing a query for the indications filtering
            * **QueryLanguage** (*string*) -- query language; eg. `WQL`, or `DMTF:CQL`
            * **Name** (*string*) -- indication name
            * **CreationNamespace** (*string*) -- creation namespace
            * **SubscriptionCreationClassName** (*string*) -- subscription object class
              name
            * **Permanent** (*bool*) -- whether to preserve the created subscription on
              LMIShell's quit. Default value is False.
            * **FilterCreationClassName** (*string*) -- creation class name of the filter
              object
            * **FilterSystemCreationClassName** (*string*) -- system creation class name
              of the filter object
            * **FilterSourceNamespace** (*string*) -- local namespace where the
              indications originate
            * **HandlerCreationClassName** (*string*) -- creation class name of the
              handler object
            * **HandlerSystemCreationClassName** (*string*) -- system creation name of the
              handler object
            * **Destination** (*string*) -- destination URI, where the indications should
              be delivered

        :returns: :py:class:`LMIReturnValue` object with ``rval`` set to True, if
            indication was subscribed; False otherwise. If a error occurs, ``errorstr`` is
            set to appropriate error string.
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
                    "SystemName" : self._client.uri,
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
                    "SystemName" : self._client.uri,
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
            permanent = kwargs.get("Permanent", False)
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
        Unsubscribes an indication.

        :param string name: indication name
        :returns: :py:class:`LMIReturnValue` object with ``rval`` set to True, if
            unsubscribed; False otherwise
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

    def unsubscribe_all_indications(self):
        """
        Unsubscribes all the indications. This call ignores *Permanent* flag, which may be
        provided in :py:meth:`.LMIConnection.subscribe_indication`, and deletes all the
        subscribed indications.
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
        :returns: list of all the subscribed indications
        """
        return self._indications.keys()
