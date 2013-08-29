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

from tg import override_template, request
from tg import tmpl_context as c

def partial_action(action, widget, data, **kwargs):
    """
    This can be use inside of a TG2 action that uses paging.
    It returns a partial content
    @action: the TG2 action
    @param widget: the widget that is paginated
    @param data: the data that should be returned, typically a list like object
    @kwargs: the kwargs of the action. That may contain 'partial'
    """
    name = widget.id
    page = '%s_page' % name

    if kwargs.get('partial') and request.GET.has_key(page):
        override_template(action,
                          "genshi:abl.jquery.core.templates.widget_container")
        c.widget = widget
        return {name: data}
