
from django import template
from django.template import TemplateSyntaxError, Node
import gushuley.multihost
import re
from django.utils.encoding import smart_str
from gushuley.multihost import models
import django.contrib.sites.models
from gushuley.multihost.mh_utils import get_current_site, mh_reverse


class MHReverseNode(Node):
    def __init__(self, view_name, site, args, kwargs, asvar, site_ins):
        self.view_name = view_name
        self.args = args
        self.site = site
        self.asvar = asvar
        self.kwargs = kwargs
        self.site_ins = site_ins

    def render(self, context):
        args = [arg.resolve(context) for arg in self.args]
        site = self.site_ins or self.site.resolve(context)
        kwargs = dict([(smart_str(k,'ascii'), v.resolve(context))
            for k, v in self.kwargs.items()])
        is_external = False
        for k, v in kwargs.items():
            if k == "is_external":
                is_external = v
                del kwargs[k]
                break
          
        url = mh_reverse(self.view_name, site, is_external, args, kwargs)

        if self.asvar:
            context[self.asvar] = url
            return ''
        else:
            return url        


kwarg_re = re.compile(r"(?:(\w+)=)?(.+)")
def mh_reverse_tag(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least two argument"
                                  " (path to a view) (site)" % bits[0])
    viewname = bits[1]
    site = bits[2]
    if site.startswith('site='):
        site_inst = models.Site.objects.get(site__exact = django.contrib.sites.models.Site.objects.get(name = site[5:]))
        site = None
    else:
        site_inst = None
        site = parser.compile_filter(site)
    args = []
    kwargs = {}
    asvar = None
    bits = bits[3:]
    if len(bits) >= 3 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]

    # Backwards compatibility: check for the old comma separated format
    # {% url urlname arg1,arg2 %}
    # Initial check - that the first space separated bit has a comma in it
    if bits and ',' in bits[0]:
        check_old_format = True
        # In order to *really* be old format, there must be a comma
        # in *every* space separated bit, except the last.
        for bit in bits[1:-1]:
            if ',' not in bit:
                # No comma in this bit. Either the comma we found
                # in bit 1 was a false positive (e.g., comma in a string),
                # or there is a syntax problem with missing commas
                check_old_format = False
                break
    else:
        # No comma found - must be new format.
        check_old_format = False

    if check_old_format:
        # Confirm that this is old format by trying to parse the first
        # argument. An exception will be raised if the comma is
        # unexpected (i.e. outside of a static string).
        match = kwarg_re.match(bits[0])
        if match:
            value = match.groups()[1]
            try:
                parser.compile_filter(value)
            except TemplateSyntaxError:
                bits = ''.join(bits).split(',')

    # Now all the bits are parsed into new format,
    # process them as template vars
    if len(bits):
        for bit in bits:
            match = kwarg_re.match(bit)
            if not match:
                raise TemplateSyntaxError("Malformed arguments to url tag")
            name, value = match.groups()
            if name:
                kwargs[name] = parser.compile_filter(value)
            else:
                args.append(parser.compile_filter(value))

    return MHReverseNode(viewname, site, args, kwargs, asvar, site_inst)

register = template.Library()
register.tag(compile_function=mh_reverse_tag, name='mh_reverse')
