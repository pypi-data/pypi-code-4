from django.core.management.base import BaseCommand, CommandError

from south.models import MigrationHistory
from south.db import db


class Command(BaseCommand):
    def handle(self, *args, **options):
        db.delete_table('cmsplugin_frequentlyentrycategoryplugin')
        db.rename_table('cmsplugin_entrycategoryplugin', 'cmsplugin_frequentlyentrycategoryplugin')
        db.delete_table('cmsplugin_frequently_frequentlyentrycategoryplugin_categories')
        db.rename_table('frequently_entrycategoryplugin_categories', 'cmsplugin_frequently_frequentlyentrycategoryplugin_categories')
        db.rename_column('cmsplugin_frequently_frequentlyentrycategoryplugin_categories', 'entrycategoryplugin_id', 'frequentlyentrycategoryplugin_id')
        MigrationHistory.objects.filter(app_name='frequently').delete()
