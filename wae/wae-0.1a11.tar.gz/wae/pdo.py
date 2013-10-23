#coding: utf-8
import psycopg2, types
import psycopg2.extensions

class _Recordset(object):
    def __init__(self, cursor):
        assert not cursor.closed
        self._cur = cursor
        self._colnames = tuple(c[0] for c in cursor.description)

    def __del__(self):
        self._cur.close()

    def _get_rowcount(self):
        return self._cur.rowcount
    rowcount = property(_get_rowcount)


    def fetchOne(self):
        t = self._cur.fetchone()
        if t != None:
            return t[0]
        else:
            return None

    def fetchRow(self):
        t = self._cur.fetchone()
        if t != None:
            return dict((self._colnames[i], v) for i, v in enumerate(t))
        return None

    def fetchAll(self):
        lst = []
        for t in self._cur:
            d = dict((self._colnames[i], v) for i, v in enumerate(t))
            lst.append(d)
        return tuple(lst)

    def fetchPairs(self):
        assert len(self._colnames)>1
        return dict((x[0], x[1]) for x in self._cur)


class Connection(object):
    def __init__(self, dbconn):
        self._dbconn = dbconn

    def query(self, sql, *args):
        cur = self._dbconn.cursor()
        if len(args)>0:
            if type(args[0]) is types.DictType:
                cur.execute(sql, *args)
            else:
                cur.execute(sql, args)
        else:
            cur.execute(sql)
        return _Recordset(cur)

    def execute(self, sql, *args):
        cur = self._dbconn.cursor()
        if len(args)>0:
            if type(args[0]) is types.DictType:
                cur.execute(sql, *args)
            else:
                cur.execute(sql, args)
        else:
            cur.execute(sql)
        n = cur.rowcount
        cur.close()
        return n

    def insert(self, table, data):
        lns = ["insert into %s (%s) values" % (table.lower(), ','.join(data))]
        lns.append(" (%s)" % ','.join("%%(%s)s" % k for k in data))
        s = ''.join(lns)
        return self.execute(s, data)

    def update(self, table, data, where):
        lns = ["update %s set" % table.lower()]
        lns.append(",".join("%s=%%(%s)s" % (k,k) for k in data))
        lns.append("where %s" % where)
        s = ' '.join(lns)
        return self.execute(s, data)

    def commit(self):
        self._dbconn.commit()

    def rollback(self):
        self._dbconn.rollback()

    def close(self):
        if self._dbconn.status == psycopg2.extensions.STATUS_IN_TRANSACTION:
            self._dbconn.rollback()

        self._dbconn.close()
        del self._dbconn
        assert not hasattr(self, "_dbconn")


    def fetchOne(self, sql, *args):
        return self.query(sql, *args).fetchOne()

    def fetchRow(self, sql, *args):
        return self.query(sql, *args).fetchRow()

    def fetchAll(self, sql, *args):
        return self.query(sql, *args).fetchAll()

    def fetchPairs(self, sql, *args):
        return self.query(sql, *args).fetchPairs()


    def seqValue(self, seqname):
        return self.query("select last_value from %s" % seqname).fetchOne()

    def lastInsertId(self, table, field):
        return self.seqValue("%s_%s_seq" % (table.lower(), field.lower()))


    def __del__(self):
        if hasattr(self, "_dbconn"):
            self.close()


def connect(host="localhost", port=5432, user="", password="", dbname=""):
    """connect to database and returns session"""
    return Connection(psycopg2.connect(host=host, port=port, user=user, password=password, database=dbname))

