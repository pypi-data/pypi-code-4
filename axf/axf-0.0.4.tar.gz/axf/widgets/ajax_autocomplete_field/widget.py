from tw2 import forms
from tw2.core import Param, Link
from axf.axel import AxelWidgetMixin, AxelScript, AxelStyle


class AjaxAutocompleteField(forms.InputField, AxelWidgetMixin):
    type = 'hidden'
    resources = [Link(filename='/resources/select2.png'),
                 Link(filename='/resources/spinner.gif'),
                 Link(filename='/resources/select2x2.png'),
                 Link(filename='/resources/new_arrow.png')]
    axel_styles = [AxelStyle('select2-style', '/resources/select2.css')]
    axel_scripts = [AxelScript('jquery', 'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
                               load=False),
                    AxelScript('select2', 'resources/select2.min.js', load=False),
                    AxelScript('AjaxAutocompleteField', 'scripts.js', load=False,
                               callback='AjaxAutocompleteField_init'),
                    AxelScript(['jquery', 'select2', 'AjaxAutocompleteField'], load=True)]

    multiple = Param('Multiple selection enabled', request_local=False, default=False)
    datasource = Param('Url that will be called to retrieve the data', request_local=False)
    inverse_datasource = Param('Url that will be called to resolve selected entry', request_local=False)
    placeholder = Param('Placeholder to show when no selection is available',
                        default="Search for a city", request_local=False)

    def prepare(self):
        super(AjaxAutocompleteField, self).prepare()
        options = {'multiple':self.multiple}
        self.axel_prepare(str(self.placeholder), self.datasource, self.inverse_datasource, options)
