from django.conf import settings
from django.template.base import Library

tracking_code = '<script type="text/javascript">' +\
                'var _gaq = _gaq || [];' +\
                '_gaq.push(["_setAccount", "%s"]);' % settings.ANALYTICS_CODE +\
                '_gaq.push(["_trackPageview"]);' +\
                '(function() {'+\
                'var ga = document.createElement("script"); ga.type = "text/javascript"; ga.async = true;' +\
                'ga.src = ("https:" == document.location.protocol ? "https://ssl" : "http://www") + ".google-analytics.com/ga.js";' +\
                'var s = document.getElementsByTagName("script")[0]; s.parentNode.insertBefore(ga, s);' +\
                '})();' +\
                '</script>'

register = Library()

@register.simple_tag(takes_context=True)
def analytics(context):
    user = context['user']
    if settings.ANALYTICS:
        if user.is_anonymous():
            return tracking_code
        elif settings.ANALYTICS_TRACK_ADMINS:
            return tracking_code

    return ''
