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

import string
from email.generator import Generator
from datetime import datetime
from coils.core import Folder, Document, ObjectProperty, CoilsException


from smtp_common import \
    get_mimetypes_for_target, \
    transcode_to_filename, \
    parse_message_from_string, \
    parse_message_from_stream, \
    get_raw_message_stream, \
    get_streams_from_message, \
    get_properties_from_message, \
    week_range_name_of_date


def walk_to_subdirectory(target, context, ):
    '''
    Check to see if the target [Folder] has a "subfolderPattern' property
    and if so attempt to walk to or create the path maching that pattern.
    '''

    sub_target = target
    prop = context.property_manager.get_property(
        target,
        'http://www.opengroupware.us/smtp',
        'subfolderPattern', )
    if prop:
        value = prop.get_value()
        if not isinstance(value, basestring):
            raise CoilsException(
                '"subfolderPattern" property value is not a string')

        today = datetime.today()
        value = value.replace('$__YEAR__;', today.strftime('%Y'))
        value = value.replace('$__MONTH__;', today.strftime('%m'))
        value = value.replace('$__DAYOFMONTH__;', today.strftime('%d'))
        value = value.replace('$__WEEKOFMONTH__;',
                              week_range_name_of_date(today))

        path_components = value.split('/')
        for path_component in path_components:

            if not path_component:
                '''
                Something like " fred//george" will be treated like
                "fred/george" we skip the empty parts
                '''
                continue

            folder = context.run_command('folder::ls',
                                         folder=sub_target,
                                         name=path_component, )
            if folder and len(folder) == 1:
                folder = folder[0]
                if not isinstance(folder, Folder):
                    raise CoilsException(
                        '"subfolderPattern" path includes a non-folder OGo#{0}'.
                        format(folder.object_id, ))
                sub_target = folder
            else:
                sub_target = context.run_command(
                    'folder::new',
                    folder=sub_target,
                    values={'name': path_component, }, )

    return sub_target


def smtp_send_to_folder(service, context, object_id, message, from_, to_):

    def save_streams(context, folder, props, streams, mimetype, ):
        for filename, stream in streams.items():
            # Create the document
            stream.seek(0)
            document = context.run_command('document::new',
                                           name=filename,
                                           handle=stream,
                                           values={},
                                           folder=folder,
                                           access_check=False, )
            for prop in props:
                context.property_manager.set_property(
                    document, prop[0], prop[1], prop[2], )
            context.property_manager.set_property(
                document,
                'http://www.opengroupware.us/mswebdav',
                'contentType',
                mimetype, )

        return True

    folder = context.run_command('folder::get', id=object_id, )
    if folder is None:
        service.log.warn(
            'OGo#{0} [Folder] not available to the NetworkContext'.
            format(object_id, ))
        service.send_administrative_notice(
            subject=
            'Insufficient permissions to deliver SMTP message to folder',
            message=
            'Attempt to delivery message from {0} to folder OGo#{1}.\n'
            'Cannot marshall folder.\n'.format(from_, object_id, ),
            urgency=5,
            category='security',
            attachments=[], )
        return

    mimetypes = get_mimetypes_for_target(target=folder, context=context, )
    folder = walk_to_subdirectory(target=folder, context=context, )

    rights = context.access_manager.access_rights(folder)
    '''
    Allow post-to-folder to proceed so long as the context has write, admin,
    insert "insert" is a useful permission as it should only allow object
    creation and not the ability to modify the folder itself
    '''
    if not set('wai').intersection(rights):
        service.log.warn(
            'OGo#{0} [Folder] not available for "insert" operations '
            'by NetworkContext'.format(object_id, ))
        service.send_administrative_notice(
            subject='Insufficient permissions to deliver SMTP message to folder',
            message='Attempt to delivery message from {0} to folder OGo#{1}.\nInsert access required.\n'.format(from_, object_id, ),
            urgency=5,
            category='security',
            attachments=[])
        return

    for mimetype in mimetypes:
        message_id, streams, rejects = \
            get_streams_from_message(message=message,
                                     mimetype=mimetype,
                                     logger=service.log, )
        if not streams and not rejects:
            service.log.debug(
                'No streams of type "{0}" discovered from message'.
                format(mimetype, ))
            continue
        service.log.debug(
            'Found {0} streams of type "{1}" in message.'.
            format(len(streams) + len(rejects), mimetype, ))
        props = get_properties_from_message(message)
        if streams:
            service.log.debug(
                'Found {0} *valid* streams of type "{1}" in message.'.
                format(len(streams), mimetype, ))
            save_streams(context, folder, props, streams, mimetype=mimetype, )
        if rejects:
            service.log.debug(
                'Found {0} *damaged* streams of type "{1}" in message.'.
                format(len(rejects), mimetype, ))
            props.append(
                ('57c7fc84-3cea-417d-af54-b659eb87a046', 'damaged', 'YES', )
            )
            props.append(
                ('57c7fc84-3cea-417d-af54-b659eb87a046',
                 'suspectMIMEType',
                 mimetype, )
            )
            save_streams(context, folder, props, rejects,
                         mimetype='application/octet-stream', )

    context.commit()
