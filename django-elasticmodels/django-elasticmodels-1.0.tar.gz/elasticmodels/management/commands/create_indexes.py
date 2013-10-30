from django.core.management.base import NoArgsCommand

from elasticmodels import settings
from elasticmodels.index import Indexer


class Command(NoArgsCommand):
    help = 'Updates the ElasticSearch indexes'

    def handle_noargs(self, **options):
        indexer = Indexer()
        for model in settings.ELASTICSEARCH_TO_INDEX:
            indexer.generate_index(model)

        indexer.create_indexes()
