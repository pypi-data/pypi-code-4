# Copyright (c) 2010, 2012, 2013
#   Adam Tauno Williams <awilliam@whitemice.org>
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
import xmlrpclib
import transport
import traceback
import pprint
import time
import base64
import textwrap
from xml.parsers import expat
from os import getenv
from base64 import b64decode
from coils.core import Service, ServerDefaultsManager, AuthenticationException
from coils.net import XMLRPCServer, Protocol, PathObject
from coils.foundation import fix_microsoft_text
from coils.core.omphalos import \
    associate_omphalos_representation, disassociate_omphalos_representation

PROXY_URI_PATTERN = 'http://{0}/zidestore/so/{1}/'


class Proxy(Protocol, PathObject):
    __pattern__ = '^proxy$'
    __namespace__ = None
    __xmlrpc__ = False
    __ResultTranscode__ = None

    def __init__(self, parent, **params):
        self.name = 'proxy'
        PathObject.__init__(self, parent, **params)
        if (Proxy.__ResultTranscode__ is None):
            sd = ServerDefaultsManager()
            Service.__PayloadTranscode__ = \
                sd.bool_for_default('CoilsXMLRPCProxyTranscode')
            self.log.debug('XML-RPC Proxy Transcoded Results Enabled')
            coils_proxy_target = getenv('COILS_RPC2_PROXY_TARGET')
            if coils_proxy_target:
                Service.__ProxyHost__ = coils_proxy_target
            else:
                Service.__ProxyHost__ = \
                    sd.string_for_default(
                        'CoilsXMLRPCProxyTarget',
                        value='127.0.0.1')
            self.log.debug(
                'XML-RPC Proxy Target is "{0}"'.format(
                    Service.__ProxyHost__
                )
            )

    def local_methods(self):
        return ['zogi.getLoginAccount', 'zogi.getTombstone', ]

    def do_POST(self):
        request = self.request
        # Set authorization information
        authorization = request.headers.get('authorization')
        if authorization is None:
            raise AuthenticationException('Authentication Required')
        (kind, data) = authorization.split(' ')
        if (kind == 'Basic'):
            (username, _, password) = b64decode(data).partition(':')
        else:
            raise 'Proxy can only process Basic authentication'
            return

        '''Decode response'''
        payload = request.get_request_payload()
        if (Service.__PayloadTranscode__):
            self.log.debug('XML-RPC Proxy Transcoding Results')
            payload = fix_microsoft_text(payload)
        try:
            rpc = xmlrpclib.loads(payload, use_datetime=True)
        except xmlrpclib.ResponseError:
            data = base64.encodestring(payload)
            tw = textwrap.TextWrapper(width=76)
            self.context.send_administrative_notice(
                subject='XML-RPC Request Cannot Be Parsed',
                message='Context: {0} [{1}]\n'
                        'Request:\n'
                        '{2}\n\n'
                        'Traceback:\n'
                        '{3}\n'.
                        format(
                            self.context.account_id,
                            self.context.login,
                            tw.fill(data),
                            traceback.format_exc(),
                        )
            )
            raise
        except expat.ExpatError:
            if payload:
                data = base64.encodestring(payload)
                tw = textwrap.TextWrapper(width=76)
                self.context.send_administrative_notice(
                    subject='XML-RPC Request is not valid XML (Expat Error)',
                    message='Context: {0} [{1}]\n'
                            'Request:\n'
                            '{2}\n\n'
                            'Traceback:\n'
                            '{3}\n'.
                            format(
                                self.context.account_id,
                                self.context.login,
                                tw.fill(data),
                                traceback.format_exc(),
                            )
                )
                tw = None
                data = None
            raise

        # Issue request
        x = transport.Transport()
        x.credentials = (username, password)

        omphalos_ua = self.context.user_agent_description['omphalos']

        '''
        HACK: If the method is specified to be handled locally then we
        delegate the work to a Coils XMLRPCServer object and we leave the
        Legacy backend out of the loop.
        '''
        parameters = rpc[0]
        method_name = rpc[1]
        if method_name in self.local_methods():
            self.log.info(
                'Proxy selecting local method for call to {0}'.
                format(
                    method_name,
                )
            )
            server = XMLRPCServer(self,
                                  self.parent._protocol_dict['^RPC2$'],
                                  context=self.context,
                                  request=self.request)
            server.do_POST()
            return
        else:
            # Passing this call to Legacy backend
            self.log.info(
                'Proxy calling remote method for call to {0}'.
                format(
                    method_name,
                )
            )
            '''
            HACK: Here we pretend that OpenGroupware Legacy understands
            Coils User Agent descriptions. If a user-agent is known to use
            associativeLists then we flatten then before sending the data to
            the backend server.
            '''
            if omphalos_ua['associativeLists']:
                if method_name.lower() == 'zogi.putobject':
                    parameters = \
                        disassociate_omphalos_representation(parameters)

            server = xmlrpclib.Server(
                PROXY_URI_PATTERN.format(
                    Service.__ProxyHost__,
                    username,
                ),
                transport=x)

        method = getattr(server, method_name)

        errors = 0
        start = time.time()

        for attempt in range(1, 3):
            try:
                result = None
                result = method(*parameters)
                break

            except xmlrpclib.ProtocolError, err:
                self.log.warn(
                    '****Protocol Error, trying again in 0.5 seconds****')
                self.log.exception(err)
                time.sleep(0.5)
                errors += 1

            except xmlrpclib.Fault as err:
                # Return the fault to the client; this is BROKEN!
                self.log.warn('Fault code: {0}'.format(err.faultCode, ))
                self.log.warn('Fault string: {0}'.format(err.faultString, ))
                errors += 1

                self.context.send_administrative_notice(
                    subject='XML-RPC Fault Response',
                    message='Method: {0}\n'
                            'Context: {1} [{2}]\n'
                            'Args:{3}\n'
                            'Fault: {4}\n'
                            'Message: {5}\n'.format(
                                method_name,
                                self.context.account_id,
                                self.context.login,
                                pprint.pformat(parameters),
                                err.faultCode,
                                err.faultString,
                            ),
                    urgency=5,
                    category='xmlrpc-proxy',
                    attachments=[])

                result = xmlrpclib.dumps(err, methodresponse=True)

                self.request.simple_response(200,
                                             data=result,
                                             mimetype='text/plain', )

                return

            except Exception as err:

                self.log.warn(
                    '****General Error, trying again in 0.5 seconds****')
                self.log.exception(err)
                time.sleep(0.5)
                errors += 1

                self.context.send_administrative_notice(
                    subject='XML-RPC Generic Failure',
                    message='Context: OGo#{0} [{1}]\n'
                            'Session: {2}\n'
                            'Attempt: {3}\n'
                            'Method: {4}\n'
                            'Args: {5}\n'
                            'Traceback: {6}\n'.
                            format(
                                self.context.account_id,
                                self.context.login,
                                self.context.session_id,
                                attempt,
                                method_name,
                                pprint.pformat(parameters),
                                traceback.format_exc(),
                            ),
                    urgency=5,
                    category='xmlrpc-proxy',
                    attachments=[])

            finally:
                end = time.time()
                if self.context.amq_available:
                    self.context.send(
                        None,
                        'coils.administrator/performance_log',
                        {'lname': 'proxycalls',
                         'oname': method_name,
                         'runtime': (end - start),
                         'error': bool(errors), })
                    self.context.send(
                        None,
                        'coils.administrator/performance_log',
                        {'lname': 'proxyusers',
                         'oname': self.context.login,
                         'runtime': (end - start),
                         'error': bool(errors), })

        '''
        HACK: Again we pretend that Legacy can understand Coils User
              Agent descriptions.
        '''
        if result is not None:

            if omphalos_ua['associativeLists']:
                result = associate_omphalos_representation(result)

            try:
                result = xmlrpclib.dumps(tuple([result]), methodresponse=True)
            except:
                self.context.send_administrative_notice(
                    subject='XML-RPC Proxy Serialization Error',
                    message='Method: {0}\n'
                            'Parameters: {1}\n'
                            'Context: {2} [{3}]\n'
                            'Representation: {4}\n\n'
                            'Traceback: {5}\n'.
                            format(
                                method_name,
                                pprint.pformat(parameters),
                                self.context.account_id,
                                self.context.login,
                                pprint.pformat(result),
                                traceback.format_exc()
                            ),
                    urgency=5,
                    category='xmlrpc-proxy',
                    attachments=[])
                raise

            # HACK: Try to transcode out any unpleasent characters if such
            # feature is enabled.
            if (Service.__PayloadTranscode__):
                self.log.debug('XML-RPC Proxy Transcoding Results')
                result = fix_microsoft_text(result)
            self.request.simple_response(200, data=result, mimetype='text/xml')
            return

        self.log.error('NULL result for XML-RPC request')

        self.context.send_administrative_notice(
            subject='NULL Response To XML-RPC call',
            message='Context: OGo#{0} [{1}]\n'
                    'Method: {2}\n'
                    'Args:{3}\n'.
                    format(
                        self.context.account_id,
                        self.context.login,
                        method_name,
                        pprint.pformat(parameters),
                    ),
            urgency=5,
            category='xmlrpc-proxy',
            attachments=[])

        self.request.simple_response(
            500,
            data='No response from proxy backend',
            mimetype='text/plain', )
