import os
import datetime
from fabric.api import task, settings, hide, puts
from djeploy import djeploy_require, get_env, command


def get_mysql_options(extra=None, connect_as=None, dbhost=None, port=None,
                      dbname=None, password=None):
    cmd_map = {
        'connect_as': '-u %s' % connect_as if connect_as else None,
        'dbhost': '-h %s' % dbhost if dbhost else None,
        'port': '-P %s' % str(port) if port else None,
        'dbname': '-D %s' % dbname if dbname else None,
        'password': '-p%s' % password if password else None,
    }

    return ' '.join([x for x in cmd_map.values() + [extra] if x])


@task
def mysql_query(query, connect_as=None, dbname=None,
                password=None, dbhost=None, port=None,
                extra_opts=None):
    opts = '%s ' % extra_opts if extra_opts else ''
    opts += get_mysql_options(
        connect_as=connect_as,
        dbhost=dbhost,
        port=port,
        dbname=dbname,
        password=password,
    )

    cmd = 'mysql %s -e "%s"' % (opts, query)
    c_opts = {}
    if command.is_local:
        c_opts['capture'] = True
    return command.run(cmd, **c_opts)


@task
def mysql_change_user_password(uname, user_password, connect_as=None,
                               password=None, dbhost=None, port=None):
    sql = 'SET PASSWORD FOR %s = PASSWORD(\'%s\');' % (uname, user_password)
    mysql_query(sql, connect_as, password, dbhost, port)


@task
def mysql_user_exists(username, connect_as=None,
                      password=None, dbhost=None, port=None):
    query = 'use mysql; SELECT User FROM user WHERE User = \'%s\';' % username
    with settings(hide('running'), warn_only=True):
        res = mysql_query(
            query,
            connect_as=connect_as,
            password=password,
            dbhost=dbhost,
            port=port,
            extra_opts='-N -r -B',
        )
    return res.succeeded and (res == username)


@task
def mysql_create_user(username, user_host='localhost', user_password=None,
                      connect_as=None, password=None, dbhost=None, port=None):
    query = 'CREATE USER \'%s\'@\'%s\'' % (username, user_host)
    if user_password is not None:
        query += ' IDENTIFIED BY \'%s\'' % user_password
    query += ';'

    with settings(hide('running')):
        mysql_query(
            query,
            connect_as=connect_as,
            password=password,
            dbhost=dbhost,
            port=port,
        )
    puts('Created MySQL user "%s".' % username)


@task
def mysql_delete_user(username, user_host='localhost', connect_as=None,
                      password=None, dbhost=None, port=None):
    query = 'DROP USER \'%s\'@\'%s\';' % (username, user_host)
    mysql_query(
        query,
        connect_as=connect_as,
        password=password,
        dbhost=dbhost,
        port=port,
    )


@task
def mysql_db_exists(dbname, connect_as=None,
                    password=None, dbhost=None, port=None):
    query = 'SHOW DATABASES;'
    with settings(hide('running'), warn_only=True):
        res = mysql_query(
            query,
            connect_as=connect_as,
            password=password,
            dbhost=dbhost,
            port=port,
            extra_opts='-N -r -B',
        )
    return res.succeeded and (dbname in res.split())


@task
def mysql_create_db(dbname, owner=None, owner_host='localhost', charset='utf8',
                    collate='utf8_general_ci', connect_as=None, password=None,
                    dbhost=None, port=None):
    query = 'CREATE DATABASE %s CHARACTER SET %s COLLATE %s;' % (
        dbname,
        charset,
        collate,
    )
    mysql_query(
        query,
        connect_as=connect_as,
        password=password,
        dbhost=dbhost,
        port=port,
    )

    if owner:
        query = \
         'GRANT ALL PRIVILEGES ON %s.* TO \'%s\'@\'%s\' WITH GRANT OPTION;' % (
            dbname,
            owner,
            owner_host,
        )
        mysql_query(
            query,
            connect_as=connect_as,
            password=password,
            dbhost=dbhost,              
            port=port,                          
        )


@task
def mysql_delete_db(dbname, connect_as=None, password=None,
                    dbhost=None, port=None):
    query = 'DROP DATABASE IF EXISTS %s;' % dbname
    mysql_query(
        query,
        connect_as=connect_as,
        password=password,
        dbhost=dbhost,
        port=port,
    )


@task
def mysql_backup_db(dbname, backup_dir='~/', connect_as=None,
                    password=None, dbhost=None, port=None):
    now = datetime.datetime.now()
    backup_fname = '%s-%s.sql' % (dbname, now.strftime('%m-%d-%Y.%H%M%S'))
    opts = get_mysql_options(
        extra=dbname,
        connect_as=connect_as,
        dbhost=dbhost,
        port=port,
        password=password,
    )

    with command.cd(backup_dir):
        cmd = 'mysqldump %s > %s' % (opts, backup_fname)
        command.run(cmd)
        command.run('gzip %s' % backup_fname)


@task
def mysql_backup_all(backup_dir='~/', connect_as=None, password=None,
                     dbhost=None, port=None):
    now = datetime.datetime.now()
    backup_fname = 'all_dbs-%s.sql' % now.strftime('%m-%d-%Y.%H%M%S')
    opts = get_mysql_options(
        extra='--all-databases',
        connect_as=connect_as,
        dbhost=dbhost,
        port=port,
        password=password,
    )

    with command.cd(backup_dir):
        cmd = 'mysqldump %s > %s' % (opts, backup_fname)
        command.run(cmd)
        command.run('gzip %s' % backup_fname)
