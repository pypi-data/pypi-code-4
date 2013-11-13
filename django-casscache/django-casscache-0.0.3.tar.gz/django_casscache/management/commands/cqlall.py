from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


CQL = """
CREATE KEYSPACE {keyspace} WITH replication = {{
  'class': 'SimpleStrategy',
  'replication_factor': '2'
}};

USE {keyspace};

CREATE TABLE {columnfamily} (
  key text PRIMARY KEY,
  flags int,
  value blob
) WITH
  caching='ALL' AND
  compaction={{'sstable_size_in_mb': '160', 'class': 'LeveledCompactionStrategy'}} AND
  compression={{'sstable_compression': 'SnappyCompressor'}};
"""


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--backend',
                    dest='backend',
                    default='default',
                    help='Cache backend by name'),
    )

    def handle(self, *args, **options):
        conf = settings.CACHES[options['backend']]
        if 'casscache' not in conf['BACKEND']:
            raise CommandError('"%s" is not a valid casscache backend' % options['backend'])
        options = conf.pop('OPTIONS')
        keyspace = options.pop('keyspace')
        columnfamily = options.pop('columnfamily')

        self.stdout.write(CQL.format(keyspace=keyspace, columnfamily=columnfamily))
