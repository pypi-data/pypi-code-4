from django_diazo.models import Theme


def get_active_theme(request):
    for theme in Theme.objects.filter(enabled=True).order_by('sort'):
        if theme.available(request):
            return theme
    return None
