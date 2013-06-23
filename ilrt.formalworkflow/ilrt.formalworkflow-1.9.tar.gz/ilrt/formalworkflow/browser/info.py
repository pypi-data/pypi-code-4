from plone.app.iterate.browser.info import BaselineInfoViewlet
from AccessControl import getSecurityManager

class BaselineInfoViewlet(BaselineInfoViewlet):
    """ Added to alter security declaration to allow editors
        to see info viewlet """

    def render(self):
        if self.working_copy() is not None and \
          getSecurityManager().checkPermission('Copy or Move', self.context):
            return self.index()
        else:
            return ""
