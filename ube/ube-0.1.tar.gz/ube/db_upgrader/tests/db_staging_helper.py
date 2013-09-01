'''
Created on Sep 1, 2012

@author: Nicklas Boerjesson
@note: 
Helpers for testing database upgrades.
Oracle has a different structure, making it impossible(?) to create databases through SQL-DDL.
This is difficult on DB2 as well.
'''


from ube.db_upgrader.db_upgrader import DBUpgrader
from qal.dal.dal_types import DB_POSTGRESQL, DB_MYSQL, db_type_to_string ,\
    DB_SQLSERVER, DB_DB2, DB_ORACLE
from qal.tools.meta_queries import Meta_Queries
from qal.dal.tests.framework import get_default_dal
from time import time
from ube.concerns.connection import set_connection




def handle_none(value):
    if value == None:
        return ''
    else:
        return value


class db_staging_helper():
    
    debuglevel = 0
    results = list()


    def print_and_clear_results(self, _description):
        print(_description)
        for _curr_result in self.results:
            print(_curr_result)
        self.results = None
        self.results = list()
       
    def drop_all_tables(self, _db_type, _dropdal):
        _meta_queries = Meta_Queries(_dropdal)
        _tables = _meta_queries.table_list_by_schema(_dropdal.db_username.upper())
        for _curr_table in _tables:
            _curr_sql ="DROP TABLE  \"" + _curr_table +"\""
            if _db_type == DB_ORACLE:
                _curr_sql+=" cascade constraints"

            _dropdal.execute(_curr_sql)
            print(db_type_to_string(_db_type) + _curr_sql)
                
    def oracle_drop_all_sequences(self, _dropdal):
        _meta_queries = Meta_Queries(_dropdal)
        _sequences = _meta_queries.oracle_all_sequences()
        for _curr_sequence in _sequences:
            _curr_sql ="DROP SEQUENCE " + _curr_sequence +""
            _dropdal.execute(_curr_sql)
            print(_curr_sql)
                        
    def setup_database(self, _db_type, _db_name):
        if _db_type == DB_POSTGRESQL:
            _dropdal = get_default_dal(DB_POSTGRESQL, "postgres")
            _dropdal.db_connection.autocommit = True
            _dropdal.execute('DROP DATABASE IF EXISTS ' +_db_name)
            _dropdal.execute("CREATE DATABASE " + _db_name + " ENCODING='UTF8' TEMPLATE=template0")
            _dropdal.db_connection.autocommit = False
            _dropdal.close()
            print (db_type_to_string(_db_type) + " database dropped and created")
                   
        elif _db_type == DB_MYSQL:
            _dropdal = get_default_dal(DB_MYSQL, "mysql")
            _dropdal.execute('DROP DATABASE IF EXISTS ' +_db_name)
            _dropdal.execute("CREATE DATABASE " + _db_name )
            _dropdal.close()
            print (db_type_to_string(_db_type) +  " database dropped and created")

        elif _db_type == DB_SQLSERVER:
            _dropdal = get_default_dal(DB_SQLSERVER, "master")
            _dropdal.execute("USE Master;")
            _dropdal.execute("IF db_id('" + _db_name + "') IS NOT NULL BEGIN DROP DATABASE " + _db_name + " END")
            _dropdal.execute("CREATE DATABASE " +_db_name)
            _dropdal.db_connection.autocommit = False
            _dropdal.close()
            print (db_type_to_string(_db_type) + " database dropped and created")
            
        if _db_type == DB_ORACLE:
            try:
                _dropdal = get_default_dal(_db_type, _db_name)
                self.drop_all_tables(_db_type, _dropdal)
                self.oracle_drop_all_sequences(_dropdal)
#                _dropdal.execute('''Begin
#for c in (select table_name from user_tables WHERE TABLESPACE_NAME = \''''+_dropdal.db_username + '''') loop
#execute immediate ('drop table '||c.table_name||' cascade constraints');
#end loop;
#End;
#''' )

                _dropdal.commit()
            except Exception as e:
                print('Minor: Database probably already dropped. Error: ' + str(e))
            finally:            
                _dropdal.close()
        
        if _db_type == DB_DB2:
            try:
                _dropdal = get_default_dal(_db_type, _db_name)

                self.drop_all_tables(_db_type, _dropdal)


                _dropdal.commit()
            except Exception as e:
                print('Minor: Database probably already dropped. Error: ' + str(e) )
            finally:            
                _dropdal.close() 
                
    def set_root_passwd(self, _db_type, _db_name, _password):
        set_connection(get_default_dal(_db_type, _db_name))
        from ube.api.tree.access import access
        _access = access()
        _user = _access.load_nodes(_nodeids = [1], _with_data = True)[0]
        _user.Login = 'root'
        _user.Password = _password
        _access.save_nodes([_user])
               

                        
    def upgrade_database(self,_db_type, _db_name, _xmlfiles):
        
        print ("_______Testing " + db_type_to_string(_db_type) + " upgrade_____________")
        _start = time()
        self.setup_database(_db_type, _db_name)
        try:
            _dal = get_default_dal(_db_type, _db_name)
            _upgrader = DBUpgrader(_dal)
            _upgrader.debuglevel = self.debuglevel
            
            for _currfile in _xmlfiles: 
                _upgrader.upgrade_database(_currfile)
                
        finally:
            _dal.close()
        
        self.results.append("Testing " + db_type_to_string(_db_type) + " upgrade took " + str(time()-_start) + " seconds.")
        
        #self.debuglevel = 3      
      
