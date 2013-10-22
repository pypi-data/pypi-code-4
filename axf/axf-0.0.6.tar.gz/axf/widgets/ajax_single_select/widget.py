from axf.axel import AxelWidgetMixin, AxelScript
from tw2 import forms
from tw2.core import Param

class AjaxSingleSelectField(forms.SingleSelectField, AxelWidgetMixin):
    datasource = Param('Url that will be called to retrieve the data', request_local=False)
    onevent = Param('A tuple (id, event[currently ignored]) that specifies which event of which element' +
                    'triggers options to be reloaded from the datasource', request_local=False)
    axel_scripts = [AxelScript('jquery', 'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
                               load=False),
                    AxelScript('AjaxSingleSelectField', 'scripts.js', load=False,
                               callback='AjaxSingleSelectField_init'),
                    AxelScript(['jquery', 'AjaxSingleSelectField'], load=True)]

    def prepare(self):
        super(AjaxSingleSelectField, self).prepare()
        self.axel_prepare(self.onevent[0], self.onevent[1], self.datasource, self.value)
