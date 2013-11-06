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

import sys
import pywbem
import signal
import socket
import urlparse
import threading
import collections

from LMIBaseObject import LMIWrapperBaseObject
from LMIBaseClient import LMIBaseClient
from LMIObjectFactory import LMIObjectFactory
from LMIFormatter import LMIMofFormatter
from LMIReturnValue import LMIReturnValue
from LMIConstantValues import LMIConstantValuesParamProp
from LMIConstantValues import LMIConstantValuesMethodReturnType
from LMIIndicationListener import LMIIndicationListener

from LMIJob import lmi_is_job_finished
from LMIJob import lmi_is_job_completed
from LMIJob import lmi_is_job_terminated
from LMIJob import lmi_is_job_killed
from LMIJob import lmi_is_job_exception
from LMIJob import JOB_NOT_FINISHED
from LMIJob import JOB_FINISH_DELAYED
from LMIJob import JOB_FINISH_EARLY

from LMIUtil import LMIPassByRef
from LMIUtil import lmi_raise_or_dump_exception
from LMIUtil import lmi_cast_to_cim
from LMIUtil import lmi_transform_to_lmi

from LMIExceptions import LMIIndicationListenerError
from LMIExceptions import LMIMethodCallError
from LMIExceptions import LMISynchroMethodCallError
from LMIExceptions import LMISynchroMethodCallFilterError
from LMIExceptions import LMIUnknownParameterError
from LMIExceptions import LMIHandlerNamePatternError

