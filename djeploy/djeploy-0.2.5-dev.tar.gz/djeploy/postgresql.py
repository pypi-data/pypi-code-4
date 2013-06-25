import os
import datetime
from fabric.api import task, settings, hide
from djeploy.system import set_environment
from djeploy import djeploy_require, get_env, command


def get_pgsql_prefix(password=None):
    return set_environment('PGPASSWORD', password) if password else ''


def get_pgsql_command(cmd, password=None):
    return get_pgsql_prefix(password) + cmd


def get_pgsql_options(extra=None, connect_as=None, dbhost=None, port=None,
                      is_superuser=None, createdb=None, createrole=None,
                      template=None, out_file=None, encoding=None,
                      owner=None, database=None):
    cmd_map = {
        'connect_as': '-U %s' % connect_as if connect_as else None,
        'dbhost': '-h %s' % dbhost if dbhost else None,
        'port': '-p %s' % str(port) if port else None,
        'template': '-T %s' % template if template else None,
        'file': '-f %s' % out_file if out_file else None,
        'encoding': '-E %s' % encoding if encoding else None,
        'owner': '-O %s' % owner if owner else None,
        'database': '-d %s' % database if database else None,
    }

    # Special extras for create user
    if is_superuser is not None:
        cmd_map['is_superuser'] = '-s' if is_superuser else '-S'
    if createdb is not None:
        cmd_map['createdb'] = '-d' if createdb else '-D'
    if createrole is not None:
        cmd_map['createrole'] = '-r' if createrole else '-R'

    return ' '.join([x for x in cmd_map.values() + [extra] if x])


@task
def postgresql_query(query, connect_as=None, database=None,
                     password=None, dbhost=None, port=None,
                     extra_opts=None):
    opts = '%s ' % extra_opts if extra_opts else ''
    opts += get_pgsql_options(
        connect_as=connect_as,
        dbhost=dbhost,
        port=port,
        database=database,
    )

    cmd = get_pgsql_command('psql %s -c \'%s\'' % (opts, query), password)
    c_opts = {}
    if command.is_local:
        c_opts['capture'] = True
    return command.run(cmd, **c_opts)


@task
def postgresql_change_user_password(uname, user_password, connect_as=None,
                                    password=None, dbhost=None, port=None,
                                    database='template1'):
    # Uses PostgreSQL "Dollar Quoting" to help with CLI escaping issues.
    query = \
        'ALTER USER %s WITH PASSWORD $$%s$$' % (uname, user_password)
    with settings(hide('running')):
        postgresql_query(query, connect_as, database, password, dbhost, port)


@task
def postgresql_user_exists(username, connect_as=None, password=None,
                           dbhost=None, port=None, database='template1'):
    with settings(hide('everything'), warn_only=True):
        res = postgresql_query(
            '\\du',
            connect_as=connect_as,
            password=password,
            dbhost=dbhost,
            port=port,
            database=database,
            extra_opts='-t -A',
        )
    return res.succeeded and \
           (username in [x.split('|')[0] for x in res.split()])


@task
def postgresql_create_user(username, user_password=None, connect_as=None, 
                           is_superuser=False, createdb=False, 
                           createrole=False, password=None,
                           dbhost=None, port=None):
    opts = get_pgsql_options(
        extra=username,
        connect_as=connect_as,
        dbhost=dbhost,
        port=port,
        is_superuser=is_superuser,
        createdb=createdb,
        createrole=createrole,
    )

    cmd = get_pgsql_command('createuser %s' % opts, password)
    command.run(cmd)

    if user_password is not None:
        postgresql_change_user_password(
            username,
            user_password,
            connect_as,
            password,
            dbhost,
            port,
        )


@task
def postgresql_delete_user(username, connect_as=None, password=None,
                           dbhost=None, port=None):
    opts = get_pgsql_options(
        extra=username,
        connect_as=connect_as,
        dbhost=dbhost,
        port=port,
    )

    cmd = get_pgsql_command('dropuser %s' % opts, password)
    command.run(cmd)


@task
def postgresql_db_exists(dbname, connect_as=None, password=None,
                         dbhost=None, port=None, database='template1'):
    with settings(hide('everything'), warn_only=True):
        res = postgresql_query(
            '\\l',
            connect_as=connect_as,
            password=password,
            dbhost=dbhost,
            port=port,
            database=database,
            extra_opts='-t -A',
        )
    return res.succeeded and \
           (dbname in [x.split('|')[0] for x in res.split()])


@task
def postgresql_create_db(dbname, owner, encoding='UTF-8', connect_as=None,
                         template=None, password=None, dbhost=None, port=None):
    opts = get_pgsql_options(
        extra=dbname,
        owner=owner,
        connect_as=connect_as,
        dbhost=dbhost,
        port=port,
        template=template,
        encoding=encoding,
    )

    cmd = get_pgsql_command('createdb %s' % opts, password)
    command.run(cmd)


@task
def postgresql_delete_db(dbname, connect_as=None, password=None,
                         dbhost=None, port=None):
    opts = get_pgsql_options(
        extra=dbname,
        connect_as=connect_as,
        dbhost=dbhost,
        port=port,
    )
    
    cmd = get_pgsql_command('dropdb %s' % opts, password)
    command.run(cmd)


@task
def postgresql_backup_db(dbname, backup_dir='~/', connect_as=None,
                         password=None, dbhost=None, port=None):
    now = datetime.datetime.now()
    backup_fname = '%s-%s.sql' % (dbname, now.strftime('%m-%d-%Y.%H%M%S'))
    opts = get_pgsql_options(
        extra=dbname,
        connect_as=connect_as,
        dbhost=dbhost,
        port=port,
        out_file=backup_fname,
    )

    cmd = get_pgsql_command('pg_dump %s' % opts, password)

    with command.cd(backup_dir):
        command.run(cmd)
        command.run('gzip %s' % backup_fname)


@task
def postgresql_backup_all(backup_dir='~/', connect_as=None, password=None,
                          dbhost=None, port=None):
    now = datetime.datetime.now()
    backup_fname = 'all_dbs-%s.sql' % now.strftime('%m-%d-%Y.%H%M%S')
    opts = get_pgsql_options(
        connect_as=connect_as,
        dbhost=dbhost,
        port=port,
        out_file=backup_fname,
    )

    cmd = get_pgsql_command('pg_dumpall %s' % opts, password)

    with command.cd(backup_dir):
        command.run(cmd)
        command.run('gzip %s' % backup_fname)
