import re
import json

from settings import settings

space_clean = re.compile(r'(^|>)(\s+)(<|$)')

class Page(object):

    node_template = 'var $e%(num)s = %(f)s(\'%(content)s\').hide();%(f)s(\'%(node)s\', \'%(context)s\').%(method)s($e%(num)s);$e%(num)s.show(\'%(effect)s\');'
    node_template_text = '%(f)s(\'%(node)s\').%(method)s(\'%(content)s\')'
    call_node_template = '%(f)s(\'%(node)s\').%(method)s()'
    node_select_script = '%(f)s(\'%(node)s\')'
    method_call_script = '.%(method)s(%(args)s)'
    page_hide_script = '%(f)s(\'.page\').hide().last().show();'
    page_prepend_script = '%(f)s(\'.page\').hide().first().show().nextUntil("").remove()'

    def __init__(self, function, context = 'html', args = {}, is_mobile = False, path='/', back='/'):
        self._f = function
        self.nodes = []
        self.context = context
        self.path = path
        self.back = back
        self.prepend_page = args.get('prepend', 'false') == 'true'

        mode = int(args.get('mode', 2000))
        if is_mobile:
            self.mode = False
        else:
            self.mode = mode>767

    def _make_text_node(self, node, method, content):
        return self.node_template_text % {
            'f': self._f,
            'node': node,
            'method': method,
            'content': re.escape(unicode(content)) #str(content).replace('\n','').replace('\r','')
        }

    def _make_call_node(self, node, method):
        return self.call_node_template % {
            'f': self._f,
            'node': node,
            'method': method
        }

    def _make_node(self, node, method, content, effect):

        #print content
        content = ' '.join(content.split())

        return self.node_template % {
            'num': len(self.nodes),
            'f': self._f,
            'node': self.mode and node or (self.prepend_page and '.page:first' or '.page:last'),
            'context': self.mode and self.context or 'body',
            'method': self.mode and method or (self.prepend_page and 'before' or 'after'),
            'content': re.escape(content) if self.mode else ('<div class="page" data-url="%s" data-back="%s">%s</div>' % (self.path, self.back, re.escape(content))), #str(content).replace('\n','').replace('\r',''),
            'effect': (effect and effect or '')
        }

    def hide(self, node):
        self.nodes.append(self._make_text_node(node, 'hide', ''))

    def show(self, node):
        self.nodes.append(self._make_call_node(node, 'show'))

    def title(self, t):
        self.nodes.append(self._make_text_node('title', 'html', t))

    def set(self, node, content, effect = None):
        self.nodes.append(self._make_node(node, 'html', content, effect))

    def html(self, node, content, effect = None):
        self.nodes.append(self._make_text_node(node, 'html', content))

    def text(self, node, content, effect = None):
        self.nodes.append(self._make_text_node(node, 'text', content))

    def append(self, node, content, effect = None):
        self.nodes.append(self._make_node(node, 'append', content, effect))

    def prepend(self, node, content, effect = None):
        self.nodes.append(self._make_node(node, 'prepend', content, effect))

    def after(self, node, content, effect = None):
        self.nodes.append(self._make_node(node, 'after', content, effect))

    def before(self, node, content, effect = None):
        self.nodes.append(self._make_node(node, 'before', content, effect))

    def empty(self, node):
        self.nodes.append(self._make_text_node(node, 'empty', ''))

    def remove(self, node):
        self.nodes.append(self._make_text_node(node, 'remove', ''))

    def alert(self, message = ''):
        self.nodes.append('alert("%s")' % message)

    def add_class(self, node, cls):
        self.nodes.append(self._make_text_node(node, 'addClass', '%s' % cls))

    def remove_class(self, node, cls):
        self.nodes.append(self._make_text_node(node, 'removeClass', '%s' % cls))

    def raw(self, line):
        self.nodes.append(line)

    def data(self, key, data):
        self.raw('window.dataProvider.set("%s", %s)' % (key, data))

    def chain(self, node, methods):
        links = [self.node_select_script % {'f': self._f, 'node':node}]

        for method, args in methods:
            links.append(self.method_call_script % {
                'method': method,
                'args': ', '.join([repr(x) for x in args])
            })

        self.nodes.append(''.join(links))

    def popup(self, data):
        self.raw('ramen.msgbox(%s)' % json.dumps(data, default=unicode))

    def script(self, href, once = False):
        self.nodes.append('%(f)s.getScript("%(assets)s%(href)s")' % {
            'assets': settings['domain']['assets'],
            'f': self._f,
            'href': href
        })

    def style(self, id, href):
        self.nodes.append('getStyle("%(id)s", "%(assets)s%(href)s")' % {
            'assets': settings['domain']['assets'],
            'id': id,
            'href': href
        })

    def render(self):
        if not self.mode:
            if self.prepend_page:
                self.nodes.append(self.page_prepend_script % {'f':self._f})
            else:
                self.nodes.append(self.page_hide_script % {'f':self._f})
        return ';\n'.join(self.nodes)

    def __str__(self):
        return self.render()

    def __unicode__(self):
        return self.render()
