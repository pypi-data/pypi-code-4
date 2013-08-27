from db_defaults.db import generic
from south.db.mysql import DatabaseOperations

class DBDefaultDatabaseOperations(generic.DBDefaultDatabaseOperations):

    DB_TRANSFORM_DICT = {
        'current_date' : 'CURRENT_DATE',
        'current_timestamp' : 'CURRENT_TIMESTAMP',
    }

    def alter_set_db_defaults(self, field, name, params, sqls):
        """
        1. MySQL does not support defaults on text or blob columns.
        2. Add postgres specific extra here
        """
        type = self._db_type_for_alter_column(field)
        #  MySQL does not support defaults for geometry columns also
        is_geom = True in [type.find(t) > -1 for t in self.geom_types]
        is_text = True in [type.find(t) > -1 for t in self.text_types]
        if not is_geom and not is_text:
            super(DBDefaultDatabaseOperations, self).alter_set_db_defaults(field, name, params, sqls)

DatabaseOperations.__bases__ += (DBDefaultDatabaseOperations,)
