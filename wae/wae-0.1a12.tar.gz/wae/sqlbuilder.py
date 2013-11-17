#coding: utf-8
import copy

class SqlBuilder(object):

    def __init__(self, template=None):
        if template==None:
            self._from = []
            self._where = []
            self._orderby = []
            self._groupby = []
            self._leftjoin = {}
            self._having = []
            self._empty = False
        else:
            self._from = copy.copy(template._from)
            self._where = copy.copy(template._where)
            self._orderby = copy.copy(template._orderby)
            self._groupby = copy.copy(template._groupby)
            self._leftjoin = copy.copy(template._leftjoin)
            self._having = copy.copy(template._having)
            self._empty = copy.copy(template._empty)


    def _is_empty(self): return self._empty
    is_empty = property(_is_empty)

    def set_empty(self):
        self._empty = True

    def add_from(self, table, alias=''):
        t = ("%s %s" % (table, alias)).strip()
        if t not in self._from:
            self._from.append(t)

    def left_join(self, master_alias, slave, alias, on):
        assert on!=""

        master_exists=False
        master_alias = master_alias.lower()

        # 在主表中查
        for t in self._from:
            if t.split()[1].lower().strip()==master_alias:
                master_exists=True
                break

        if not master_exists:
            # 在join表中查
            for j in self._leftjoin.values():
                for t in j:
                    if t['table'].split()[1].lower().strip()==master_alias:
                        master_exists=True
                        break

        assert master_exists==True
        if master_alias not in self._leftjoin:
            self._leftjoin[master_alias]= [{"table": "%s %s" % (slave, alias), "on":on}]
        else:
            self._leftjoin[master_alias].append({"table": "%s %s" % (slave, alias), "on":on})

    def where(self, w):
        w = w.strip()
        assert w!=""
        if w not in self._where:
            self._where.append(w)

    add_where = where

    def add_orderby(self, o):
        for x in o.split(","):
            x = " ".join(y.strip() for y in x.strip().split())
            if x not in self._orderby:
                self._orderby.append(x)

    def drop_orderby(self, o):
        for x in o.split(","):
            x = x.strip()
            x = " ".join(y.strip() for y in x.strip().split())
            if x in self._orderby:
                self._orderby.remove(x)

    def groupby(self, o):
        for x in o.split(","):
            x = x.strip().lower()
            if x not in self._groupby:
                self._groupby.append(x)

    add_groupby = groupby

    def where_clause(self):
        assert not self._empty
        return " and ".join(self._where)

    def having(self, c):
        if not c in self._having:
            self._having.append(c)

    def find_from(self, table, alias=""):
        table = table.lower()
        a = alias.lower()
        lst = []
        for t in self._from:
            r = t.split()
            if r[0].lower().strip()==table:
                lst.append((r[0].strip(), r[1].strip()))

        if len(lst)==0:
            return None

        if a!="":
            for _, al in lst:
                if al.lower()==a:
                    return alias
            return None
        else:
            return lst[0][1]

    def make_sql_base(self, sort=True):
        if not self._empty:
            fs = []
            for f in self._from:
                m=f.split()[1].strip().lower()
                if m in self._leftjoin:
                    for j in self._leftjoin[m]:
                        f += " left join %s on %s" % (j['table'], j['on'])
                fs.append(f)

            lst = ["from %s" % ",".join(fs)]
            if len(self._where)>0:
                lst.append("where %s" % self.where_clause())

            if len(self._groupby)>0:
                lst.append("group by %s" % ", ".join(self._groupby))

            if len(self._having)>0:
                lst.append("having %s" % " and ".join(self._having))

            if sort and len(self._orderby)>0:
                lst.append("order by %s" % ", ".join(self._orderby))

            return " ".join(lst)

        else:
            return None


    def select(self, fields, sort=True, pagesize=0, page=1):
        if not self._empty:
            lst = ["select %s %s" % (fields, self.make_sql_base(sort))]
            if pagesize>0:
                lst.append("limit %d" % pagesize)
                if page>1:
                    lst.append("offset %d" % ((page-1)*pagesize))

            return " ".join(lst)

        else:
            return None

    def distinct(self, fields, sort=True, pagesize=0, page=1):
        return self.select("distinct %s" % fields, sort, pagesize, page)


    def count(self, db):
        s = self.select("count(1)", False)
        if s==None:
            return 0
        else:
            c = db.fetchOne(s)
            if c==None: c=0
            return c


    def paginate(self, db, pagesize):
        c = self.count(db)
        pages = (c//pagesize)
        if c%pagesize>0: pages+=1

        return {"count":c, "pages":pages, "pagesize":pagesize}

