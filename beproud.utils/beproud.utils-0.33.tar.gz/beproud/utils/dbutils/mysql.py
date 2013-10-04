#:coding=utf-8:

TUPLE=0
DICT=1
DICT_WITH_TABLE=2

def MySQLConnection(connect_info):
    """ 単純にMySQLのコネクションを作って返します。 """
    import MySQLdb
    return MySQLdb.connect(**connect_info)

class MySQLCursor(object):
    """
    MySQLdb用のカーソルクラス。

    connection = MySQLConnection({
        'db' : "imagawa",
        'host' : "127.0.0.1",
        'port' : 3306,
        'user' : "user",
        'passwd' : "password"
    })
    cursor = MySQLCursor(connection)
    cursor.query('select id, name, email from huge_data')
    for i in cursor:
        # do something...
    """

    _next = None
    _index = 0
    def __init__(self, connection, rows=1, value_type=DICT):
        self.connection = connection
        self.rows = rows
        self.value_type = value_type
        self.rs = None
        self.row = None
    
    def query(self, sql):
        self.connection.query(sql)
        self.rs = self.connection.use_result()
        self._next = None
    
    def __iter__(self):
        return self

    def has_next(self):
        if self._next is None:
            if not self.row or self._index+1 > len(self.row):
                self.row = list(self.rs.fetch_row(self.rows, self.value_type) or [])
                self._index = 0
            self._next = bool(self.row)
        return self._next

    def next(self):
        if self.has_next():
            self._next = None
            return_val = self.row[self._index]
            self._index += 1
            self.has_next() # Check for next values
            return return_val
        else:
            raise StopIteration  
