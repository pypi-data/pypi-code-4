from tw2.forms import SingleSelectField
from axf.axel import AxelWidgetMixin, AxelScript

class SingleSelectFieldWithAdd(SingleSelectField, AxelWidgetMixin):
    template = "axf.widgets.single_select_with_add.single_select_with_add"

    axel_styles = []
    axel_scripts = [AxelScript('jquery', 'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
                               load=False),
                    AxelScript('SingleSelectFieldWithAdd', 'scripts.js', load=False),
                    AxelScript(['jquery', 'SingleSelectFieldWithAdd'], load=True)]

    def prepare(self):
        super(SingleSelectFieldWithAdd, self).prepare()
        self.axel_prepare()
