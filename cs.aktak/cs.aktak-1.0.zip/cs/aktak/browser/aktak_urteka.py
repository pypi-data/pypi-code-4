
__version__ = '$Id$'

from Products.CMFPlone import utils



__version__ = '$Id$'

from Products.CMFPlone import utils

import DateTime
import pdb
from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
import random
class Aktak(BrowserView):

	def __call__(self):
                
		context=aq_inner(self.context)
                urteak=context.getFolderContents({'portal_type':'DonEdukia'})
                dict={}
                for urtea in urteak:
                    aktak=urtea.getObject().getFolderContents({'portal_type':'File'}, full_objects=1)
                    dict[urtea.Title]=aktak
                return dict
