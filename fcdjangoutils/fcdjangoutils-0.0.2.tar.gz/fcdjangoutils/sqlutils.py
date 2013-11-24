import contextlib
import psycopg2

def query_columns(cur, query, args = {}):
    cur.execute("""
      select
        *
      from
        """ + query + """ as a
      limit 1
    """, args)

    return dict((name, ts[0])
                for (name, ts) in ((column.name, 
                                    [name
                                     for name, t in ((name, getattr(psycopg2, name))
                                                     for name in ("Date",
                                                                  "Time",
                                                                  "Timestamp",
                                                                  "DateFromTicks",
                                                                  "TimeFromTicks",
                                                                  "TimestampFromTicks",
                                                                  "Binary",
                                                                  "STRING",
                                                                  "BINARY",
                                                                  "NUMBER",
                                                                  "DATETIME",
                                                                  "ROWID"))
                                     if column.type_code == t])
                                   for column in cur.description)
                if ts)

def dictreader(cur):
    cols = None
    for row in cur:
        if cols is None:
            cols = [dsc[0] for dsc in cur.description]
        yield dict(zip(cols, row))
