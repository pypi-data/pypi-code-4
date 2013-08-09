# Copyright (c) 2012 Ian C. Good
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

"""Relays an |Envelope| locally to an external process. This functionality is
modelled closely off the pipe_ daemon in postfix.

.. _pipe: http://www.postfix.org/pipe.8.html
.. _courier-maildrop: http://www.courier-mta.org/maildrop/
.. _deliver: http://wiki.dovecot.org/LDA

"""

from __future__ import absolute_import

import re

from gevent import Timeout
import gevent_subprocess

from slimta.smtp.reply import Reply
from slimta.relay import Relay, PermanentRelayError, TransientRelayError
from slimta import logging

__all__ = ['PipeRelay']

log = logging.getSubprocessLogger(__name__)


class PipeRelay(Relay):
    """When delivery attempts are made on this object, it will create a new sub-
    process and pipe envelope data to it. Delivery success or failure depends on
    the return code of the sub-process and error messages are pulled from
    standard error output.

    To facilitate passing the |Envelope| metadata, the process's command-line
    arguments can be populated with macros replaced using :py:meth:`str.format`
    with corresponding keywords:

    * ``{sender}``: The sender address.
    * ``{recipient}``: The first address in the recipient last.

    :param args: List of arguments used to spawn the external process, as you
                 would provide them to the :py:class:`~subprocess.Popen`
                 constructor. Each argument has :py:meth:`str.format` called on
                 it, as described above.
    :param timeout: The length of time a delivery is allowed to run before it
                    fails transiently, default unlimited.
    :param error_pattern: A string pattern or :py:class:`~re.RegexObject` for
                          finding the error message in *stdout* or *stderr*. The
                          function :py:func:`re.search` is called, and if there
                          is a match, the first group is used as the error
                          message (e.g. ``match.group(1)``).

                          If no pattern is given, or the given pattern does not
                          match, ``'Delivery failed'`` is used as the error.
    :param popen_kwargs: Extra keyword arguments passed in to the
                         :py:class:`~subprocess.Popen`.

    """

    permanent_error_pattern = re.compile(r'^5\.\d+\.\d+\s')

    def __init__(self, args, timeout=None, error_pattern=None, **popen_kwargs):
        super(PipeRelay, self).__init__()
        self.args = args
        self.timeout = timeout
        self.error_pattern = error_pattern
        self.popen_kwargs = popen_kwargs

    def _process_args(self, envelope):
        macros = {'sender': envelope.sender,
                  'recipient': envelope.recipients[0]}
        return [arg.format(**macros) for arg in self.args]

    def _process_error(self, stdout, stderr):
        if self.error_pattern:
            match = re.search(self.error_pattern, stdout)
            if not match:
                match = re.search(self.error_pattern, stderr)
            if match:
                return match.group(1)

    def _exec_process(self, envelope):
        header_data, message_data = envelope.flatten()
        stdin = ''.join((header_data, message_data))
        with Timeout(self.timeout):
            args = self._process_args(envelope)
            p = gevent_subprocess.Popen(args, stdin=gevent_subprocess.PIPE,
                                              stdout=gevent_subprocess.PIPE,
                                              stderr=gevent_subprocess.PIPE,
                                              **self.popen_kwargs)
            log.popen(p, args)
            stdout, stderr = p.communicate(stdin)
        log.stdio(p, stdin, stdout, stderr)
        log.exit(p)
        if p.returncode == 0:
            return 0, None
        msg = self._process_error(stdout, stderr) or 'Delivery failed'
        return p.returncode, msg

    def _try_pipe(self, envelope):
        try:
            status, err = self._exec_process(envelope)
        except Timeout:
            msg = 'Delivery timed out'
            reply = Reply('450', msg)
            raise TransientRelayError(msg, reply)
        if status != 0:
            self.raise_error(status, err)

    def raise_error(self, status, error_msg):
        """This method may be over-ridden by sub-classes if you need to control
        how the relay error is generated. By default, the error is a
        :class:`~slimta.relay.TransientRelayError` unless the error message
        begins with a ``5.X.X`` enhanced status code. This behavior mimics the
        postfix pipe_ daemon.

        This method is only called if the subprocess returns a non-zero exit
        status.

        :param status: The non-zero exit status of the subprocess.
        :param error_msg: The error messaged as parsed from the *stdout* or
                          *stderr* of the subprocess.
        :raises: :class:`~slimta.relay.TransientRelayError`,
                 :class:`~slimta.relay.PermanentRelayError`

        """
        if self.permanent_error_pattern.match(error_msg):
            reply = Reply('550', error_msg)
            raise PermanentRelayError(error_msg, reply)
        else:
            reply = Reply('450', error_msg)
            raise TransientRelayError(error_msg, reply)

    def attempt(self, envelope, attempts):
        self._try_pipe(envelope)


class MaildropRelay(PipeRelay):
    """Variation of :class:`PipeRelay` that is specifically tailored for calling
    `courier-maildrop`_ for local mail delivery.

    :param path: The path to the ``maildrop`` command on the system. By default,
                 ``$PATH`` is searched.
    :param timeout: The length of time ``maildrop`` is allowed to run before it
                    fails transiently, default unlimited.
    :param extra_args: List of extra arguments, if any, to pass to ``maildrop``.
                       By default, only the sender is passed in with ``-f``.

    """

    EX_TEMPFAIL = 75

    def __init__(self, path=None, timeout=None, extra_args=None):
        args = [path or 'maildrop', '-f', '{sender}']
        if extra_args:
            args += extra_args
        error_pattern = re.compile(r'^maildrop:\s+(.*)$')
        super(MaildropRelay, self).__init__(args, timeout, error_pattern)

    def raise_error(self, status, error_msg):
        if status == self.EX_TEMPFAIL:
            reply = Reply('450', error_msg)
            raise TransientRelayError(error_msg, reply)
        else:
            reply = Reply('550', error_msg)
            raise PermanentRelayError(error_msg, reply)


class DovecotRelay(PipeRelay):
    """Variation of :class:`PipeRelay` that is specifically tailored for calling
    dovecot's deliver_ command for local mail delivery.

    :param path: The path to the ``deliver`` command on the system. By default,
                 ``$PATH`` is searched.
    :param timeout: The length of time ``deliver`` is allowed to run before it
                    fails transiently, default unlimited.
    :param extra_args: List of extra arguments, if any, to pass to ``deliver``.
                       By default, only the sender and recipient are passed in
                       with ``-f`` and ``-d``, respectively.

    """

    EX_TEMPFAIL = 75

    def __init__(self, path=None, timeout=None, extra_args=None):
        args = [path or 'deliver',
                '-f', '{sender}',
                '-d', '{recipient}']
        if extra_args:
            args += extra_args
        super(DovecotRelay, self).__init__(args, timeout)

    def raise_error(self, status, error_msg):
        if status == self.EX_TEMPFAIL:
            reply = Reply('450', error_msg)
            raise TransientRelayError(error_msg, reply)
        else:
            reply = Reply('550', error_msg)
            raise PermanentRelayError(error_msg, reply)


# vim:et:fdm=marker:sts=4:sw=4:ts=4
