#!/usr/bin/env python
import sys
import os
import codecs
from optparse import OptionParser

import mysql.connector
from mysql.connector import errorcode

from jinja2 import Environment, FileSystemLoader


VERSION = "0.2"

TEMPLATE = "db.tmpl"


def get_tables(cursor, schema):
    SELECT = "select * from TABLES where TABLE_SCHEMA=%s order by TABLE_NAME"
    cursor.execute(SELECT, (schema,))
    tables = []
    for table in cursor.fetchall():
        tables.append(dict(zip(cursor.column_names, table)))
    return tables


def get_indexes(cursor, schema, table):
    SELECT = "show index from %s.%s" % (schema, table)
    cursor.execute(SELECT)
    indexes = []
    for indexe in cursor.fetchall():
        indexes.append(dict(zip(cursor.column_names, indexe)))
    return indexes


def get_fields(cursor, schema, tablename):
    SELECT = "select * from COLUMNS where TABLE_SCHEMA=%s and " + \
             "TABLE_NAME=%s order by ORDINAL_POSITION"
    cursor.execute(SELECT, (schema, tablename))
    fields = []
    for field in cursor.fetchall():
        fields.append(dict(zip(cursor.column_names, field)))
    return fields


def get_f_key(cursor, schema, tablename, fieldname):
    SELECT = """select * from KEY_COLUMN_USAGE where TABLE_SCHEMA=%s
              and TABLE_NAME=%s
              and COLUMN_NAME=%s and REFERENCED_TABLE_NAME is not null"""
    cursor.execute(SELECT, (schema, tablename, fieldname))
    f_keys = []
    for f_key in cursor.fetchall():
        f_keys.append(dict(zip(cursor.column_names, f_key)))
    return f_keys


def get_references(cursor, schema, tablename):
    SELECT = """select * from KEY_COLUMN_USAGE where TABLE_SCHEMA=%s
             and REFERENCED_TABLE_NAME=%s
             order by REFERENCED_TABLE_NAME"""
    cursor.execute(SELECT, (schema, tablename))
    references = []
    for reference in cursor.fetchall():
        references.append(dict(zip(cursor.column_names, reference)))
    return references

USAGE = "usage: %prog [options] database"


def main():

    parser = OptionParser(usage=USAGE, version=VERSION)
    parser.add_option("-f", "--file", dest="filename",
                  help="write documentation to FILE, default database.html",
                  metavar="FILE")
    parser.add_option("-H", "--host",
                  action="store", dest="host",
                  help="Database server hostname")
    parser.add_option("-u", "--user",
                  action="store", dest="user",
                  help="database username")
    parser.add_option("-p",
                  action="store_true", dest="ask_pass",
                  help="ask for a database password")
    parser.add_option("--password",
                  action="store", dest="password",
                  help="database password")
    parser.add_option("-P", "--port",
                  action="store", dest="port",
                  help="database connection port")
    parser.add_option("-v",
                  action="store_true", dest="verbose",
                  help="Verbose mode")

    options, args = parser.parse_args()

    if len(args) == 0:
        parser.error("No database provided")

    if len(args) > 1:
        parser.error("Too many arguments")

    conn_params = {"database": "information_schema"}

    schema = args[0]

    if options.host:
        conn_params['host'] = options.host
    if options.user:
        conn_params['user'] = options.user
    if options.ask_pass:
        import getpass
        password = getpass.getpass("%s database password : " % schema)
        conn_params['password'] = password
    if options.password:
        conn_params['password'] = options.password
    if options.port:
        conn_params['port'] = options.port

    try:
        conn = mysql.connector.connect(**conn_params)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exists")
        else:
            print(err)
        sys.exit(2)

    cursor = conn.cursor()

    if options.filename:
        filename = options.filename
    else:
        filename = args[0] + ".html"

    tables = get_tables(cursor, schema)
    for table in tables:
        tablename = table['TABLE_NAME']

        if options.verbose:
            print("\nTABLE %s" % tablename)
            print("----------------------------------------------------\n")

        # search fields
        fields = get_fields(cursor, schema, tablename)
        for field in fields:
            fieldname = field['COLUMN_NAME']
            field['f_keys'] = get_f_key(cursor, schema, tablename, fieldname)
            if options.verbose:
                print("  %s : %s" % (fieldname, field))

        table['fields'] = fields
        table['indexes'] = get_indexes(cursor, schema, tablename)
        table['references'] = get_references(cursor, schema, tablename)

    cursor.close()
    conn.close()

    env = Environment(loader=FileSystemLoader(os.path.dirname(__file__)))
    template = env.get_template(TEMPLATE)

    context = {
      'tables': tables,
      'schema': schema,
    }

    page = template.render(**context)

    with codecs.open(filename, 'w', 'utf-8-sig') as f:
        f.write(page)
        f.close()

if __name__ == '__main__':
    sys.exit(main() or 0)
