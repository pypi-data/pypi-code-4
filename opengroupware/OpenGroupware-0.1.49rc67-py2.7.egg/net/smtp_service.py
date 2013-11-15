#
# Copyright (c) 2011, 2013
#  Adam Tauno Williams <awilliam@whitemice.org>
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

try:
    import gc
    MANUAL_GC_ENABLED = True
except:
    MANUAL_GC_ENABLED = False

import smtpd
import re
import asyncore
import threading
import string

from email.generator import Generator
from email.Parser import Parser

from coils.core import \
    Attachment, \
    Service, \
    Task, \
    Project, \
    Folder, \
    Document, \
    BLOBManager, \
    CoilsException, \
    ServerDefaultsManager, \
    NetworkContext

from smtp_common import \
    get_mimetypes_for_target, \
    transcode_to_filename, \
    parse_message_from_string, \
    parse_message_from_stream, \
    get_raw_message_stream, \
    get_streams_from_message, \
    get_properties_from_message

from smtp_to_folder import smtp_send_to_folder
from smtp_to_collection import smtp_send_to_collection
from smtp_to_route import smtp_send_to_route
from smtp_to_task import smtp_send_to_task


class SMTPServer(smtpd.SMTPServer):

    def __init__(self, manager):
        self.manager = manager
        self.context = NetworkContext()
        sd = ServerDefaultsManager()
        SMTP_ADDR = sd.string_for_default('SMTPListenAddress', '127.0.0.1')
        SMTP_PORT = sd.integer_for_default('SMTPListenPort', 25252)
        smtpd.SMTPServer.__init__(self, (SMTP_ADDR, SMTP_PORT, ), None, )

    def process_message(self, peer, from_, to_, data):
        # TODO: Verify one of the recipients is a candidate
        # TODO: discard messgaes over a given size?
        # TODO: discard messages with more tha n recipients?

        attachment = self.context.run_command(
            'attachment::new',
            mimetype='message/rfc822',
            kind='opengroupware:smtp:message/rfc822',
            data=data, )
        self.context.commit()

        self.manager.enqueue_message((from_, to_, attachment.uuid, ))

        attachment = None
        data = None
        if MANUAL_GC_ENABLED:
            gc.collect()
        self.context.db_close()

    def stop(self):
        self.close()
        self.context.close()


class SMTPService(Service):
    __service__ = 'coils.smtpd'
    __auto_dispatch__ = True
    __is_worker__ = True

    @property
    def queue(self):
        return self._queue

    @property
    def queue_lock(self):
        return self._queue_lock

    @property
    def smtp_prefix(self):
        return self._prefix

    @property
    def ctx(self):
        return self._ctx

    def prepare(self):
        Service.prepare(self)
        try:
            sd = ServerDefaultsManager()
            self._prefix = sd.string_for_default(
                'SMTPAddressPrefix', 'ogo').lower()
            self._queue = []
            self._queue_lock = threading.Lock()
            self._smtpd = SMTPServer(self)
            self._thread = threading.Thread(target=lambda: asyncore.loop())
            self._thread.start()
            self._ctx = NetworkContext(broker=self._broker, )
        except Exception, e:
            self.log.warn('Exception in SMTP component prepare')
            self.log.exception(e)
            raise e

    def shutdown(self):
        self.log.error(
            'Component received shutdown request; '
            'waiting for SMTP service to end.')
        self._smtpd.stop()
        threading.Thread.join(self._thread, 5)
        self.log.error(
            'SMTP service has shutdown, component now shutting down.')
        Service.shutdown(self)

    def enqueue_message(self, message):
        with self.queue_lock:
            self.queue.append(message)

    def work(self):
        '''
        TODO: Component check should be a time-based, not iteration
        based, component
        '''
        with self.queue_lock:
            self.log.debug('SMTP service checking message queue')
            while self.queue:
                data = self.queue.pop()
                self.log.info('SMTP server found message!')
                attachment_uuid = data[2]
                try:
                    recipient = None
                    rfile = self._ctx.run_command('attachment::get-handle',
                                                  uuid=attachment_uuid, )
                    message = parse_message_from_stream(rfile)
                    BLOBManager.Close(rfile)
                    if message.has_key('message-id'):
                        for recipient in data[1]:
                            recipient = recipient.lower().strip()
                            self.log.debug(
                                'checking recipient {0}'.format(recipient))
                            x = recipient.split('@')[0].split('+', 1)
                            if len(x) == 2:
                                if x[0].lower() == self.smtp_prefix:
                                    recipient = x[1]
                                    break
                        else:
                            self.log.warn(
                                'Discarding message, no matching recipients')
                    else:
                        raise CoilsException(
                            'Invalid message, message received '
                            'with no Message-ID')
                except Exception, e:
                    self.log.info('SMTP failed to parse message')
                    self.log.exception(e)
                else:
                    # OK!
                    self.log.info('SMTP sending administrative message')
                    try:
                        self.process_recipient(data[0], recipient, message, )
                    except Exception, e:
                        self.log.exception(e)
                finally:
                    '''
                    Delete the attachment, no matter what. We do not want
                    a huge pile of attachments building up.
                    '''
                    self._ctx.run_command('attachment::delete',
                                          uuid=attachment_uuid, )
                    self._ctx.commit()
                    if MANUAL_GC_ENABLED:
                        gc.collect()
        if self._ctx:
            self._ctx.db_close()

    def process_recipient(self, from_, to_, message):
        targets = to_.split('+')
        if len(targets) == 1:
            try:
                object_id = long(targets[0])
            except:
                self.log.warn(
                    'Unable to convert single recipient target "{0}" '
                    'into an integer value'.format(targets[0], ))
            else:
                self.log.info('Processing SMTP recipient as an objectId')
                kind = self._ctx.type_manager.get_type(object_id)
                self.log.info(
                    'objectId#{0} identitified as a "{1}"'.
                    format(object_id, kind, ))
                if kind == 'Task':
                    smtp_send_to_task(from_=from_,
                                      to_=targets[1],
                                      message=message,
                                      context=self.ctx,
                                      service=self, )
                elif kind == 'Collection':
                    smtp_send_to_collection(object_id=object_id,
                                            message=message,
                                            context=self.ctx,
                                            service=self, )
                elif kind == 'Folder':
                    smtp_send_to_folder(service=self,
                                        context=self.ctx,
                                        object_id=object_id,
                                        message=message,
                                        from_=from_,
                                        to_=to_, )
        elif len(targets) == 2:
            if targets[0] == 'wf':
                smtp_send_to_route(from_=from_,
                                   to_=targets[1],
                                   message=message,
                                   context=self.ctx,
                                   service=self, )
            else:
                self.log.warn(
                    'Nested outer target type of "{0}" not recognized'.
                    format(targets[0], ))
        else:
            self.log.warn('Target of message has too many components')
