from random import randint

from tg import TGController, expose
from tg import tmpl_context as c
from tg.decorators import paginate
from tw.api import Widget
from abl.jquery.core.utils import partial_action
from abl.jquery.core.widgets import AjaxPager


class MyList(Widget):
    template = "abl.jquery.examples.pager.templates.my_list"
    engine_name = "genshi"


horizontal_widget = AjaxPager('horizontal_list',
                              widget=MyList('horizontal_list_child'))

vertical_widget = AjaxPager('vertical_list',
                            widget=MyList('vertical_list_child'),
                            pager_type='vertical')


#this is maybe a database query
names = ['Alice', 'Bob']
words = ['foo', 'bar', 'baz', 'hello', 'world']
my_list=["%i %s %s" % (i,
                       names[randint(0,1)],
                       words[randint(0,4)]) for i in range(50)]
horizontal_list = my_list
vertical_list = my_list


class PagerController(TGController):

    @expose('abl.jquery.examples.pager.templates.index')
    @paginate("horizontal_list", items_per_page=10, use_prefix=True)
    @paginate("vertical_list", items_per_page=10, use_prefix=True)
    def index(self, **kwargs):
        partial = partial_action(self.index,
                                 horizontal_widget,
                                 horizontal_list,
                                 **kwargs)
        if partial:
            return partial

        partial = partial_action(self.index,
                                 vertical_widget,
                                 vertical_list,
                                 **kwargs)
        if partial:
            return partial

        c.horizontal_widget = horizontal_widget
        c.vertical_widget = vertical_widget

        return dict(vertical_list=vertical_list,
                    horizontal_list=horizontal_list)
