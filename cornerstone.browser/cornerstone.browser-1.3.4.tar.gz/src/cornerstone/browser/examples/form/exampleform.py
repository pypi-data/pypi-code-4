from repoze import formapi
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from cornerstone.browser.form import FormRenderer

class ExampleForm(formapi.Form):
    
    fields = {
        'mytextinput': unicode,
        'myselection': unicode,
    }
    
    @formapi.validator('mytextinput')
    def check_mytextinput(self):
        if self.data['mytextinput'].strip() == '':
            yield 'Kein Input angegeben.'
    
    @formapi.validator('myselection')
    def check_myselection(self):
        if self.data['myselection'] == '-':
            yield 'Kein Auswahl getroffen.'
    
    @formapi.action("save")
    def save(self, data):
        # zope context available at self._context
        # and zope request available at self._request
        print 'save some data'

class ExampleFormRenderer(FormRenderer):
    
    template = ViewPageTemplateFile(u'exampleform.pt')
    factory = ExampleForm
    
    @property
    def nexturl(self):
        return self.makeUrl(self.context)
    
    @property
    def formaction(self):
        return self.makeUrl(self.context, resource='@@exampleformview')
    
    @property
    def myselectionvocab(self):
        """A Selection Vocab is always a list of 3-Tuples containing ``key``,
        ``value`` and ``bool`` if item is selected.
        """
        return [
            ['-', '-', False],
            ['key1', 'Value 1', False],
            ['key2', 'Value 2', False],
        ]