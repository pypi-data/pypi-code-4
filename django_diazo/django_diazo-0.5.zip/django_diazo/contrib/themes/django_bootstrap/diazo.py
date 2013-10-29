"""
Register the theme.
"""
from django_diazo.theme import DiazoTheme, registry


class Theme(DiazoTheme):
    name = 'Django Admin - Bootstrap 3.0.0'
    slug = 'django_bootstrap'


registry.register(Theme)
