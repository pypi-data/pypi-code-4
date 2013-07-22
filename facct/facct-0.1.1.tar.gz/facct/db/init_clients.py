#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import time
import sqlite3 as lite
import data
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config

def get_db_path():
    appli_name = config.appli_name
    db_path =  os.path.join(os.path.expanduser('~'), '.%s' % appli_name, 'db',)
    print (db_path)
    if not os.path.exists(db_path):
        os.makedirs(db_path)
    return  os.path.join(os.path.expanduser('~'), '.%s' % appli_name, 'db',)


debug = False
def create_tables(cur, tables, data):
    for t in tables:
        cur.execute('DROP TABLE IF EXISTS %s' % t)
        request = 'CREATE TABLE %s(' % t + ', '.join(
                    [ '%s %s' % col for col in tables[t]]) + ')'
        print(request)
        cur.execute(request)
        request = 'INSERT INTO %s VALUES(' % t + '?, '*(len(tables[t])-1) + '? )'
        if not t in data:
            continue
        for r in data[t]: 
            for i, v in enumerate(r):
                if v and sys.version_info.major == 2 and tables[t][i][1] == 'TEXT':
                    r[i] = v.decode('utf-8')
                if v and tables[t][i][1] == 'DATE' and type(v) == type(str):
                    r[i] = datetime.datetime(
                        *(time.strptime(v, '%Y/%m/%d')[0:6])).date()
        if debug:
            print(request, data[t])
        try:
            cur.executemany(request, data[t])
        except:
            sys.stderr.write(_('Error while executing SQL statement {0} for {1}'
                    ).format(request, tables[t]))

def get_data(orga):
    return data.get_data(orga)

def get_tables():
    return data.get_tables()

def main(orga):
    tables = get_tables()
    data = get_data(orga)
    if not orga:
        sys.stderr.write('orga:%s is empty, please define\n' % orga)
        sys.exit(2)
    con = lite.connect(os.path.join(get_db_path(), '%s.db' % orga))
    with con:
        cur = con.cursor()    
        create_tables(cur, tables, data)

if __name__ == '__main__':
    sys.exit(main(config.get_args().orga))

