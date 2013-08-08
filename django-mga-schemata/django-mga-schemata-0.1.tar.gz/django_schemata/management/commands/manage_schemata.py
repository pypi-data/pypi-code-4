from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.db import connections, router, transaction, models, DEFAULT_DB_ALIAS


from django_schemata.postgresql_backend.base import _check_identifier

class Command(BaseCommand):
    help = "Manages the postgresql schemata."

    option_list = BaseCommand.option_list + (
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Nominates a database. '
                'Defaults to the "default" database.'),
    )

    def handle(self, *unused_args, **options):
        """
        Go through settings.SCHEMATA_DOMAINS and create all schemata that
        do not already exist in the database. 
        """
        db = options.get('database')
        connection = connections[db]

        if not hasattr(connection, 'schema_name'):
            raise RuntimeError("You can't use this database with 'manage_schemata' command")

        # operate in the default schema
        connection.set_schemata_off()
        cursor = connection.cursor()
        cursor.execute('SELECT schema_name FROM information_schema.schemata')
        existing_schemata = [ row[0] for row in cursor.fetchall() ]

        for sd in settings.SCHEMATA_DOMAINS.values():
            schema_name = str(sd['schema_name'])
            _check_identifier(schema_name)

            if schema_name not in existing_schemata:
                sql = 'CREATE SCHEMA %s' % schema_name
                print sql
                cursor.execute(sql)
                transaction.commit_unless_managed()