class LMISignalHelper(object):
    """
    Helper class, which takes care of signal (de)registration and handling.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LMISignalHelper, cls).__new__(cls)
            LMISignalHelper.reset(cls._instance)
        return cls._instance

    def reset(self):
        """
        Resets the single instance into default state.
        """
        self._handler_sigint  = None
        self._handler_sigterm = None
        self._signal_handled  = False
        self._instance._callbacks = collections.OrderedDict()

    def signal_attach(self):
        """
        Registers *SIGINT* and *SIGTERM* signals to local handler in which, the flags for
        each signal are modified, if such signal is caught.
        """
        self._signal_handled  = False
        self._handler_sigint  = signal.signal(signal.SIGINT,  LMISignalHelper.__signal_handler)
        self._handler_sigterm = signal.signal(signal.SIGTERM, LMISignalHelper.__signal_handler)

    def signal_detach(self):
        """
        Unregisters *SIGINT* and *SIGTERM* handler and removes all the attached callbacks.
        """
        signal.signal(signal.SIGINT,  self._handler_sigint)
        signal.signal(signal.SIGTERM, self._handler_sigterm)

    def signal_handled(self):
        """
        :returns: True, if any of *SIGINT* or *SIGTERM* has been caught; False otherwise
        """
        return self._signal_handled

    def callback_attach(self, cb_name, cb):
        """
        Registers a callback, which will be called when a *SIGINT* or *SIGTERM* is caught.

        :param string cb_name: callback name
        :param cb: callable object, which takes zero arguments
        """
        self._callbacks[cb_name] = cb

    def callback_detach(self, cb_name):
        """
        Removes a callback from the callback dictionary.

        :param string cb_name: callback name
        """
        self._callbacks.pop(cb_name)

    @staticmethod
    def __signal_handler(signo, frame):
        """
        Signal handler, which is called, when *SIGINT* and *SIGTERM* are sent to
        the LMIShell.

        :param int signo: signal number
        :param frame: -- stack frame

        **NOTE:** see help(signal)
        """
        if signo in (signal.SIGINT, signal.SIGTERM):
            LMISignalHelper._instance._signal_handled = True
        for cb in LMISignalHelper._instance._callbacks.values():
            cb()

class LMIMethod(LMIWrapperBaseObject):
    """
    LMI wrapper class representing :py:class:`CIMMethod`.

    :param LMIConnection conn: connection object
    :param LMIInstance lmi_instance: :py:class:`LMIInstance` object, on which the method
        call will be issued
    :param string method: method name
    :param bool sync_method: flag indicating, if we are trying to perform a
        synchronous method call
    """
    # 15 seconds sleep timeout for main waiting thread
    _COND_WAIT_TIME = 15
    # Wake count of main thread, when the GetInstance is performed to check,
    # if the job object is present. Prevents infinite waiting for indication
    # delivery. Maximum waiting time, before the GetInstance for job object
    # will be called is: _COND_WAIT_TIME * _COND_WAIT_WAKE_CNT
    _COND_WAIT_WAKE_CNT = 8
    # Default tcp port, where the indications will be delivered.
    # TODO: create a configuration option for the port
    _INDICATION_DESTINATION_PORT = 10240
    # Job classes, which can be used for synchro method calls
    # TODO: create a configuration option for the static filters' classnames
    _INDICATION_JOB_CLASSNAMES = (
        "LMI_StorageJob",
        "LMI_SoftwareInstallationJob",
        "LMI_SoftwareVerificationJob",
        "LMI_NetworkJob"
    )
    # Default namespace where the indication subscriptions, used for synchronous
    # method calls, will be registered.
    _INDICATION_NAMESPACE = "root/interop"
    # When performing a synchronous method call and using the polling method to
    # get a job object status, the sleep time between 2 polls doubles if it is
    # less than _POLLING_ADAPT_MAX_WAITING_TIME.
    _POLLING_ADAPT_MAX_WAITING_TIME = 128

    def __init__(self, conn, lmi_instance, method, sync_method):
        super(LMIMethod, self).__init__(conn)
        self._lmi_instance = lmi_instance
        self._method = lmi_instance._lmi_class._cim_class.methods[method]
        self._sync_method = sync_method
        # Store the constant values as a list. This can consume some time, if computed on demand.
        self._valuemap_parameters_list = [k for (k, v) in self._method.parameters.iteritems() \
            if "ValueMap" in v.qualifiers]
        # For simplicity, we add return value constants to the same list
        if "ValueMap" in self._method.qualifiers:
            self._valuemap_parameters_list.append(self._method.name)

    def __return_synchro_method_call(self, job_inst, job_refresh=True):
        """
        Returns a :py:class:`LMIReturnValue` object with Job output parameters set.

        :param LMIInstance job_inst: job returned from a synchronous method call
        :param bool job_refresh: flag, which indicates, if the ``job_inst``
            needs to be refreshed
        :returns: :py:class:`LMIReturnValue` object with ``rval`` set to Job output parameters
        """
        # Adjust return value from the job object
        if job_refresh:
            job_inst.refresh()
        rval = None
        rparams = pywbem.NocaseDict()
        if not job_inst.JobOutParameters is None:
            rparams = pywbem.NocaseDict({
                k: x.value
                for k, x in job_inst.JobOutParameters.properties.iteritems()})
            rval = rparams["__ReturnValue"]
            del rparams["__ReturnValue"]    # NocaseDict has no pop()
        errorstr = ""

        # Is job in exception state? If so, adjust corresponding error string
        # from job.GetError() instance
        if lmi_is_job_exception(job_inst):
            (refreshed, _, errorstr) = job_inst.refresh()
            if not refreshed:
                raise LMISynchroMethodCallError(errorstr)
            (exc_rval, exc_rparams, exc_errorstr) = job_inst.GetError()
            error_inst = exc_rparams.get("error", None)
            if not error_inst:
                raise LMISynchroMethodCallError("Could not get Job error message")
            errorstr = error_inst.Message
        return LMIReturnValue(rval=rval, rparams=rparams, errorstr=errorstr)

    def __handle_synchro_method_call_indication(self, job_inst):
        """
        Handles a synchronous call for asynchronous methods returning a job object. This
        method uses static filters installed by each OpenLMI provider, which is capable of
        using jobs.

        :param LMIInstance job_inst: job object returned from a synchronous
            method call
        :returns: :py:class:`LMIReturnValue` object with ``rval`` set to 0 and ``rparams``
            set to job's output parameters
        :raises: :py:exc:`.LMIIndicationListenerError`,
            :py:exc:`.LMISynchroMethodCallError`,
            :py:exc:`.LMISynchroMethodCallFilterError`

        **NOTE:** Static filters' names need to be in format
            "``LMI:<job_class_name>:Changed``"

        """
        def handle_job(ind, cond, job_finished, job_exception):
            """
            :py:class:`LMIListener` handler for synchronous method call, which uses
            indication means of waiting for the job. This function is called, when a job
            changes its state.

            :param threading.Condition cond: condition object used for thread synchronization
            :param LMIPassByRef job_finished: used for synchronization, whether the
                job has finished
            :param LMIPassByRef job_exception: contains an exception object, if any
                exception was raised
            """
            cond.acquire()
            try:
                exp_obj = ind.exported_objects()[0]
                src_inst = exp_obj["SourceInstance"]
                if lmi_is_job_finished(src_inst):
                    # Job has just finished
                    job_finished.value = JOB_FINISH_DELAYED
            except Exception, e:
                # Notify main thread, we are not able to work with such objects
                job_finished.value = JOB_FINISH_DELAYED
                job_exception.value = e
            finally:
                # XXX: Let's be defensive, always notify+release main thread
                cond.notify()
                cond.release()

        # Start indication listener
        cond = threading.Condition()
        job_finished = LMIPassByRef(JOB_NOT_FINISHED)
        job_exception = LMIPassByRef(None)
        # There needs to be a pattern of at least 8 "X" in a row at the end of the indication_name
        indication_name = "synchro-method-call-XXXXXXXX"
        listener = LMIIndicationListener("0.0.0.0", LMIMethod._INDICATION_DESTINATION_PORT)
        indication_name = listener.add_handler(indication_name, handle_job, cond, job_finished,
            job_exception)
        if not listener.start():
            raise LMIIndicationListenerError("Can not start indication listener")

        # Search for necessary static filter
        filter_name = "LMI:%s:Changed" % job_inst.classname
        (cim_filters, _, err) = self._conn._client._get_instances("CIM_IndicationFilter",
            LMIMethod._INDICATION_NAMESPACE, {"Name" : filter_name})
        if not cim_filters:
            listener.stop()
            errorstr = "Can not find proper CIM_IndicationFilter for this method call"
            raise LMISynchroMethodCallFilterError(errorstr)
        cim_filter = cim_filters[0]

        # Create handler object
        netloc = urlparse.urlparse(self._conn.uri).netloc
        if not netloc:
            listener.stop()
            errorstr = "Can not determine netloc from client's uri"
            raise LMISynchroMethodCallError(errorstr)
        netloc = netloc.split(":")[0]
        # NOTE: This will work only on a local area network. Complicated networks may require
        # additional configuration to make this work. See LMIMethod() and PreferPolling.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect((netloc, LMIMethod._INDICATION_DESTINATION_PORT))
        except socket.gaierror, e:
            listener.stop()
            errorstr = "Can not determine IP address of this machine"
            raise LMISynchroMethodCallError(errorstr)
        destination = s.getsockname()[0]
        s.close()
        # NOTE: For now, we are using insecure HTTP as a transport protocol.
        # TODO: Switch to HTTPS
        cim_handler_props = {
            "Name" : indication_name,
            "Destination" : "http://%s:%d/%s" % (destination,
                LMIMethod._INDICATION_DESTINATION_PORT, indication_name),
        }
        (cim_handler, _, err) = self._conn._client._create_instance("CIM_IndicationHandlerCIMXML",
            LMIMethod._INDICATION_NAMESPACE, cim_handler_props)
        if not cim_handler:
            listener.stop()
            errorstr = "Can not create CIM_IndicationHandlerCIMXML object"
            raise LMISynchroMethodCallError(errorstr)

        # Create indication subscription object
        cim_subscription_props = {
            "Filter" : cim_filter.path,
            "Handler" : cim_handler.path
        }
        (cim_subscription, _, err) = self._conn._client._create_instance("CIM_IndicationSubscription",
            LMIMethod._INDICATION_NAMESPACE, cim_subscription_props)
        if not cim_subscription:
            self._conn._client._delete_instance(cim_handler)
            listener.stop()
            errorstr = "Can not create CIM_IndicationSubscription object"
            raise LMISynchroMethodCallError(errorstr)

        # Check, if the job is not already in finished state,
        # while we were subscribing for the indications
        job_inst.refresh()
        if lmi_is_job_finished(job_inst):
            job_finished.value = JOB_FINISH_EARLY

        # Register signal callback for SIGINT, SIGTERM with callback,
        # which awakes waiting thread for immediate return.
        LMISignalHelper().callback_attach("indication", lambda: LMIMethod.__wake(cond))
        LMISignalHelper().signal_attach()

        # Wait for the job to finish
        wake_cnt = 0
        cond.acquire()
        while not LMISignalHelper().signal_handled() and \
                not job_finished.value and \
                not lmi_is_job_finished(job_inst):
            cond.wait(LMIMethod._COND_WAIT_TIME)
            wake_cnt += 1
            # XXX: threading.Condition.wait() does not inform about timeout or being awaken by
            # notify call. There is a counting to 4 sleep cycles before we actually check for
            # job status manually. This number can be increased, so we rely more on indications,
            # rather then on manual polling.
            if wake_cnt >= LMIMethod._COND_WAIT_WAKE_CNT and \
                    not job_finished.value:
                wake_cnt = 0
                try:
                    (refreshed, _, errorstr) = job_inst.refresh()
                except pywbem.cim_operations.CIMError, e:
                    job_exception.value = e
                    break
                if not refreshed:
                    job_exception.value = LMISynchroMethodCallError(errorstr)
                    break

        # Unregister signal handler
        LMISignalHelper().signal_detach()
        LMISignalHelper().callback_detach("indication")

        cond.release()

        # Cleanup
        listener.stop()
        self._conn._client._delete_instance(cim_subscription.path)
        self._conn._client._delete_instance(cim_handler.path)
        if job_exception.value:
            raise job_exception.value
        if LMISignalHelper().signal_handled() and not job_finished.value:
            # We got SIGINT or SIGTERM, when waiting for the job, cancelling the job
            sys.stderr.write("Cancelling a job '%s'\n" % job_inst.Name)
            job_inst.RequestStateChange(
                RequestedState=job_inst.RequestStateChange.RequestedStateValues.Terminate
            )
            return LMIReturnValue(rval=None)

        # Return the job return values, refresh the job_inst object, if we got notified
        # about the job finish state by indication.
        return self.__return_synchro_method_call(job_inst, job_finished.value == JOB_FINISH_DELAYED)

    def __handle_synchro_method_call_polling(self, job_inst):
        """
        Handles a synchronous call for asynchronous methods returning a job object.
        This call uses polling method to wait for the job to finish.

        :param LMIInstance job_inst: job object
        :returns: :py:class:`LMIReturnValue` object with ``rval`` set to 0 and ``rparams``
            set to job's output parameters.
        :raises: :py:exc:`.LMISynchroMethodCallError`
        """

        # Register signal callback for SIGINT, SIGTERM with callback,
        # which awakes waiting thread for immediate return.
        LMISignalHelper().callback_attach("polling", lambda: LMIMethod.__wake(cond))
        LMISignalHelper().signal_attach()

        cond = threading.Condition()
        cond.acquire()

        job_exception = None

        try:
            sleep_time = 1
            while not LMISignalHelper().signal_handled() and \
                    not lmi_is_job_finished(job_inst):
                # Sleep, a bit longer in every iteration
                cond.wait(sleep_time)
                if sleep_time < LMIMethod._POLLING_ADAPT_MAX_WAITING_TIME:
                    sleep_time *= 2
                (refreshed, _, errorstr) = job_inst.refresh()
                if not refreshed:
                    job_exception = LMISynchroMethodCallError(errorstr)
                    break
        except pywbem.cim_operations.CIMError, e:
            job_exception = LMISynchroMethodCallError(e.message)
        finally:
            cond.release()

        # Unregister signal handler and callback
        LMISignalHelper().signal_detach()
        LMISignalHelper().callback_detach("polling")

        if LMISignalHelper().signal_handled() and not lmi_is_job_finished(job_inst):
            # We got SIGINT or SIGTERM, when waiting for the job, cancelling the job
            sys.stderr.write("Cancelling a job '%s'\n" % job_inst.Name)
            job_inst.RequestStateChange(
                RequestedState=job_inst.RequestStateChange.RequestedStateValues.Terminate
            )
            return LMIReturnValue(rval=None)

        if not job_exception is None:
            raise job_exception

        # Return the job return values. No need to refresh the job instance, we already
        # have a "fresh" one.
        return self.__return_synchro_method_call(job_inst, False)

    def __call__(self, method_args=None, **kwargs):
        """
        Perform a method call.

        Method arguments are preferably passed by dictionary (parameter : value). Using
        former means of passing arguments, by keyword arguments, to a method call works
        too.

        If performing a synchronous method call, passing PreferPolling can be used
        to select which method should be used -- either subscribing to an indication
        or polling method.

        :param dictionary method_args: method arguments
        :param dictionary kwargs: keyword method arguments (``method_args`` preffered)

            * **RefreshInstance** (*bool*) flag, which tells the LMIShell, whether
              the instance should be refreshed after a method call. Default
              value is False.

        :returns: :py:class:`LMIReturnValue` object with ``rval`` set to method's return
            value; ``rparams`` set to method's return parameters; ``errorstr`` set
            method's error string in case of failure
        :raises: :py:exc:`.LMIUnknownParameterError`,
            :py:exc:`.LMIMethodCallError`
            :py:exc:`.LMISynchroMethodCallError`

        **Usage:** :ref:`instances_methods`.
        """
        synchro_method_polling = kwargs.pop("PreferPolling", False)
        refresh_requested = kwargs.pop("RefreshInstance", False)
        if method_args is None:
            method_args = {}
        method_args.update(kwargs)
        for (param, value) in method_args.iteritems():
            if param in self._method.parameters:
                if isinstance(value, LMIObjectFactory().LMIInstanceName):
                    value = value.wrapped_object
                t = self._method.parameters[param].type
                method_args[param] = lmi_cast_to_cim(t, value)
            else:
                # NOTE: maybe we could check for pywbem type and not to exit prematurely
                errorstr = "Unknown parameter '%s' supplied for method '%s'" % (param, self._method.name)
                lmi_raise_or_dump_exception(LMIUnknownParameterError(errorstr))
                return LMIReturnValue(rval=-1, errorstr=errorstr)
        (rval, call_rparams, call_errorstr) = self._conn._client._call_method_raw(self._lmi_instance,
            self._method.name, **method_args)
        rval = lmi_transform_to_lmi(self._conn, rval)
        if call_rparams:
            call_rparams = lmi_transform_to_lmi(self._conn, call_rparams)
            if not call_rparams:
                # NOTE: this is wrong! What should we do?
                errorstr = "Could not perform CIM -> LMI object transformation"
                lmi_raise_or_dump_exception(LMIMethodCallError(errorstr))
                return LMIReturnValue(rval=rval, errorstr=errorstr)
            # Check if we can perform synchronous method call
            job = call_rparams.get("job", None)
            can_perform_sync_call = job.classname in LMIMethod._INDICATION_JOB_CLASSNAMES if job else False
            if self._sync_method and job and can_perform_sync_call:
                # Synchronous method calls
                job_inst = call_rparams['job'].to_instance()
                # At first, try to wait for the call to finish by subscribing to an indication
                handled_by_indication = False
                if not synchro_method_polling:
                    try:
                        (rval, call_rparams, call_errorstr) = self.__handle_synchro_method_call_indication(job_inst)
                        handled_by_indication = True
                    except pywbem.CIMError, e:
                        lmi_raise_or_dump_exception(e)
                        return LMIReturnValue(rval=-1, errorstr=e.args[1])
                    except LMISynchroMethodCallError, e:
                        lmi_raise_or_dump_exception(e)
                        return LMIReturnValue(rval=-1, errorstr=e.message)
                    # Fall through, try to handle the synchro call by polling
                    except LMIHandlerNamePatternError, e:
                        handled_by_indication = False
                    except LMISynchroMethodCallFilterError, e:
                        handled_by_indication = False
                    except LMIIndicationListenerError, e:
                        handled_by_indication = False
                if not handled_by_indication:
                    # Executed, when LMIListener can not be started
                    try:
                        (rval, call_rparams, call_errorstr) = self.__handle_synchro_method_call_polling(job_inst)
                    except LMISynchroMethodCallError, e:
                        lmi_raise_or_dump_exception(e)
                        return LMIReturnValue(rval=-1, errorstr=e.message)
                call_rparams = lmi_transform_to_lmi(self._conn, call_rparams)
        if refresh_requested and not self._lmi_instance.refresh():
            # NOTE: this is wrong! What should we do?
            errorstr = "Could not update an LMI object after a method call"
            lmi_raise_or_dump_exception(LMIMethodCallError(errorstr))
            return LMIReturnValue(rval=rval, errorstr=errorstr)
        return LMIReturnValue(rval=rval, rparams=call_rparams, errorstr=call_errorstr)

    def __getattr__(self, name):
        """
        Returns either a class member, or a constant value.

        :param string name: class member, or the constant value name
        """
        if name in self.__dict__:
            return self.__dict__[name]
        if name.endswith("Values"):
            parameter_name = name[:-6]
            if parameter_name in self._method.parameters:
                return LMIConstantValuesParamProp(self._method.parameters[parameter_name])
            elif parameter_name == self._method.name:
                return LMIConstantValuesMethodReturnType(self._method)
        raise AttributeError(name)

    @staticmethod
    def __wake(cond):
        """
        Helper function used for manual :py:attr:`threading.Condition` wakeup.

        :param threading.Condition cond: condition object
        """
        cond.acquire()
        cond.notify()
        cond.release()

    @property
    def return_type(self):
        """
        :returns: string of the method call's return type
        """
        return self._method.return_type

    def tomof(self):
        """
        Prints out a message with MOF representation of :py:class:`CIMMethod`. If the
        LMIShell is run in a interactive mode, the output will be redirected to a pager
        set by environment variable :envvar:`PAGER`. If there is not :envvar:`PAGER` set,
        less or more will be used as a fall-back.
        """
        LMIMofFormatter(self._method.tomof()).fancy_format(self._conn._client.interactive)

    def valuemap_parameters(self):
        """
        :returns: list of strings of the constant names
        """
        return self._valuemap_parameters_list

    def print_valuemap_parameters(self):
        """
        Prints out the list of strings of constant names.
        """
        for i in self._valuemap_parameters_list:
            sys.stdout.write("%s\n" % i)

    def parameters(self):
        """
        :returns: list of strings of :py:class:`CIMMethod`'s parameters
        """
        return self._method.parameters

    def print_parameters(self):
        """
        Prints out :py:class:`CIMMethod`'s parameters.
        """
        for (param, value) in self._method.parameters.iteritems():
            sys.stdout.write("%s %s%s\n" % (value.type, param, "[]" if value.is_array else ""))

    @property
    def wrapped_object(self):
        """
        :returns: wrapped :py:class:`CIMmethod` object
        """
        return self._method
