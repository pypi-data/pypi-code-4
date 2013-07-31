def cursor2cursorCopy(src, dest, table_name):
    """Copy record set from src cursor into table on dest cursor"""
    paramstyle = dest.connection.interface.paramstyle
    columns = src.columns()
    col_list = ', '.join(columns)

    if paramstyle == 'qmark':
        parm_list = ', '.join(['?' for c in columns])
    elif paramstyle == 'numeric':
        parm_list = ', '.join([':%d' % (i+1) for i in range(len(columns))])
    elif paramstyle == 'format':
        parm_list = ', '.join(['%s' for c in columns])
    elif paramstyle == 'named':
        parm_list = ', '.join([':%s' % c for c in columns])
    elif paramstyle == 'pyformat':
        parm_list = ', '.join(['%%(%s)s' % c for c in columns])

    query = 'INSERT INTO %s\n(%s)\nVALUES(%s)' % (table_name, col_list, parm_list)
    inserts = 0
    skips = 0
    for rec in src:
        try:
            dest.execute(query, rec)
            inserts += 1
        except dest.connection.interface.IntegrityError:
            # likely tried to insert existing record, just ignore
            skips += 1

    print 'Inserted %d records and skipped %d records' % (inserts, skips)