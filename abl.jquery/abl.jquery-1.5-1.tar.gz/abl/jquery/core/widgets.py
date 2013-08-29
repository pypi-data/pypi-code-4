# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
An ajaxified pager for TurboGears. It requires the tg package.
"""

from formencode import All
from formencode.schema import Schema
from formencode.foreach import ForEach
from tg import tmpl_context as c
from tw.api import JSLink, CSSLink, Widget
from tw.forms import (
    FormFieldRepeater,
    TextField,
    TextArea,
)
from abl.jquery.core import jquery_js
from abl.jquery.core.base import jQuery


page_widget_js = JSLink(modname=__name__,
                        filename='static/javascript/jquery.ajax.pager.js',
                        javascript=[jquery_js])


class AjaxPager(Widget):
    """
    An ajaxified pager. It works with tg.decorators.paginate
    in a TurboGears controller action. There can be multiple
    paged containers on one site. The AjaxPagertakes care
    that the returned partial content will be replaced in
    the website.

    The basic concept is to add a pageable container to a website
    and to update/replace its content partially. When Javascript is
    disabled, the website will be reloaded completely.

    For usage see abl.jquery.examples.pager
    """

    template = "abl.jquery.core.templates.ajax_pager"
    engine_name = "genshi"

    params = dict(widget="""The widget to be displayed and paginated.
                            It will be called with the data given to the AjaxPager.""",
                  format="""The format of the pager, default is
                            $link_previous ~3~ $link_next . More Info: tg.decorators.paginate.Page""",
                  show_pager="""Defines where to show the pager. Values can be
                                'both', 'top', bottom. Default:'bottom'""",
                  pager_type="""default is a regular 'horizontal' pager. 'vertical' will load more content
                                instead of switching to the next page""",
                  symbol_next="""default is 'next'""",
                  symbol_previous="""default is 'previous'""",
                  symbol_more="""default is 'more'. Only used if pager_type is 'vertical'"""
                  )
    widget = Widget()
    show_pager = 'bottom'
    format = '$link_previous ~3~ $link_next'
    symbol_next='next'
    symbol_previous='previous'
    symbol_more='more'
    pager_type= 'horizontal'
    javascript = [page_widget_js,]

    def update_params(self, d):
        super(AjaxPager, self).update_params(d)

        if d.id is None:
            d.id = "pager_%i" % id(self)

        d.partial = d.get('partial', False)
        d.show_pager = self.show_pager
        paginator = getattr(c.paginators, d.id)
        pager = paginator.pager
        d.next_page = paginator.next_page
        link_attr = {'class':'pager_link'}

        d.pager = pager(d.format,
                        symbol_next=d.symbol_next,
                        symbol_previous=d.symbol_previous,
                        link_attr=link_attr)

        if d.pager_type == 'vertical':
            self.add_call(jQuery('#%s' % d.id).pager(dict(pager_type=d.pager_type)))
        else:
            self.add_call(jQuery('#%s' % d.id).pager())


growing_js = JSLink(
    javascript=[jquery_js],
    modname=__name__,
    filename='static/javascript/jquery.growing.js',
    )


class StripEmpty(Schema):
    """
    A validator that removes empty lines from a list
    of values. The list can contain dictionaries
    where keys with empty values are stripped.
    All other dict values become list elements
    Otherwise empty list elements are removed.
    """

    def _to_python(self, value_list, state):

        def allow(arg):
            if hasattr(arg, 'values'):
                return any((x != '' for x in arg.values()))
            else:
                return arg

        return [x for x in value_list if allow(x)]


class GrowingFormFieldRepeater(FormFieldRepeater):
    """
    Like FormFieldRepeater but it let the user click an 'add'
    button to add a new line instantly and let the user click
    an delete button on each filled line to remove the line.
    But the line is not deleted on the server it is only hidden
    so the request will not send the data to the server

    If a delete button was pressed a undo link will become
    available.
    """

    params = ['add_link_text', 'delete_link_text', 'undo_link_text']
    add_link_text = 'add'
    delete_link_text = 'delete'
    undo_link_text = 'undo'
    extra=1
    repetitions=1
    javascript = [growing_js]

    def __init__(self, id=None, parent=None, children=[], **kw):
        """
        Initializes the FormFieldRepeater and sets self._id
        """
        super(GrowingFormFieldRepeater, self).__init__(id,parent,children, **kw)
        self._id = id

    def post_init(self, *args, **kw):
        """
        Sets the validators, especially a StripEmpty validator that
        removes empty lines.
        """
        self.validator = All(ForEach(self.children[0].validator),
                             StripEmpty())

    @property
    def id_path_elem(self):
        """
        The parents property does not return the correct id,
        so this is a replacement.
        """
        return self._id

    def update_params(self, d):
        """
        Renders the form elements and additional links for
        add, delete and undo.
        """
        super(GrowingFormFieldRepeater, self).update_params(d)
        v_f = d['value_for']
        a_f = d['args_for']

        if 'has_error' in d["output"]:
            #don't add new fields on validation errors
            d.extra = 0

        outputs = []
        for i, w in enumerate(d['children'].__iter__(max(d['repetitions'], len(d['value']) + d.extra))):
            rendered_w = w.render(v_f(w), isextra=(w.repetition >= len(d['value'])), **a_f(w))

            if i >= len(d['value']):
                #dont display a delete button on empty lines
                outputs.append((rendered_w, 'style="display:none;"'))
            else:
                outputs.append((rendered_w, ''))

        #recreate the output
        form_elem_html = '<div class="grow_form_elem">%s<a href="" class="grow_form_delete_link" title="delete" %s >%s</a></div>'
        d["output"] = '\n'.join(form_elem_html % (rendered_w,
                                                  extra_style,
                                                  self.delete_link_text) \
                                for rendered_w, extra_style in outputs if rendered_w)
        if self.undo_link_text:
            undo_link = '<a href="" class="grow_form_undo_link" style="display:none;">%s</a>' % self.undo_link_text
        else:
            undo_link = ''

        if self.add_link_text:
            add_link = '<a href="" class="grow_form_add_link">%s</a>' % self.add_link_text
        else:
            add_link = ''


        d["output"]= "".join([undo_link,
                              '<div class="grow_form_payload">%s</div>' % d["output"],
                              add_link])

        self.add_call(jQuery('#%s\\.container' % self.id).grow_form())


update_content_js = JSLink(modname=__name__,
                           filename='static/javascript/jquery.update.content.js',
                           javascript=[jquery_js])


class AjaxUpdateContentWidget(Widget):
    """
    A widget that can reload content for multiple
    elements on the site.
    An element on the site with a class name like
    the widget id starts the Ajax load.

    For usage see
    abl.jquery.examples.update_content
    """

    javascript = [update_content_js]
    params = dict(url="""The URL that provides the data, optional.
                         If not given the trigger elements href will
                         be used""")
    url = ''

    def update_params(self, d):
        super(AjaxUpdateContentWidget, self).update_params(d)
        self.add_call(jQuery('.%s' % d.id).update_content(d.url))


class OnloadFocusMixin(Widget):
    """
    Makes a form field beeing focus when the page is loaded
    The field must have an id.
    """
    javascript=[jquery_js]

    def update_params(self, d):
        super(OnloadFocusMixin, self).update_params(d)
        self.add_call(
            """
            setTimeout( function() { $('#%s').focus(); }, 100 );
            """ % d.id
        )

class OnloadFocusTextField(TextField, OnloadFocusMixin):
    """
    A TextField that uses the onload focus.
    """
    pass


class OnloadFocusTextArea(TextArea, OnloadFocusMixin):
    """
    A TextArea that uses the onload focus.
    """
    pass


default_text_css = CSSLink(
    modname=__name__,
    filename='static/css/default_text.css'
)


default_text_js = JSLink(
    javascript=[jquery_js],
    modname=__name__,
    filename='static/javascript/jquery.default_text.js'
)


class DefaultTextMixin(Widget):
    """
    A default="text" can be used to display a text in a
    text field. If this field gets the focus the text
    will be removed.
    """
    javascript = [default_text_js]
    css = [default_text_css]

    def update_params(self, d):
        super(DefaultTextMixin, self).update_params(d)
        self.add_call(jQuery('#%s' % d.id).default_text())


class DefaultTextField(TextField, DefaultTextMixin):
    """
    A TextField with default text that disapears if it
    is focused.
    Usage:
    default="default text"
    """
    pass


class DefaultTextArea(TextArea, DefaultTextMixin):
    """
    A TextArea with default text that disapears if it
    is focused.
    Usage:
    default="default text"
    """
    pass
