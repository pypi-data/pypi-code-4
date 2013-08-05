import abc

class Database(metaclass=abc.ABCMeta):
    
    @abc.abstractmethod
    def __init__(self, connection):
        self.connection = connection
        
    def process(self, statement, values):
        cursor = self.connection.execute(statement, values)
        
        self.connection.commit()
        
        return cursor
    
    def assert_list(self, list_to_be_assserted, name):
        count = len(list_to_be_assserted)
        
        assert isinstance(list_to_be_assserted, list) and count > 0, '{0} need to be a list and {0} count needs to be bigger than 0'.format(name.title())
        
        return count
        
    def select(self, table, columns="*", where="1", where_values=[]):
        assert where.count('?') == len(where_values), 'Where injection count needs to be the same as where values count'
        
        if not isinstance(columns, list):
            columns = ["*"]
            
        inject = dict(table=table, columns=','.join(columns), where=where)
        
        statement = 'SELECT {columns} FROM {table} WHERE {where}'.format(**inject)
            
        cursor = self.process(statement, where_values)
        
        return cursor.fetchall()
    
    def insert(self, table, columns, values):
        column_count = self.assert_list(columns, 'columns')
        value_count = self.assert_list(values, 'values')
        
        assert column_count == value_count, 'Columns count and Values count needs to be the same'
        
        inject = dict(table=table, columns=','.join(columns), values=','.join([i for i in '?' * len(values)]))
        
        statement = 'INSERT INTO {table} ({columns}) VALUES({values})'.format(**inject)
        
        self.process(statement, values)
        
    def update(self, table, columns, values, where="1", where_values=[]):
        column_count = self.assert_list(columns, 'columns')
        value_count = self.assert_list(values, 'values')
        
        assert column_count == value_count, 'Columns count and Values count needs to be the same'
        
        assert where.count('?') == len(where_values), 'Where injection count needs to be the same as where values count'
        
        inject = dict(table=table, columns='=?,'.join(columns) + '=?')
        
        inject['where'] = where
        
        statement = 'UPDATE {table} SET {columns} WHERE {where}'.format(**inject)
        
        if len(where_values) > 0:
            values.extend(where_values)
        
        self.process(statement, values)
    
    def delete(self, table, where="1", where_values=[]):
        assert where.count('?') == len(where_values), 'Where injection count needs to be the same as where values count'
        
        inject = dict(table=table, where=where)
        
        statement = 'DELETE FROM {table} WHERE {where}'.format(**inject)
        
        cursor = self.process(statement, where_values)
        
        return cursor.rowcount
        