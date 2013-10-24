#Fusion Table Insert/Update Utility

from FTClient import FTClient
from FTClient.authorization.clientlogin import ClientLogin
from FTClient.sql.sqlbuilder import SQL
import MySQLdb
from MySQLdb.cursors import DictCursor
import time
import logging


class MysqlFTSync:
    ft_id_field = 'ft_id'
    seq_field = 'seq'
    ft_client = None
    db = None
        
    def __init__(self, ft_client, mysql_db, ft_id_field='ft_id', seq_field='seq'):
        self.ft_client = ft_client
        self.db = mysql_db
        self.ft_id_field = ft_id_field
        self.seq_field = seq_field


    def sync_mysql_to_ft (self, mysql_table_name, ft_table_id,  batch_size=100):
        params = {
            'mysql_table_name': mysql_table_name,
            'ft_table_id': ft_table_id,
            'batch_size': batch_size,
            'ft_id_field': self.ft_id_field,
            'seq_field': self.seq_field
        }
        logging.debug ("Syncng from mysql table %(mysql_table_name)s to FT table %(ft_table_id)s" % params )
        logging.debug ("Using batch size %s" %(batch_size) )


        logging.debug ("Retrieving mysql records..." )
        sql = 'select * from %(mysql_table_name)s where `%(ft_id_field)s` is null order by %(seq_field)s asc limit %(batch_size)s' % params
        
        cur = self.db.cursor(DictCursor)
        n = cur.execute (sql)
        if not n:
            logging.info ("All records synced. Nothing to do.")
            return 0
            
        # get mysql records not synced
        logging.info ("Syncing %s records..." % n)
        rows = cur.fetchall()
        
        if self.seq_field != 'seqid':
            # translate sequence id field name
            for row in rows:
                row['seqid'] = row[self.seq_field]
                del row[self.seq_field]
        
        logging.debug ("Updating Fusion table records..." )
        # insert any rows that are not already present in ft (match on seq_field)
        # do not update records that already exist
        rows = self.ft_client.insertOrReplaceRows(ft_table_id, rows, 'seqid', insert_only=True)
        
        # update mysql with new ft rowids
        logging.debug ("Updating FT IDs in mysql ..." )
        for row in rows:
            params['ft_id_value'] = row['rowid']
            params['seq_value'] = row['seqid']
            sql = "update %(mysql_table_name)s set %(ft_id_field)s = %(ft_id_value)s where %(seq_field)s = '%(seq_value)s'" % params
            cur.execute (sql)
        
        logging.info ("Synced %s records from mysql to FT" % len(rows) )

        return len(rows)
        
    def sync_ft_to_mysql (self, mysql_table_name, ft_table_id,  batch_size=100):
        params = {
            'mysql_table_name': mysql_table_name,
            'ft_table_id': ft_table_id,
            'batch_size': batch_size,
            'ft_id_field': self.ft_id_field,
            'seq_field': self.seq_field,
            'sql_where': ''
        }
        logging.debug ("Syncng from FT table %(ft_table_id)s to mysql table %(mysql_table_name)s" % params )
        logging.debug ("Using batch size %s" %(batch_size) )

        logging.debug ("Retrieving Fustion Table records..." )
        
        # get largest sequence number present in mysql
        cur = self.db.cursor(DictCursor)
        sql = 'select %(seq_field)s from %(mysql_table_name)s order by %(seq_field)s desc limit 1' % params
        n = cur.execute (sql)

        if not n:
            logging.debug ("Mysql table empty, syncing everything")
        else:
            row = cur.fetchone()  
            seqid = row[params['seq_field']]

            logging.debug ("Largest seqid found in MySQL table %s: %s" % (mysql_table_name, seqid) )
            params['sql_where'] = "WHERE seqid > '%s'" % self.db.escape_string(str(seqid))
            
        # get columns present in FT
        ft_cols = self.ft_client.csv2Dict(self.ft_client.query("DESCRIBE %(ft_table_id)s" % params)) 
        params['ft_cols'] = ",".join([c['name'] for c in ft_cols])

        
        # get new FT rows
        sql = 'select ROWID, %(ft_cols)s from %(ft_table_id)s %(sql_where)s ORDER BY seqid ASC LIMIT %(batch_size)s' % params
        rows = self.ft_client.csv2Dict(self.ft_client.query(sql))

        # insert new rows into mysql    
        sql_base = "INSERT INTO %(mysql_table_name)s set " % params
        for row in rows:
            new_row = dict((key,row[key]) for key in (set(row) - set(['rowid', 'seqid'])))
            new_row[params['ft_id_field']] = row['rowid']
            new_row[params['seq_field']] = row['seqid']
            
            sql_items = ",".join(["%s = '%s'" % (key, self.db.escape_string(value)) for key,value in new_row.items()])
            sql = "%s %s" % (sql_base, sql_items)
            logging.debug('MYSQL: %s'%sql)
            cur.execute(sql)
        
        return len(rows)    
#            
#        # get ft records not synced
#        logging.info ("Syncing %s records" % n)
#        rows = cur.fetchall()
#
#        logging.debug ("Updating Fusion table records..." )
#        # insert any rows that are not already present in ft (match on seq_field)
#        # do not update records that already exist
#        rows = self.ft_client.insertOrReplaceRows(ft_table_id, rows, self.seq_field, insert_only=True)
#      
#        # update mysql with new ft rowids
#        logging.debug ("Updating FT IDs in mysql ..." )
#        for row in rows:
#            params['ft_id_value'] = row['ROWID']
#            params['seq_value'] = row[self.seq_field]
#            sql = "update %(mysql_table_name)s set %(ft_id_field)s = %(ft_id_value)s where %(seq_field)s = '%(seq_value)s'" % params
#            cur.execute (sql)
#        
#        logging.info ("Synced %s records from mysql to FT" % rows.len() )
#    
