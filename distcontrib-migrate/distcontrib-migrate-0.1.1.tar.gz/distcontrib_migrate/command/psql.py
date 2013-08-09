#!/usr/bin/env python

from distutils.core import Command


class psql(Command):

    import os

    description = 'Runs psql'

    __logname = os.environ['LOGNAME']

    user_options = [
        ('createuser', None, "create user"),
        ('createdb',   None, "create database"),
        ('dropuser',   None, "drop user "),
        ('dropdb',     None, "drop database"),
        ('url=',        'u',  "database connection string. default: postgresql://" + __logname + "@localhost:5432/sample"), ]

    boolean_options = [ 'createuser', 'createdb', 'dropuser', 'dropdb' ]
    help_options    = [ ]
    negative_opt    = { }
    sub_commands    = [ ]

    def initialize_options(self):
        self.createuser  = False
        self.createdb    = False
        self.dropuser    = False
        self.dropdb      = False
        self.url         = 'postgresql://' + psql.__logname + '@localhost:5432/sample'

    def finalize_options(self):
        from distcontrib_migrate.dsn import dsn
        check = dsn(self.url, dry_run=self.dry_run).check()
        self.__username = check['username']
        self.__password = check['password']
        self.__database = check['database']

    def __passwd(self):
        (password, confirm) = self.db._ask_pass(confirm=False)
        return password + '\n'

    def run(self):
        self.__call(['/usr/bin/sudo','-k','-S','-u','postgres','/usr/bin/whoami'], self.__passwd)

        if self.dropdb or self.dropuser:
            self.__call(['/usr/bin/sudo','-u','postgres',
                         '/usr/bin/dropdb',self.__database])

        if self.dropuser:
            self.__call(['/usr/bin/sudo','-u','postgres',
                         '/usr/bin/dropuser',self.__username])

        if self.createuser:
            self.__call(['/usr/bin/sudo','-u','postgres',
                         '/usr/bin/createuser','--createdb',self.__username])
            self.__call(['/usr/bin/sudo','-u','postgres',
                         '/usr/bin/psql','-c', 
                            "alter user %s with password '%s'" % (self.__username, self.__password)])

        if self.createdb:
            self.__call(['/usr/bin/sudo','-u','postgres',
                         '/usr/bin/createdb',self.__database,
                         '--owner',self.__username])

    def __call(self, args, method=None, verbose=True):
        cmd = ' '.join(args)
        if cmd.find('password') == -1:
            print(cmd)
        if not self.dry_run:
            text = method() if method else None
            import subprocess as sp
            p = sp.Popen(args, shell=False, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
            (stdout, stderr) = p.communicate(text)
            if stdout is not None: print(stdout)
            if stderr is not None: print(stderr)
