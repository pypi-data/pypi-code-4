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
import string, time, os, base64, shutil
from datetime        import datetime, timedelta
from shlex           import split as _split
from email.generator import Generator
from email.Parser    import Parser
from coils.core      import BLOBManager, ServerDefaultsManager

global EXTENSION_MAP

EXTENSION_MAP = None

TRANSCODE_MAP = string.maketrans(' <>%&/\\', '____---' )

INTERESTING_HEADERS = ( 'subject', 'x-spam-level', 'from', 'to', 'date',
                        'x-spam-status', 'reply-to', 'x-virus-scanned',
                        'x-bugzilla-classification', 'x-bugzilla-product',
                        'x-bugzilla-component', 'x-bugzilla-severity',
                        'x-bugzilla-status', 'x-bugzilla-url', 'x-mailer',
                        'x-original-sender', 'mailing-list', 'list-id',
                        'x-opengroupware-regarding', 'x-opengroupware-objectid',
                        'x-original-to', 'in-reply-to', 'cc',
                        'x-gm-message-state',  )


#TODO: THis is not required in Python 2.7, can we check the running version
#      and automatically toggle on/off this version work-around HACK?
safe_split = lambda a: [ b.decode( 'utf-8' ) for b in _split( a.encode( 'utf-8' ) ) ]


def get_mimetypes_for_target(target, context):
    mimetypes = [ 'message/rfc822', ]
    prop = context.property_manager.get_property( target, 'http://www.opengroupware.us/smtp', 'collectMIMEType' )
    if prop:
        mimetypes = [ x.strip( ) for x in prop.get_value( ).split( ',' ) ]
    return mimetypes


def transcode_to_filename( filename ):
    return filename.translate( TRANSCODE_MAP )


def parse_message_from_string( data ):
    return Parser( ).parsestr( data )


def parse_message_from_stream( rfile ):
    return Parser( ).parse( rfile )


def get_raw_message_stream( message ):
    '''
    Retrun a stream of the full flattened message
    :param message: a message object
    '''
    s = BLOBManager.ScratchFile( encoding='binary' )
    g = Generator( s, mangle_from_=False, maxheaderlen=255 )
    g.flatten( message )
    return s

def reliably_decode_message_section( section, sfile ):
    '''
    Reliably decode a message section to the specified stream.  This
    function works around the *COMPLETLEY BROKEN* behavior of the
    Python standard library's get_payload message method.
    :param section: An e-mail section having content
    :param sfile: Stream to receive the section's content
    '''
    if section.get( 'Content-Transfer-Encoding' ) == 'base64':
        wfile = BLOBManager.ScratchFile( )
        # DO NOT LET THE STANDARD LIBRARY AUTO-DECODE A BASE64
        # ENCODED SECTION - if the encoding is bad it will return
        # the *RAW* data *AND* raise *NO EXCEPTION*,  it just gives you
        # swill you think is the specified data-type.  Here we will
        # attempt to correct bad-padding and then decode the section
        # outselves.
        wfile.write( section.get_payload( decode=False ) )
        unpadded = wfile.tell( ) % 4
        if unpadded:
            wfile.seek( -1, os.SEEK_END )
            char = wfile.read( 1 )
            if ord(char) == 10:
                wfile.seek( -1, os.SEEK_END )
            else:
                wfile.seek( 0, os.SEEK_END )
            wfile.write( '=' * unpadded )
        wfile.seek( 0 )
        try:
            base64.decode( wfile, sfile )
        except base64.binascii.Error:
            wfile.seek( 0 )
            # put the raw data in to the stream so it gets stashed as a reject
            shutil.copyfileobj( wfile, sfile )
            raise CoilsException( 'Unable to decode content of section {0}'.format( section ) )
        finally:
            BLOBManager.Close( wfile )
    else:
        sfile.write( section.get_payload( decode=True ) )

