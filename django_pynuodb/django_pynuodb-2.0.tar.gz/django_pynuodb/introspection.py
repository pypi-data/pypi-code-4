from __future__ import unicode_literals

from django.db.backends import BaseDatabaseIntrospection


class DatabaseIntrospection(BaseDatabaseIntrospection):
     
    # Maps type codes to Django Field types.
    data_types_reverse = {
        16: 'BooleanField',
        20: 'BigIntegerField',
        21: 'SmallIntegerField',
        23: 'IntegerField',
        25: 'TextField',
        700: 'FloatField',
        701: 'FloatField',
        869: 'GenericIPAddressField',
        1042: 'CharField', # blank-padded
        1043: 'CharField',
        1082: 'DateField',
        1083: 'TimeField',
        1114: 'DateTimeField',
        1184: 'DateTimeField',
        1266: 'TimeField',
        1700: 'DecimalField',
    }
        
    def get_table_list(self, cursor):
        "Returns a list of table names in the current database."
        if self.connection.settings_dict.has_key('SCHEMA'):
            cursor.execute(str("SELECT tablename FROM system.tables WHERE schema='%s'" % self.connection.settings_dict['SCHEMA']))
        else:
            cursor.execute(str("SELECT tablename FROM system.tables WHERE schema='USER'"))
        results = [row[0] for row in cursor.fetchall()]
        return results

    def get_table_description(self, cursor, table_name):
        "Returns a description of the table, with the DB-API cursor.description interface."
        print 'get_table_description'
        cursor.execute("""
            SELECT column_name, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s""", [table_name])
        null_map = dict(cursor.fetchall())
        cursor.execute("SELECT * FROM %s LIMIT 1" % table_name)
        return [line[:6] + (null_map[line[0]]=='YES',)
                for line in cursor.description]

    def table_name_converter(self, name):
        """Apply a conversion to the name for the purposes of comparison.

        The default table name converter is for case sensitive comparison.
        """
        return str(name).upper()
