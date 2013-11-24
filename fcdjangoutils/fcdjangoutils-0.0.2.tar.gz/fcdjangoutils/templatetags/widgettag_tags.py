import fcdjangoutils.widgettagmiddleware
import django.template

register = django.template.Library()


@register.tag
def widget_addjsfile(parser, token):
    try:
        tag_name, filename = token.split_contents()
    except ValueError:
        raise django.template.TemplateSyntaxError, "%r tag requires one argument" % token.contents.split()[0]

    filename = django.template.Variable(filename)

    class Node(django.template.Node):
        def render(self, context):
            fcdjangoutils.widgettagmiddleware.WidgetTagMiddleware.addjsfile(filename.resolve(context))
            return ''

    return Node()

@register.tag
def widget_addieonlyjsfile(parser, token):
    try:
        tag_name, filename = token.split_contents()
    except ValueError:
        raise django.template.TemplateSyntaxError, "%r tag requires one argument" % token.contents.split()[0]

    filename = django.template.Variable(filename)

    class Node(django.template.Node):
        def render(self, context):
            fcdjangoutils.widgettagmiddleware.WidgetTagMiddleware.addieonlyjsfile(filename.resolve(context))
            return ''

    return Node()

@register.tag
def widget_addcssfile(parser, token):
    try:
        tag_name, filename = token.split_contents()
    except ValueError:
        raise django.template.TemplateSyntaxError, "%r tag requires one argument" % token.contents.split()[0]

    filename = django.template.Variable(filename)

    class Node(django.template.Node):
        def render(self, context):
            fcdjangoutils.widgettagmiddleware.WidgetTagMiddleware.addcssfile(filename.resolve(context))
            return ''

    return Node()

@register.tag
def widget_addjs(parser, token):
    """Usage: {% widget_addjs "somename" %}Some javascript{% widget_endjs %}"""

    try:
        tag_name, name = token.split_contents()
    except ValueError:
        raise django.template.TemplateSyntaxError, "%r tag requires one argument" % token.contents.split()[0]

    nodelist = parser.parse(('widget_endjs',))
    name = django.template.Variable(name)

    class Node(django.template.Node):
        def render(self, context):
            fcdjangoutils.widgettagmiddleware.WidgetTagMiddleware.addjs(name.resolve(context), nodelist.render(context))
            return ''
 
    parser.delete_first_token()
    return Node()

@register.tag
def widget_addcss(parser, token):
    """Usage: {% widget_addcss "somename" %}Some javascript{% widget_endcss %}"""

    try:
        tag_name, name = token.split_contents()
    except ValueError:
        raise django.template.TemplateSyntaxError, "%r tag requires one argument" % token.contents.split()[0]

    nodelist = parser.parse(('widget_endcss',))
    name = django.template.Variable(name)

    class Node(django.template.Node):
        def render(self, context):
            fcdjangoutils.widgettagmiddleware.WidgetTagMiddleware.addcss(name.resolve(context), nodelist.render(context))
            return ''
 
    parser.delete_first_token()
    return Node()

@register.tag
def widget_adddialog(parser, token):
    """Usage: {% widget_adddialog "somename" %}Some html{% widget_enddialog %}"""

    try:
        tag_name, name = token.split_contents()
    except ValueError:
        raise django.template.TemplateSyntaxError, "%r tag requires one argument" % token.contents.split()[0]

    nodelist = parser.parse(('widget_enddialog',))
    name = django.template.Variable(name)

    class Node(django.template.Node):
        def render(self, context):
            fcdjangoutils.widgettagmiddleware.WidgetTagMiddleware.adddialog(name.resolve(context), nodelist.render(context))
            return ''
 
    parser.delete_first_token()
    return Node()


@register.tag
def widget_uniquename(parser, token):
    """Usage: {% widget_uniquename varname "group" %}"""

    try:
        tag_name, varname, group = token.split_contents()
    except ValueError:
        raise django.template.TemplateSyntaxError, "%r tag requires one argument" % token.contents.split()[0]

    groupvar = django.template.Variable(group)

    class Node(django.template.Node):
        def render(self, context):
            request = context['request']
            group = groupvar.resolve(context)

            if not hasattr(request, 'widget_uniquename'):
                request.widget_uniquename = {}
            if group not in request.widget_uniquename:
                request.widget_uniquename[group] = 0

            context[varname] = request.widget_uniquename[group]
            request.widget_uniquename[group] += 1

            return ''

    return Node()
