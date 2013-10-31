import cgi
from base import XBrowserView
import urllib
from tmpl import HTMLRendererMixin
from ZPublisher.HTTPRequest import FileUpload

def safe_escape(value):
    if value:
        return cgi.escape(value)
    return value

class FormRenderer(XBrowserView, HTMLRendererMixin):
    """An abstract form renderer and processor for repoze.formapi.
    """
    
    template = None
    factory = None
    nexturl = None
    
    @property
    def formname(self):
        return ''
    
    @property
    def actionnames(self):
        return dict()
    
    @property
    def defaultvalues(self):
        return dict()
    
    @property
    def formaction(self):
        return self.makeUrl(self.context)
    
    def textinput(self, name):
        value = self.formvalueordefault(name)
        payload = self._tag('input',
                            type='text',
                            name=name,
                            value=safe_escape(value))
        return self.wraperror(name, payload)
    
    def selectioninput(self, name, vocab, multiple=None):
        if multiple:
            payload = self._selection(vocab, name=name, multiple='multiple')
        else:
            payload = self._selection(vocab, name=name)
        return self.wraperror(name, payload)
    
    def checkboxinput(self, name, value=None):
        fod = self.formvalueordefault(name)
        cb = self.formvalueordefault('%s_cb' % name)
        if not value:
            if isinstance(fod, list):
                raise ValueError(u'could not set default value')
            else:
                value = fod
        cbkw = {
            'type': 'checkbox',
            'name': name,
            'value': safe_escape(value),
        }
        if not isinstance(fod, list):
            fod = [fod]
        cb = self.formvalueordefault('%s_cb' % name)
        if cb and value in fod:
            cbkw['checked'] = 'checked'
        cbinput = self._tag('input', **cbkw)
        cbmarker = self.hiddeninput('%s_cb' % name, '1')
        return self.wraperror(name, '\n'.join([cbinput, cbmarker]))
    
    def radioinput(self, name, value):
        default = self.formvalueordefault(name)
        cbkw = {
            'type': 'radio',
            'name': name,
            'value': safe_escape(value),
        }
        if default == value:
            cbkw['checked'] = 'checked'
        payload = self._tag('input', **cbkw)
        return self.wraperror(name, payload)
    
    def textareainput(self, name, **kw):
        value = self.formvalueordefault(name)
        if not value:
            value = ''
        payload = self._tag('textarea',
                            safe_escape(value),
                            name=name,
                            **kw)
        return self.wraperror(name, payload)
    
    def passwordinput(self, name):
        payload = self._tag('input',
                            type='password',
                            name=name)
        return self.wraperror(name, payload)
    
    def fileinput(self, name):
        payload = self._tag('input',
                            type='file',
                            name=name)
        return self.wraperror(name, payload)
    
    def hiddeninput(self, name, value):
        return self._tag('input', type='hidden', name=name,
                         value=safe_escape(value))
    
    def displayinput(self, name):
        value = self.formvalueordefault(name)
        if value is None:
            return u''
        return self._tag('span',
                         self._tag('span', value),
                         self.hiddeninput(name, safe_escape(value)),
                         class_='displayinput')
    
    def renderedaction(self, name, multisubmit=False):
        if name == 'default':
            fieldname = self.formname
        else:
            fieldname = '%s.%s' % (self.formname, name)
        if multisubmit:
            class_ = 'formaction allowMultiSubmit'
        else:
            class_ = 'formaction'
        return self._tag('input',
                         type='submit',
                         name=fieldname,
                         _class=class_,
                         value=self.actionnames.get(name, name))
    
    def wraperror(self, name, payload):
        message = self.form.errors._dict.get(name)
        if not message:
            return self._tag('div',
                             payload,
                             _class='field')
        message = ', '.join(message._messages)
        return self._tag('div',
                         self._tag('div', message, _class='message'),
                         self._tag('div', payload, _class='field'),
                         _class='error')
    
    def formvalueordefault(self, name):
        value = self.form.data[name]
        if not value:
            value = self.request.form.get(name, None)
        if not value:
            value = self.defaultvalues.get(name, None)
        if isinstance(value, basestring):
            return urllib.unquote(value)
        return value
    
    def __call__(self):
        self.succeed = False
        self.processform()
        if self.succeed:
            if self.nexturl:
                self.redirect(self.nexturl)
                return
        return self.template()
    
    def processform(self):
        params = dict()
        params.update(self.request.form)
        for key in params.keys():
            if isinstance(params[key], basestring):
                params[key] = params[key].decode('utf-8')
        self.form = self.factory(data=self.defaultvalues,
                                 params=params,
                                 prefix=self.formname)
        if self.form.action:
            # XXX: provide following attributes via annotation
            setattr(self.form, '_request', self.request)
            setattr(self.form, '_context', self.context)
            if self.form.validate():
                self.form()
                self.succeed = True
