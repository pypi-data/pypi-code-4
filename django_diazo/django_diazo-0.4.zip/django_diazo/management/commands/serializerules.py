from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from django_diazo.models import Theme


class WrongFormatException(Exception):
    pass


class Command(BaseCommand):
    help = _('Serialize the rules of a specific theme to XML.')
    requires_model_validation = True

    def handle(self, theme_id, filename, fmt='xml', **options):
        if not fmt in ['xml']:
            raise WrongFormatException("Serializing to format '{0}' not supported.".format(fmt))

        theme = Theme.objects.get(pk=theme_id)
        fp = open(filename, 'w')
        try:
            fp.write(theme.rules.serialize())
        finally:
            fp.close()
