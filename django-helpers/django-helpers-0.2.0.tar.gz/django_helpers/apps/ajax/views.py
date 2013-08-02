from django.shortcuts import render
from django.template import loader, Context, Template, RequestContext
from django.utils import six
from django.template.base import TextNode
from django.template.loader_tags import BlockNode, ExtendsNode, BLOCK_CONTEXT_KEY, BlockContext
from django_helpers import get_settings_val
from django_helpers.apps.static_manager import jQueryURL
from django_helpers.apps.static_manager.utils import generate_js_from_context

from django_helpers.helpers.views import render_json
from . import get_block_id


__author__ = 'ajumell'

title_key = 'title'


def find_extends_node(nodelist):
    for node in nodelist:
        if not isinstance(node, TextNode):
            if isinstance(node, ExtendsNode):
                return node
                # ExtendsNode has to be the first node!
            return


def resolve_template(template):
    if isinstance(template, Template):
        return template

    elif isinstance(template, (list, tuple)):
        return loader.select_template(template)

    elif isinstance(template, six.string_types):
        return loader.get_template(template)

    else:
        return Template(template)


def resolve_context(context, request=None):
    if isinstance(context, Context):
        return context
    if isinstance(context, dict) or context is None:
        if request is not None:
            return RequestContext(request, context)
        else:
            return Context(context)
    else:
        raise


# noinspection PyUnresolvedReferences
def is_partial_request(request):
    """

    @param request: django.http.HttpRequest
    @return: bool
    """
    is_ajax = request.META.get('HTTP_X_DJANGO_AJAX_RENDERER', None) == 'true'
    blocks = request.GET.getlist('__blocks__[]', [])
    return blocks if is_ajax else None


def get_app_name(request):
    app_name = request.GET.get('__app_name__', "")
    return None if app_name == '' else app_name


def ajax_render(request, template, context=None):
    blocks = is_partial_request(request)
    app_name = get_app_name(request)
    if blocks is None:
        return render(request, template, context)

    template = resolve_template(template)
    context = resolve_context(context, request)
    title = ''
    if title_key in context:
        title = context[title_key]

    blocks = render_blocks(template, context, blocks)

    if title_key in blocks:
        title = blocks[title_key]

    op = generate_js_from_context(context, app_name)
    static_url = get_settings_val('STATIC_URL')
    for block in op:
        files = block['files']
        url = static_url + jQueryURL
        while url in files:
            files.remove(url)

    return render_json({
        'blocks': blocks,
        'url': request.get_full_path(),
        'js': op,
        'title': title
    })


def render_blocks(template, context, ajax_blocks):
    """
    @param template: A Template object
    @param context: A Context or RequestContext object
    @param ajax_blocks: A list of blocks
    @return: dict of blocks and its data.

    Render the requested blocks into a dictionary.
    """
    templates = [template]

    # Find all templates in the inheritance chain.
    while template:
        extends_node = find_extends_node(template.nodelist)
        if extends_node:
            template = extends_node.get_parent(context)
            templates.append(template)
        else:
            break

    # Ensure we have the proper BlockContext.
    if not BLOCK_CONTEXT_KEY in context.render_context:
        context.render_context[BLOCK_CONTEXT_KEY] = BlockContext()
    block_context = context.render_context[BLOCK_CONTEXT_KEY]

    # Collect all the BlockNodes and fill the structure.
    for template in templates:
        extends_node = find_extends_node(template.nodelist)
        if extends_node:
            block_context.add_blocks(extends_node.blocks)
        else:  # Root template
            blocks = dict([(n.name, n) for n in template.nodelist.get_nodes_by_type(BlockNode)])
            block_context.add_blocks(blocks)
    res = {}
    for name in ajax_blocks:
        block = block_context.get_block(name)
        res[get_block_id(name)] = block.render(context)

    if title_key not in ajax_blocks:
        block = block_context.get_block(title_key)
        if block is not None:
            res[title_key] = block.render(context)
    return res