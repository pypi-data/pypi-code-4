from Products.CMFCore.utils import UniqueObject 
from OFS.SimpleItem import SimpleItem 
from Products.CMFCore.utils import getToolByName, _checkPermission
from Products.CMFCore.permissions import ModifyPortalContent
from zope.interface import implements
from Products.statusmessages.interfaces import IStatusMessage

from zettwerk.clickmap import clickmapMessageFactory as _
from zettwerk.clickmap.interfaces import IClickmap

from BTrees.IOBTree import IOBTree
from BTrees.OOBTree import OOBTree
from BTrees.IIBTree import IIBTree

from time import time
import drawer

from DateTime import DateTime


class ClickmapTool(UniqueObject, SimpleItem): 
    """ Tool that handles logging and viewing of clikcs """ 

    implements(IClickmap)
    id = 'portal_clickmap' 

    ## internal attributes
    logger = None
    enabled = False
    pages = [] ## the list of uids, which gets logged
    output_width = 1024
    output_height = 768
    right_align_threshold = 0

    def isThisPageDoLogging(self, uid, context):
        """
        return True or False, to control the js functionality
        edit users always gets False, cause the layout differs heavily from the
        normal views.
        """
        if _checkPermission(ModifyPortalContent, context):
            return False

        if uid in self.pages and self.enabled:
            return True

        return False

    def getControlPanel(self):
        """ some html for the overlay control in the output of the image. """

        (yesterday, now) = self._getDefaultTimespan()
        default_start = yesterday.strftime('%Y/%m/%d %H:%M')
        default_end = now.strftime('%Y/%m/%d %H:%M')
        
        returner = []
        returner.append(u'<form id="clickmap_output_controller_form" style="float: left;">')
        returner.append(u'<h5>%s</h5>' %(_(u"Clickmap output controller")))
        returner.append(u'<input type="text" name="start" value="%s"> %s <br />' %(default_start, _(u"Start time")))
        returner.append(u'<input type="text" name="end" value="%s"> %s <br />' %(default_end, _(u"End time")))
        returner.append(u'<input type="submit" name="refresh" value="%s">' %(_(u"Refresh")))
        returner.append(u'</form>')
        returner.append(u'<br style="clear: both;" />')
        return '\n'.join(returner)

    def _getDefaultTimespan(self):
        """ return the inital timestop for the output controller: 1 day """
        now = DateTime()
        yesterday = now - 1
        return (yesterday, now)

    def drawImage(self, uid, start=None, end=None):
        """ read the requested data and generate the output image """

        if not start or not end:
            start, end = self._getDefaultTimespan()
        else:
            try:
                start = DateTime(start)
                end = DateTime(end)
            except:
                start, end = self._getDefaultTimespan()

        ## transform the DateTime objects to integer seconds
        start = int(start)
        end = int(end)
        
        coords = self._getCoordsByUid(uid,
                                      start=start,
                                      end=end)

        imagepath = drawer.do(self.output_width,
                              self.output_height,
                              coords)
        
        r = self.REQUEST.RESPONSE
        r.setHeader('content-type', 'image/png')
        i = open(imagepath, 'rb')
        b = i.read()
        i.close()

        r.write(b)

    def _getCoordsByUid(self, uid, start, end):
        """ """
        uid_log = self.logger.get(uid)
        if uid_log is not None:
            return self._transformLogToCoordsToDraw(uid_log, start, end)

        return [] ## fallback

    def _transformLogToCoordsToDraw(self, log_data, start, end):
        """ """
        result = {}
        for timestamp, coord in log_data.items(start,
                                               end):

            x, y = coord[0], coord[1]
            key = (x, y)
            value = result.get(key, 1)
            result[key] = value + 1

        return ((item[0], item[1], value) for item, value in result.items())
    
    def initLogger(self, force=False):
        """
        a wrapper for _initLogger, which checks some conditions.
        @param force: boolean, to force reset the logger
        @returns: redirects to the controlpanel form
        """
        if self.logger is not None and force:
            self.logger = None

        if self.logger is None:
            self._initLogger()
            message = _(u"Clickmap logger initialized.")
            IStatusMessage(self.REQUEST).addStatusMessage(message, type='info')            
            self.REQUEST.RESPONSE.redirect('%s/@@clickmap-controlpanel' \
                                                  %(getToolByName(self, 'portal_url')()))
            return
        
        return str(doInit)

    def _initLogger(self):
        """ reset the logger attribute """
        self.logger = OOBTree()
        
    def _get_uid_log(self, uid):
        """
        return the IOBTree that holds the data of the given uid. If there is no
        one for the requested uid, create it.
        """
        if self.logger is None:
            self._initLogger()
            
        uid_log = self.logger.get(uid)
        if uid_log is None:
            uid_log = IOBTree()
            self.logger[uid] = uid_log
        return uid_log

    def _remove_uid_from_log(self, uid):
        """
        remove a logged page from the logger
        """
        if self.logger.get(uid) is not None:
            del self.logger[uid]
            
    def _store_request(self, uid, log_data):
        """
        store the request.
        @param uid: the uid of the object to log
        @param log_data: the IIBTree object to store
        """
        uid_log = self._get_uid_log(uid)
        uid_log[int(time())] = log_data

    def clicker(self, uid, x, y, w):
        """
        the parameters are stored transformed to the reference layout
        """
        if w > self.output_width: 
            return "" ## sorry, we dont support this...

        if x > self.right_align_threshold:
            x += (self.output_width - w)
            
        log_data = IIBTree([(0, x),
                            (1, y)])
        self._store_request(uid,
                            log_data)
        return "ok"

    def debug_info(self):
        """
        transform the logged data to readable data for debugging...
        """
        result = {}
        for uid, log in self.logger.items():
            log_data = []
            for timestamp, data in log.items():
                log_data.append("%s: x -> %s | y -> %s" %(timestamp, data[0], data[1]))
            result[uid] = log_data

        import pprint
        pprint.pprint(result)
        return "see console output...."
