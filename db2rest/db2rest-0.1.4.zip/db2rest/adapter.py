import sqlalchemy as sql


class DBAdapter(object):

    def __init__(self, db_engine):
        self.meta = sql.schema.MetaData()
        self.db_engine = db_engine
        self.meta.reflect(bind=db_engine)

    def tables(self):
        return reversed(self.meta.sorted_tables)
