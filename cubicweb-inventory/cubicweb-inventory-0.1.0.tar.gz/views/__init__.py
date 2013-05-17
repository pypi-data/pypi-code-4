"""inventory web user interface"""

from cubicweb.web import uicfg
from cubicweb.web.views.urlrewrite import SimpleReqRewriter
from cubicweb.web import uihelper

uihelper.edit_as_attr('DeviceModel', 'made_by')
