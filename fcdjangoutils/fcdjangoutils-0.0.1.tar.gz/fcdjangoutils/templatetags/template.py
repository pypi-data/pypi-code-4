import django.template
import django.template.defaultfilters

register = django.template.Library()

@register.filter
@django.template.defaultfilters.stringfilter
def template_exists(value):
    try:
        django.template.loader.get_template(value)
    except django.template.TemplateDoesNotExist:
        return False
    else:
        return True
