#
# Copyright (c) 2009, 2011, 2012, 2013
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
import pprint
import traceback
import textwrap
import base64
import xmlrpclib
import time
from xml.parsers import expat
from coils.net.foundation import PathObject
from coils.core import CoilsException


ZOGI_PROTOCOL_LEVEL = '3A.0;-'


class XMLRPCServer(PathObject):

    name = 'xmlrpc'

    def __init__(self, parent, bundles, **params):
        PathObject.__init__(self, parent, **params)
        self.bundles = bundles

    def do_GET(self):
        raise CoilsException('XML-RPC calls must be POST commands')

    def do_POST(self):

        ''' Process Request'''
        result = None
        start = time.time()
        payload = None
        try:
            payload = self.request.get_request_payload()
            rpc = xmlrpclib.loads(payload, use_datetime=True)
        except xmlrpclib.ResponseError:
            data = base64.encodestring(payload)
            tw = textwrap.TextWrapper(width=76)
            self.context.send_administrative_notice(
                subject='XML-RPC Request Cannot Be Parsed',
                message=('Context: {0} [{1}]\n'
                         'Request:\n'
                         '{2}\n\n'
                         'Traceback:\n'
                         '{3}\n'.
                         format(self.context.account_id,
                                self.context.login,
                                tw.fill(data),
                                traceback.format_exc()
                                )))
            raise
        except expat.ExpatError:
            if payload:
                data = base64.encodestring(payload)
                tw = textwrap.TextWrapper(width=76)
                self.context.send_administrative_notice(
                    subject='XML-RPC Request is not valid XML (Expat Error)',
                    message=('Context: {0} [{1}]\n'
                             'Request:\n'
                             '{2}\n\n'
                             'Traceback:\n'
                             '{3}\n'.
                             format(self.context.account_id,
                                    self.context.login,
                                    tw.fill(data),
                                    traceback.format_exc()
                                    )))
                tw = None
                data = None
            raise
        except:
            raise

        '''Perform Request'''
        try:
            method = rpc[1].split('.')

            if (len(method) < 2):
                raise CoilsException('XML-RPC request without namespace.')
            if (len(method) > 2):
                raise CoilsException('XML-RPC with convoluted namespace.')

            namespace = method[0]
            method_name = method[1]
            parameters = rpc[0]

            for bundle in self.bundles:
                if (bundle.__namespace__ == namespace):
                    handler = bundle(self.context)
                    try:
                        call = getattr(handler, method_name)
                    except Exception, err:
                        raise CoilsException(
                            'Namespace "{0}" has no such method as "{1}"'.
                            format(namespace, method_name))
                        break
                    else:
                        result = apply(call, parameters)
                        break
            else:
                raise CoilsException(
                    'No such API namespace as "{0}"'.format(namespace))
        except Exception, err:
            if self.context.amq_available:
                end = time.time()
                oname = '{0}.{1}'.format(namespace, method_name),

                self.context.send_administrative_notice(
                    subject='XML-RPC Methon Perform Exception',
                    message=('Method: {0}.{1}\n'
                             'Context: {2} [{3}]\n'
                             'Parameters: {4}\n'
                             'Traceback: {5}\n'.
                             format(namespace,
                                    method_name,
                                    self.context.account_id,
                                    self.context.login,
                                    pprint.pformat(parameters),
                                    traceback.format_exc()
                                    )),
                    urgency=5,
                    category='xmlrpc-proxy',
                    attachments=[])

                self.context.send(None,
                                  'coils.administrator/performance_log',
                                  {'lname': 'xmlrpc',
                                   'oname': oname,
                                   'runtime': (end - start),
                                   'error': True, })
            raise err
        else:
            if self.context.amq_available:
                end = time.time()
                oname = '{0}.{1}'.format(namespace, method_name)
                self.context.send(None,
                                  'coils.administrator/performance_log',
                                  {'lname': 'xmlrpc',
                                   'oname': oname,
                                   'runtime': (end - start),
                                   'error': False, })
        finally:
            self.log.debug('XML-RPC processing complete')

        '''Serialize Response'''
        if result is not None:
            try:
                if self.context.user_agent_description['xmlrpc']['allowNone']:
                    result = xmlrpclib.dumps(tuple([result, ]),
                                             allow_none=True,
                                             methodresponse=True)
                else:
                    result = xmlrpclib.dumps(tuple([result, ]),
                                             methodresponse=True)
            except Exception as err:
                self.context.send_administrative_notice(
                    subject='XML-RPC Serialization Error',
                    message=('Method: {0}.{1}\n'
                             'Parameters: {2}\n'
                             'Context: {3} [{4}]\n'
                             'Representation: {5}\n\n'
                             'Traceback: {6}\n'.
                             format(namespace,
                                    method_name,
                                    pprint.pformat(parameters),
                                    self.context.account_id,
                                    self.context.login,
                                    pprint.pformat(result),
                                    traceback.format_exc()
                                    )),
                    urgency=5,
                    category='xmlrpc-proxy',
                    attachments=[])
                raise err

        if self.context.user_agent_description['omphalos']['associativeLists']:
            associative_lists = 't'
        else:
            associative_lists = 'f'

        self.request.simple_response(
            200,
            data=result,
            mimetype='text/xml',
            headers={'X-COILS-ZOGI-PROTOCOL-LEVEL': ZOGI_PROTOCOL_LEVEL,
                     'X-COILS-ASSOCIATIVE-LISTS': associative_lists,
                     'X-COILS-SESSION-ID': self.context.session_id, })
        return
