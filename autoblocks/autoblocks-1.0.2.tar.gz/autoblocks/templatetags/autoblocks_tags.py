from django import template
from django.contrib.sites.models import Site
from django.utils.safestring import mark_safe

from autoblocks.models import Autoblock
from .helpers import parse_token_data

register = template.Library()


class AutoblockNode(template.Node):
    def __init__(self, composite_id_parts, site, context_variable=None):
        self.composite_id_parts = [template.Variable(id_part) for id_part in composite_id_parts]
        if not site:
            self.site = Site.objects.get_current()
        else:
            self.site = template.Variable(site)
        self.context_variable = context_variable

    def render(self, context):
        composite_id_parts = []
        for index, id_variable in enumerate(self.composite_id_parts):
            try:
                composite_id_parts.append(id_variable.resolve(context))
            except template.VariableDoesNotExist:
                composite_id_parts.append(id_variable.var)
        composite_id = '-'.join(composite_id_parts)

        if isinstance(self.site, template.Variable):
            site = self.site.resolve(context)
        else:
            site = self.site

        autoblock = None
        if 'request' in context:
            user = context['request'].user
            if user.has_perm('autoblocks.add_autoblock'):
                autoblock = Autoblock.objects.get_or_create(
                    composite_id=composite_id,
                    site=site)[0]

        if not autoblock:
            try:
                autoblock = Autoblock.objects.get(composite_id=composite_id, site=site)
            except Autoblock.DoesNotExist:
                pass
        if autoblock:
            if self.context_variable:
                context[self.context_variable] = mark_safe(autoblock.content.render(context, None))
                return ''
            else:
                return autoblock.content.render(context, None)


def do_autoblock(parser, token):
    token_data = token.split_contents()[1:]
    (id_parts, site, context_variable) = parse_token_data(token_data)
    return AutoblockNode(id_parts, site, context_variable)


register.tag('autoblock', do_autoblock)
