
from cStringIO import StringIO
import zipfile

from zope.component import getUtility
from zope.component import getMultiAdapter
from plone.registry.interfaces import IRegistry
from Products.Five.browser import BrowserView
# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from c2.app.zipdownload.controlpanel.interfaces import IZipDownloadControlPanel

def _ex_charaset(s, enc, base_char='utf-8'):
    if not isinstance(s, unicode):
        s = s.decode(base_char)
    return s.encode(enc, 'ignore')


class ZipDownload(BrowserView):
    """

    """

    def __call__(self, *args, **kw):
        portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.portal = portal_state.portal()
        select = self.request.form.get('paths', [])
        if not select:
            return None

        content_id = self.context.id
        self.request.RESPONSE.setHeader('Content-Type', 'application/zip')
        self.request.RESPONSE.setHeader('Content-disposition',
                                'attachment;filename="%s.zip"' % content_id)
        return self.get_zip_data(select, content_id)

    def get_zip_data(self, select, content_id):
        enc = self._get_encoding_setting()
        out = StringIO()
        with zipfile.ZipFile(out, 'w') as z_file:
            for path in select:
                f_name, f_data = self.get_select_file(path)
                filename = '%s/%s' % (content_id, f_name)
                z_file.writestr(_ex_charaset(filename, enc), f_data)
        out.seek(0)
        return out.getvalue()

    def get_select_file(self, path):
        obj = self.portal.unrestrictedTraverse(path)
        o_type = obj.Type()
        if o_type == 'Image':
            fobj = obj.getImage()
            f_data = fobj.data
            f_name = fobj.filename
        elif o_type == "File":
            fobj = obj.getFile()
            f_data = fobj.data
            f_name = fobj.filename
        else:
            body = getattr(obj, 'getText', getattr(obj, 'getBody', lambda :""))()
            if body:
                f_data = body
                f_name = obj.title + ".html"
            else:
                f_data = body
                f_name = obj.title
        return f_name, f_data

    def _get_encoding_setting(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IZipDownloadControlPanel)
        return settings.encoding

