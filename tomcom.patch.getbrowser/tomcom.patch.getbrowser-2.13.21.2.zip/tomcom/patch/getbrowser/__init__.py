from OFS.SimpleItem import Item
import warnings

import logging
logger = logging.getLogger('tomcom.patch.getbrowsr')

def get_browser(self, name):

    return self.restrictedTraverse('@@'+name, None)

def getBrowser(self, name):

    logger.warning('Item -> getBrowser is deprecated please use get_browser')

    return self.get_browser(name)


Item.get_browser = get_browser
Item.getBrowser = getBrowser
