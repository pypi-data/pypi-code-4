#
# Copyright (c) 2011, 2012, 2013
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
import uuid, traceback, multiprocessing
from coils.core          import *
from edition             import AUTOTHUMBNAILER_VERSION

from thumbnail_image     import ThumbnailImage
from thumbnail_pdf       import ThumbnailPDF

from events              import AUTOTHUMB_NAIL_REQUEST, \
                                AUTOTHUMB_NAIL_CREATED, \
                                AUTOTHUMB_NAIL_FAILED

from edition import AUTOTHUMBNAILER_VERSION

THUMBERS = {'image/jpeg':       ThumbnailImage,
            'image/png':        ThumbnailImage,
            'application/pdf' : ThumbnailPDF,  }

class ThumbWorker(MultiProcessWorker):

    def __init__(self, name, work_queue, event_queue, ):
        MultiProcessWorker.__init__( self, name, work_queue, event_queue )
        self.context = AdministrativeContext( )

    def process_worker_message(self, command, payload ):
        if command in ( AUTOTHUMB_NAIL_REQUEST, ):
            try:
                object_id = long( payload )
            except Exception as e:
                self.log.exception(e)
                self.log.error( 'Unable to convert payload "{0}" to objectId'.format( payload ) )
                reurn

            if command == AUTOTHUMB_NAIL_REQUEST:
                self.thumbnail_document( object_id )
        self.context.db_close()

    def thumbnail_document(self, object_id):

        document = self.context.run_command( 'document::get', id=object_id )
        if not document:
            self.log.debug( 'Unable to marshall OGo#{0} [Document] for thumbnailing'.format( object_id ) )
            return
        self.log.debug( 'Autothumb service attempting to thumbnail OGo#{0} [Document]'.format( object_id ) )

        filename = '{0}.{1}.{2}.thumb'.format( document.object_id, AUTOTHUMBNAILER_VERSION, document.version )
        filename = 'cache/thumbnails/{0}/{1}/{2}'.format( filename[1:2], filename[2:3], filename )

        # TODO: If the current thumbnail exists, do not recaclulate

        mimetype = self.context.type_manager.get_mimetype( document )
        thumber = THUMBERS.get( mimetype, None )
        if thumber:
            thumber = thumber( self.context, mimetype, document, filename )
            try:
                if thumber.create( ):
                    self.log.debug( 'Thumbnail created for OGo#{0} [Document] of type "{1}"'.format( object_id, mimetype ) )
            except Exception, e:
                self.log.debug( 'Thumbnail creation failed for OGo#{0} [Document] of type "{1}"'.format( object_id, mimetype ) )
                self.log.exception(e)
                self.context.db_session( ).rollback( )
                self.enqueue_event( AUTOTHUMB_NAIL_FAILED, ( object_id, 'Document', traceback.format_exc(), ), )
            else:
                self.enqueue_event( AUTOTHUMB_NAIL_CREATED, ( object_id, ), )
            finally:
                thumber = None
