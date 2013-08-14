from __future__ import unicode_literals

from django.db.backends import BaseDatabaseOperations


class DatabaseOperations(BaseDatabaseOperations):
    def __init__(self, connection):
        super(DatabaseOperations, self).__init__(connection)

    def quote_name(self, name):
        return name

    def date_extract_sql(self, lookup_type, field_name):
        if lookup_type == 'week_day':
            # For consistency across backends, we return Sunday=1, Saturday=7.
            return "EXTRACT('dow' FROM %s) + 1" % field_name
        else:
            return "EXTRACT('%s' FROM %s)" % (lookup_type, field_name)

    def date_interval_sql(self, sql, connector, timedelta):
        """
        implements the interval functionality for expressions
        format for NuoDB:
            (datefield + interval '3 days 200 seconds 5 microseconds')
        """
        modifiers = []
        if timedelta.days:
            modifiers.append('%s days' % timedelta.days)
        if timedelta.seconds:
            modifiers.append('%s seconds' % timedelta.seconds)
        if timedelta.microseconds:
            modifiers.append('%s microseconds' % timedelta.microseconds)
        mods = ' '.join(modifiers)
        conn = ' %s ' % connector
        return '(%s)' % conn.join([sql, 'interval \'%s\'' % mods])

    def date_trunc_sql(self, lookup_type, field_name):
        return "DATE_TRUNC('%s', %s)" % (lookup_type, field_name)

    def lookup_cast(self, lookup_type):
        lookup = '%s'

        # Cast text lookups to text to allow things like filter(x__contains=4)
        if lookup_type in ('iexact', 'contains', 'icontains', 'startswith',
                           'istartswith', 'endswith', 'iendswith'):
            lookup = "%s"

        # Use UPPER(x) for case-insensitive lookups; it's faster.
        if lookup_type in ('iexact', 'icontains', 'istartswith', 'iendswith'):
            lookup = 'UPPER(%s)' % lookup

        return lookup

    def field_cast_sql(self, db_type):
        if db_type == 'inet':
            return 'HOST(%s)'
        return '%s'

    def last_insert_id(self, cursor, table_name, pk_name):
        cursor.execute("SELECT %s FROM %s ORDER BY %s DESC" % (
            pk_name, table_name, pk_name))
        return cursor.fetchone()[0]

    def no_limit_value(self):
        return None

    def sql_flush(self, style, tables, sequences):
        if tables:
            # Perform a single SQL 'TRUNCATE x, y, z...;' statement.  It allows
            # us to truncate tables referenced by a foreign key in any other
            # table.
            sql = ['%s %s;' % \
                (style.SQL_KEYWORD('TRUNCATE TABLE '),
                    style.SQL_FIELD(t)) for t in tables]
            return sql
        else:
            return []

    def tablespace_sql(self, tablespace, inline=False):
        if inline:
            return "USING INDEX TABLESPACE %s" % tablespace
        else:
            return "TABLESPACE %s" % tablespace

    def savepoint_create_sql(self, sid):
        return "SAVEPOINT %s" % sid

    def savepoint_commit_sql(self, sid):
        return "RELEASE SAVEPOINT %s" % sid

    def savepoint_rollback_sql(self, sid):
        return "ROLLBACK TO SAVEPOINT %s" % sid

    def prep_for_iexact_query(self, x):
        return x

    def max_name_length(self):
        return 128

    def distinct_sql(self, fields):
        if fields:
            return 'DISTINCT ON (%s)' % ', '.join(fields)
        else:
            return 'DISTINCT'

    def last_executed_query(self, cursor, sql, params):
        if cursor.query is not None:
            return cursor.query.decode('utf-8')
        return None

    def bulk_insert_sql(self, fields, num_values):
        items_sql = "(%s)" % ", ".join(["%s"] * len(fields))
        return "VALUES " + ", ".join([items_sql] * num_values)
