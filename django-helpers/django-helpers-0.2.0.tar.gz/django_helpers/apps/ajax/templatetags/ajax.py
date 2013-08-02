from django.template import TemplateSyntaxError, Library
from django.template.loader import render_to_string
from django.template.loader_tags import BlockNode
from django_helpers.apps.static_manager import jQueryURL
from django_helpers.helpers.templatetags import parse_args, resolve_args
from django_helpers.utils.html import generate_code

register = Library()


class AJAXBlockRegister(list):
    has_js = True
    is_bare_js = True

    def __init__(self):
        list.__init__(self)
        self.js_files = [jQueryURL, 'js/jquery.django.ajax.js']

    def render_js(self):
        return render_to_string('ajax-block/blocks.js', {
            'blocks': self
        })

    def __unicode__(self):
        return 'AJAX Block Register'


def get_block_id(name):
    return 'ajax-block-' + name


class AJAXBlockNode(BlockNode):
    def __init__(self, name, nodelist, parent=None, args=None, kwargs=None):
        BlockNode.__init__(self, name, nodelist, parent)
        self.kwargs = kwargs
        self.args = args

    def get_id(self):
        return get_block_id(self.name)

    def resolver_tag(self, context):
        args = self.args
        kwargs = self.kwargs

        if len(args) > 0:
            tag = args[0]
            if 'tag' in kwargs:
                raise TemplateSyntaxError('Tag occures twice.')
        elif 'tag' in kwargs:
            tag = kwargs.pop('tag')
        else:
            raise TemplateSyntaxError('Tag is not specified.')

        if 'id' in kwargs:
            raise TemplateSyntaxError('ID should not be passed as an argument. It will be automatically generated from block name.')

        self.tag = tag.resolve(context, True)

    def register_block_js(self, context):
        key = 'ajax_block_register'
        registry = context.get(key)
        if registry is None:
            registry = AJAXBlockRegister()
            context = context.dicts[-2]
            context[key] = registry
        elif not isinstance(registry, AJAXBlockRegister):
            raise
        registry.append((self.name, self.get_id()))

    def start_tag(self, context):
        self.resolver_tag(context)
        kwargs = resolve_args(None, self.kwargs, context)
        kwargs['id'] = self.get_id()
        return generate_code(self.tag, kwargs, start_only=True)

    def render(self, context):
        is_ajax = context.get('is_ajax_render', False)
        op = BlockNode.render(self, context)
        if not is_ajax:
            self.register_block_js(context)
            op = self.start_tag(context) + op
            op += '</%s>' % self.tag
        return op


@register.tag('ajax_block')
def _ajax_block(parser, token):
    """
    Code Borrowed from Django Code Base.
    Define a block that can be overridden by child templates.
    """

    bits = token.contents.split()
    block_name = bits[1]
    args, kwargs = parse_args(bits[1:], parser)

    if len(args) > 1:
        raise TemplateSyntaxError('%s does not take more than two arguments.')

    try:
        if block_name in parser.__loaded_blocks:
            raise TemplateSyntaxError("'%s' tag with name '%s' appears more than once" % (bits[0], block_name))
        parser.__loaded_blocks.append(block_name)
    except AttributeError:  # parser.__loaded_blocks isn't a list yet
        parser.__loaded_blocks = [block_name]
    nodelist = parser.parse(('endajax_block',))

    # This check is kept for backwards-compatibility. See #3100.
    endblock = parser.next_token()
    acceptable_endblocks = ('endajax_block', 'endajax_block %s' % block_name)
    if endblock.contents not in acceptable_endblocks:
        parser.invalid_block_tag(endblock, 'endajax_block', acceptable_endblocks)

    return AJAXBlockNode(block_name, nodelist, None, args, kwargs)