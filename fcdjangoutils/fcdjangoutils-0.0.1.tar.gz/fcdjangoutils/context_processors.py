from django.conf import settings

def site(request):
    return {
        'site_url': request.build_absolute_uri('/')[:-1],
        'settings': settings
    }
