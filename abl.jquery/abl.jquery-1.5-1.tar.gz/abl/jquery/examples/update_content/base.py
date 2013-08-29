from tg import TGController, expose
from tg import tmpl_context as c
from tg.decorators import with_trailing_slash
from tw.api import Widget

from abl.jquery.core.widgets import AjaxUpdateContentWidget

update_widget = AjaxUpdateContentWidget('update_widget')


class UpdateContentController(TGController):

    @expose('abl.jquery.examples.update_content.templates.index')
    @with_trailing_slash
    def index(self, **kwargs):
        c.update_widget = update_widget
        return dict()


    @expose('abl.jquery.core.templates.update_content')
    @with_trailing_slash
    def content(self):
        #Use a generic content and create a return dict like
        #this. box1 and box2 are defined as containers in index.html
        return dict(content=dict(box1='New content for box1',
                                 box2="And new stuff for box2"))
