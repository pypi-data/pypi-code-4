from tg import TGController, expose
from tg import tmpl_context as c
from tw.api import WidgetsList
from tw.forms import (
    TableForm,
    TextField,
)
from abl.jquery.core.widgets import DefaultTextField


class MyForm(TableForm):
    class children(WidgetsList):
        text = TextField()
        more_text = DefaultTextField(default="type something in here ...")

my_form = MyForm('my_form')


class DefaultTextController(TGController):

    @expose('abl.jquery.examples.onload_focus.templates.index')
    def index(self, **kwargs):
        c.my_form = my_form
        return dict()
