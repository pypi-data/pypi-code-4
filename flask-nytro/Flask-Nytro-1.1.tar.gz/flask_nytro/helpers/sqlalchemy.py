#Module for sqlalchemy helpers

def m2m(db, table1, table2):
    '''Creates the intermediate table for many-to-many relationships in SQLAlchemy'''
    table1, table2 = table1.lower(), table2.lower()
    return db.Table('%s_%s' % (table1, table2),
        db.Column('%s_id' % table1, db.Integer, db.ForeignKey('%s.id' % table1)),
        db.Column('%s_id' % table2, db.Integer, db.ForeignKey('%s.id' % table2)),
    )