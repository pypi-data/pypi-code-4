from db_defaults.db import generic
from south.db.postgresql_psycopg2 import DatabaseOperations

class DBDefaultDatabaseOperations(generic.DBDefaultDatabaseOperations):

    DB_TRANSFORM_DICT = {
        'current_date' : "now()",
        'current_timestamp' : "now()",
    }

    def alter_set_db_defaults(self, field, name, params, sqls):
        super(DBDefaultDatabaseOperations, self).alter_set_db_defaults(field, name, params, sqls)


DatabaseOperations.__bases__ += (DBDefaultDatabaseOperations,)