def get_streams_from_message( message, mimetype, logger ):
    '''
    Retrieve the stream(s) from the provided message object that are of
    the request MIME type.  If the mimetype is "message/rfc833" then a
    single stream of the entire message, including all parts, is
    returned [essentially the message is flattened].  If the message is
    not multipart and the MIME type is "text/plain" then a copy of the
    text message body is produced as a stream.  Otherwise when the
    message is multipart and a normal MIME type is specified then just
    the outer parts of the messages matching that type are returned.
    Return value is a dict where keys are filenames and the value is
    a stream.  The filenames are NOT those provided with whatever the
    part is [they may not even have filenames] but are generated file-
    names. An attempt is made to have a correctish file extension.
    :param message: Message object
    :param mimetype: MIME type string
    :param logger: A logger object for the function to use
    '''
    global EXTENSION_MAP

    if not EXTENSION_MAP:
        sd = ServerDefaultsManager()
        mimetype_map = sd.default_as_dict( 'CoilsExtensionMIMEMap' )
        EXTENSION_MAP = dict( ( v, k ) for k, v in mimetype_map.iteritems( ) )

    message_id = message.get( 'message-id' )
    streams = { }
    rejects = { }
    if mimetype == 'message/rfc822':
        filename = transcode_to_filename( '{0}.{1}.mbox'.format( message_id, time.time( ) ) )
        streams[ filename ] = get_raw_message_stream( message )
        logger.debug( 'Saving full raw message' )
    elif message.is_multipart( ):
        extension = EXTENSION_MAP.get( mimetype, 'part' )
        counter = 0
        for section in message.get_payload():
            if section.get_content_type() == mimetype:
                counter += 1
                filename = transcode_to_filename( '{0}.{1}.{2}.{3}'.format( message_id, counter, time.time( ), extension ) )
                if not section.is_multipart( ):
                    s = BLOBManager.ScratchFile( encoding='binary' )
                    try:
                        reliably_decode_message_section( section, s )
                    except:
                        rejects[ filename ] = s
                    else:
                        streams[ filename ] = s
                else:
                    streams[ filename ] = get_raw_message_stream( section )
        logger.debug( 'Found {0} parts in message of type "{1}"'.format( counter, mimetype ) )
    elif mimetype == 'text/plain':
        s = BLOBManager.ScratchFile( encoding='binary' )
        s.write( message.get_payload( ) )
        streams[ transcode_to_filename( '{0}.{1}.txt'.format( message_id, time.time( ) ) ) ] = s
        logger.debug( 'Saving text of non-multipart message' )
    else:
        logger.debug( 'No candidate parts of message to save' )
    return message_id, streams, rejects


def get_properties_from_message( message, ):
    '''
    Produce a set of properties from the message and include the MIME type.
    :param message: a message object
    :param mimetype: the MIME type to include
    '''
    message_id = message.get( 'message-id' )
    props = [ ( 'us.opengroupware.mail.header', 'message-id', message_id, ), ]
    for header in INTERESTING_HEADERS:
        if message.has_key( header ):
            props.append( ( 'us.opengroupware.mail.header', header, message.get( header ), ) )
    return props


def week_ranges_of_month(year, month):
    weeks = [ ]
    tmp = datetime( year, month, 1 )
    week = [ ]
    while tmp.month == month:
        week.append( tmp.day )
        if tmp.weekday() == 6:
            weeks.append( week )
            week = [ ]
        tmp += timedelta(days = 1)
    if week:
        weeks.append( week )
    return weeks


def week_offset_of_date(dt):
    week_ranges = week_ranges_of_month( dt.year, dt.month )
    counter = 0
    for week in week_ranges:
        if dt.day in week:
            break
        counter += 1
    return counter + 1, week_ranges[counter][0], week_ranges[counter][-1]


def week_range_name_of_date(dt):
    week_number, start_day, end_day = week_offset_of_date( dt )
    return '{0:02d}-{1:02d}'.format( start_day, end_day )
