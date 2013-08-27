class DBDefaultDatabaseOperations(object):

    DB_TRANSFORM_DICT = {}

    def alter_set_db_defaults(self, field, name, params, sqls):
        template_params = {
            'column_name' : self.quote_name(name),
            'table_name' : self.quote_name(params['table_name'])
        }

        sql_params = []
        alter_sql_template = 'ALTER TABLE %(table_name)s ALTER COLUMN %(column_name)s'

        #Add defaults
        if not field.null and field.has_default():
            if field.is_default_escaped():
                sql_params.append(field.get_default())
                alter_sql_template = alter_sql_template + ' SET DEFAULT %%s'
            else:
                alter_sql_template = alter_sql_template + ' SET DEFAULT %s'%field.get_default()
        else:
            # If not default and no extra remove default
            alter_sql_template = alter_sql_template + ' DROP DEFAULT'

        sqls.append((alter_sql_template % template_params, sql_params))

    def get_db_transform(self, key):
        """
        Return DB specific transformation for a key
        """
        return self.DB_TRANSFORM_DICT.get(key)









