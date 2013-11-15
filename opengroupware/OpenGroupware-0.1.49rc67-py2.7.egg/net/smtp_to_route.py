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
from smtp_common import \
    get_mimetypes_for_target, \
    transcode_to_filename, \
    parse_message_from_string, \
    parse_message_from_stream, \
    get_raw_message_stream, \
    get_streams_from_message, \
    get_properties_from_message


def smtp_send_to_route(from_, to_, message, context, service):
    # This is meant to trigger a workflow!
    route = context.run_command('route::get', name=to_, )
    if route:
        mimetype = 'application/octet-stream'
        service.log.warn(
            'Creating process from route routeId#{0}'.
            format(route.object_id, ))
        if message.is_multipart():
            message = \
                'A multipart message was submitted to routeId#{0}'.\
                format(route.object_id, )
            service.send_administrative_notice(
                subject='Multipart message submitted to workflow',
                message=message,
                urgency=8,
                category='workflow',
                attachments=[], )
        else:
            # Single part message
            try:
                '''
                payload = message.get( 'Subject' )
                 For a non-multipart message the get_payload
                returns the message body
                '''
                payload = message.get_payload(decode=True, )
                mimetype = 'text/plain'
            except Exception as exc:
                service.log.exception(exc)
            else:
                process = context.run_command(
                    'process::new',
                    values={'route_id': route.object_id,
                            'data':  payload,
                            'priority': 210, },
                    mimetype=mimetype, )
                context.property_manager.set_property(
                    process,
                    'http://www.opengroupware.us/oie',
                    'xattr_from',
                    from_, )
                context.commit()
                context.run_command('process::start', process=process, )
                message = \
                    'Requesting to start ProcessId#{0} / RouteId#{0}'.\
                    format(process.object_id, route.object_id, )
                service.log.info(message)
    else:
        message = \
            'No such route as "{0}" available in the network context\n' \
            'From: {1}\n'.format(to_, from_, )
        service.log.warn(message)
        service.send_administrative_notice(
            subject='Unable to marshall route requested via SMTP',
            message=message,
            urgency=7,
            category='workflow',
            attachments=[], )
