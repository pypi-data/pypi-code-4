from tg import TGController, expose
from tg import tmpl_context as c
from tw.api import WidgetsList
from tw.forms import (
    HiddenField,
    FieldSet,
    TextArea,
    TableForm,
    TextField,
)
from abl.jquery.core.widgets import GrowingFormFieldRepeater
from tw.forms import FormFieldRepeater


class MyForm(TableForm):
    class children(WidgetsList):
        infos = GrowingFormFieldRepeater(widget=FieldSet(fields=[HiddenField('id'),
                                                                 TextField('data'),
                                                                 TextField('more_data')]))
        more_infos = FormFieldRepeater(widget=FieldSet(fields=[HiddenField('id'),
                                                               TextField('data'),
                                                               TextField('more_data')]))

my_form = MyForm('my_form')


class GrowingController(TGController):

    @expose('abl.jquery.examples.growing.templates.index')
    def index(self, **kwargs):

        c.my_form = my_form

        form_data = dict(infos=[dict(id=1, data='hello', more_data='world'),],
                         more_infos=[dict(id=1, data='hello', more_data='world'),])

        return dict(form_data=form_data)
