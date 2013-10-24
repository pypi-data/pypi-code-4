#Fusion Table Insert/Update Utility

import psycopg2
from psycopg2.extras import RealDictCursor as DictCursor
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

import time
import logging


class PostgresFTSync:
    ft_id_field = 'ft_id'
    seq_field = 'seq'
    ft_client = None
    db = None

    def __init__(self,
                 ft_client,
                 postgres_db,
                 ft_id_field='ft_id',
                 seq_field='seq'):

        self.ft_client = ft_client
        self.db = postgres_db
        self.ft_id_field = ft_id_field
        self.seq_field = seq_field


    def sync_postgres_to_ft (self,
                             postgres_table_name,
                             ft_table_id,
                             batch_size=100, id_log_file=None):
        params = {
            'postgres_table_name': postgres_table_name,
            'ft_table_id': ft_table_id,
            'batch_size': batch_size,
            'ft_id_field': self.ft_id_field,
            'seq_field': self.seq_field
        }
        logging.debug ("Syncing from postgres table %(postgres_table_name)s "
                       "to FT table %(ft_table_id)s" % params )
        logging.debug ("Using batch size %s" %(batch_size) )


        logging.debug ("Retrieving postgres records..." )
        sql = ('select * from "%(postgres_table_name)s" '
               'where "%(ft_id_field)s" is null '
               'order by %(seq_field)s asc '
               'limit %(batch_size)s' % params)

        cur = self.db.cursor(cursor_factory=DictCursor)
        cur.execute (sql)
        n = cur.rowcount
        if not n:
            logging.info ("All records synced. Nothing to do.")
            return 0

        # get postgres records not synced
        logging.info ("Syncing %s records..." % n)
        rows = cur.fetchall()

        if self.seq_field != 'seqid':
            # translate sequence id field name
            for row in rows:
                row['seqid'] = row[self.seq_field]
                del row[self.seq_field]

        logging.debug ("Updating Fusion table records..." )
        # insert any rows that are not already present in ft
        # (match on seq_field)
        # do not update records that already exist
        rows = self.ft_client.insertOrReplaceRows(ft_table_id,
                                                  rows,
                                                  'seqid',
                                                  insert_only=True)

        # update postgres with new ft rowids
        time.sleep(1.0)  # allow FT request to complete (desparate measure)
        logging.debug ("Updating FT IDs in postgres ..." )
        for row in rows:
            params['ft_id_value'] = row['rowid']
            params['seq_value'] = row['seqid']
            sql = ('update "%(postgres_table_name)s" '
                   "set %(ft_id_field)s = %(ft_id_value)s "
                   "where %(seq_field)s = '%(seq_value)s'" % params)
            cur.execute (sql)
	    if id_log_file:
		id_log_file.write ("%s, %s\n" % (params['ft_id_value'], params['seq_value']))

        logging.info ("Synced %s records from postgres to FT" % len(rows) )

        return len(rows)

    def sync_ft_to_postgres (self,
                             postgres_table_name,
                             ft_table_id,
                             batch_size=100):
        params = {
            'postgres_table_name': postgres_table_name,
            'ft_table_id': ft_table_id,
            'batch_size': batch_size,
            'ft_id_field': self.ft_id_field,
            'seq_field': self.seq_field,
            'sql_where': ''
        }
        logging.debug ("Syncing from FT table %(ft_table_id)s "
                       "to postgres table %(postgres_table_name)s" % params )
        logging.debug ("Using batch size %s" %(batch_size) )

        logging.debug ("Retrieving Fustion Table records..." )

        # get largest sequence number present in postgres
        cur = self.db.cursor(cursor_factory=DictCursor)
        sql = ('select "%(seq_field)s" from "%(postgres_table_name)s" '
               'order by %(seq_field)s desc limit 1' % params)
        cur.execute (sql)
        logging.debug ("DB query: %s" % sql)
        n = cur.rowcount

        if not n:
            logging.debug ("Postgres table empty, syncing everything")
        else:
            row = cur.fetchone()
            seqid = row[params['seq_field']]

            logging.debug ("Largest seqid found in PostgreSQL table %s: %s"
                           % (postgres_table_name, seqid) )
            params['sql_where'] = ("WHERE seqid > %s"
                                   % psycopg2.extensions.adapt(str(seqid)))

        # get columns present in FT
        ft_cols = self.ft_client.csv2Dict(
                self.ft_client.query("DESCRIBE %(ft_table_id)s" % params))
        # This is recommended as a replacement:
        params['ft_cols'] = ",".join([c['name'] for c in ft_cols])

        # get new FT rows
        sql = ('select ROWID, %(ft_cols)s from "%(ft_table_id)s" '
               '%(sql_where)s ORDER BY seqid ASC LIMIT %(batch_size)s' % params)
        rows = self.ft_client.csv2Dict(self.ft_client.query(sql))
        logging.debug ("FT query: %s" % sql)

        # insert new rows into postgres
        sql_base = 'INSERT INTO "%(postgres_table_name)s" ' % params
        for row in rows:
            new_row = dict((key,row[key])
                           for key in (set(row) - set(['rowid', 'seqid'])))
            new_row[params['ft_id_field']] = row['rowid']
            new_row[params['seq_field']] = row['seqid']

            sql_items = ("(%s) VALUES (%s)"
                          %(','.join(new_row.keys()),
                            ','.join([str(psycopg2.extensions.adapt(v))
                                      for v in new_row.values()])))
            sql = "%s %s" % (sql_base, sql_items)
            logging.debug ("DB query: %s" % sql)
            cur.execute(sql)

        return len(rows)
#
#        # get ft records not synced
#        logging.info ("Syncing %s records" % n)
#        rows = cur.fetchall()
#
#        logging.debug ("Updating Fusion table records..." )
#        # insert any rows that are not already present in ft
#        # (match on seq_field)
#        # do not update records that already exist
#        rows = self.ft_client.insertOrReplaceRows(
#                ft_table_id, rows, self.seq_field, insert_only=True)
#
#        # update postgres with new ft rowids
#        logging.debug ("Updating FT IDs in postgres ..." )
#        for row in rows:
#            params['ft_id_value'] = row['ROWID']
#            params['seq_value'] = row[self.seq_field]
#            sql = 'update "%(postgres_table_name)s" '
#                  "set %(ft_id_field)s = %(ft_id_value)s "
#                  "where %(seq_field)s = '%(seq_value)s'" % params
#            cur.execute (sql)
#
#        logging.info ("Synced %s records from postgres to FT" % rows.len() )
#
