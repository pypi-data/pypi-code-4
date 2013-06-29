from django.core.management.base import BaseCommand

from player.crawler import get_backend
from player.data.models import Collection


class Command(BaseCommand):

    option_list = BaseCommand.option_list + ()
    help = "Launch crawling in a all collections"
    requires_model_validation = False
    can_import_settings = True

    def handle(self, *args, **options):
        for collection in Collection.objects.all():
            crawler_collection = collection.crawler_collection
            print '   Analyzing "%s" collection...' % collection
            backend = get_backend(crawler_collection.backend)
            if backend.has_new_data(crawler_collection):
                print '\tCrawling "%s" collection...' % collection
                backend.extract_collection_data(crawler_collection)
                print '\tData extracted'
            else:
                print '\tCollection "%s" was up to date' % collection
