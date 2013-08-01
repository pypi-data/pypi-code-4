from django.template import Library


register = Library()


@register.inclusion_tag("profiles/search-result.html", takes_context=True)
def profile_result(context, profile):
    context.update({
        'profile': profile,
    })
    return context
