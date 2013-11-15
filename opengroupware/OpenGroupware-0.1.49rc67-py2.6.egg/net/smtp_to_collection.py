#
# Copyright (c) 2013
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
import re
from email.generator import Generator
from coils.core import BLOBManager

from smtp_common import \
    get_mimetypes_for_target, \
    transcode_to_filename, \
    parse_message_from_string, \
    parse_message_from_stream, \
    get_raw_message_stream, \
    get_streams_from_message, \
    get_properties_from_message


def smtp_send_to_collection(service, context, object_id, message):
    collection = context.run_command('collection::get', id=object_id)

    def authenticate_collection(object_id, message, context, service):
        collection = context.run_command('collection::get', id=object_id)
        if (collection is None):
            service.log.warn(
                'CollectionId#{0} not available to the NetworkContext'.
                format(object_id, ))
        elif (collection.owner_id == 10000):
            service.log.warn(
                'CollectionId#{0} is owned by the administrator; forbidden.'.
                format(object_id, ))
        elif (collection.auth_token is None):
            service.log.warn(
                'CollectionId#{0} has no authentication token'.
                format(object_id, ))
        elif (collection.auth_token == 'unpublished'):
            service.log.warn(
                'CollectionId#{0} is specifically not published'.
                format(object_id, ))
        elif (collection.auth_token == 'published'):
            return collection
        elif message.has_key('subject'):
            auth_tokens = re.findall('^\[[A-z0-9_]*\]', message.get('subject'))
            if (len(auth_tokens) == 1):
                auth_token = auth_tokens[0]
                if (len(auth_token) == 12):
                    if (auth_token == collection.auth_token):
                        service.log.warn(
                            'Message authenticated to CollectionId#{0}'.
                            format(object_id, ))
                        return collection
                    else:
                        service.log.warn(
                            'Authentication token mismatch for '
                            'CollectionId#{0}'.
                            format(object_id, ))
                else:
                    service.log.warn(
                        'Authentication token "{0} has inappropriate length.'.
                        format(auth_token, ))
            else:
                # No authentication token in subject
                service.log.warn('No authentication token in message subject')
        return None

    def retrieve_route(context, service):
        route = context.run_command('route::get', name='CoilsSendToCollection')
        if (route is None):
            message = \
                'Built-In route "{0}" available.'.\
                format('CoilsSendToCollection')
            service.log.warn(message)
            service.send_administrative_notice(
                subject='Unable to marshall route requested via SMTP',
                message=message,
                urgency=7,
                category='workflow',
                attachments=[], )
            return None
        return route

    collection = authenticate_collection(object_id=object_id,
                                         message=message,
                                         context=context,
                                         service=service, )
    if (collection is not None):
        # Authentication token is now removed from the message subject!
        message.replace_header('subject', message.get('subject')[12:])
        route = retrieve_route(context=context, service=service)
        if (route is not None):
            '''
            Serialize the message in a temporary file, this will be in the
            input of our OIE route
            '''
            tmp = BLOBManager.ScratchFile()
            g = Generator(tmp, mangle_from_=False, maxheaderlen=60)
            g.flatten(message)
            tmp.seek(0)
            #
            # Create and start the process
            #
            process = context.run_command(
                'process::new',
                values={'route_id': route.object_id,
                        'handle':   tmp,
                        'priority': 210, }, )
            process.owner_id = collection.owner_id
            context.property_manager.set_property(
                process,
                'http://www.opengroupware.us/oie',
                'xattr_collectionid',
                str(object_id), )
            context.commit()
            BLOBManager.Close(tmp)
            context.run_command('process::start', process=process, runas=10100)
            message = \
                'Requesting to start ProcessId#{0} / RouteId#{0}.'.\
                format(process.object_id, route.object_id, )
            service.log.info(message)
        else:
            service.log.error(
                'OIE Route entity for message delivery to Collection '
                'entities not available')
