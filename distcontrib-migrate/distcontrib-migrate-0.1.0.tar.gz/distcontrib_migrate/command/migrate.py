#!/usr/bin/env python

from __future__ import absolute_import

from distutils.core import Command
import migrate.versioning.api as dbmigrate


class migrate(Command):

    import os

    description = 'Runs sqlalchemy-migrate'

    __logname = os.environ['LOGNAME']

    user_options = [
        ('create-model',    None, "reverse engineer a database model"),
        ('upgrade',         None, "upgrades the database model (see: changeset)"),
        ('downgrade',       None, "downgrades the database model (see:changeset)"),
        ('test',            None, "performs upgrade+downgrade (see;changeset)"),
        ('status',          None, "database and repository status information"),

        #--
        ('repository=', 'r',  "migration repository. default: migrate"),
        ('scripts=',    's',  "administration scripts directory. default: admin"), 
        ('url=',        'u',  "database connection string. default: postgresql://" + __logname + "@localhost:5432/sample"),
        ('changeset=',  'v',  "apply a specific changeset version") ]

    boolean_options = ['create-model', 'upgrade', 'downgrade', 'test', 'status' ]
    help_options    = [ ]
    negative_opt    = { }
    sub_commands    = [ ]

    def initialize_options(self):
        self.create_model    = False
        self.upgrade         = False
        self.downgrade       = False
        self.test            = False
        self.status          = False
        #--
        self.scripts     = 'admin'
        self.repository  = 'migrate'
        self.url         = 'postgresql://' + migrate.__logname + '@localhost:5432/sample'
        self.changeset   = None

    def finalize_options(self):
        from distcontrib_migrate.dsn import dsn
        self.repository = self.scripts + '/' + self.repository
        self.url = dsn(self.url, dry_run=self.dry_run).normalize()

    def run(self):
        self.__bootstrap()
        if self.create_model:    self.__create_model()
        if self.upgrade:         self.__upgrade(self.changeset)
        if self.downgrade:       self.__downgrade(self.changeset)
        if self.test:            self.__test()
        if self.status:          self.__status()

    def __bootstrap(self):
        import os
        if not self.dry_run:
            # create repository
            if not os.path.exists(self.repository):
                try:
                   os.makedirs(os.path.dirname(self.repository))
                except:
                    pass
                dbmigrate.create(self.repository, self.distribution.get_name())
            # put database under version control    
            try:
                self.__database_version()
            except:
                dbmigrate.version_control(self.url, self.repository, self.changeset)

    def __create_model(self):
        if not self.dry_run:
            result = dbmigrate.create_model(self.url, self.repository)
            v = '%03d' % (self.__model_version() + 1)
            path = self.repository + '/versions/' + v + '_reverse_engineered.py'
            f = open(path, 'w')
            f.write(result)
            f.close()

    def __upgrade(self, changeset):
        if not self.dry_run:
            if changeset is None:
                 changeset = self.__model_version()
            dbmigrate.upgrade(self.url, self.repository, version=changeset)

    def __downgrade(self, changeset):
        if not self.dry_run:
            if changeset is None:
                 changeset = max(0, self.__database_version() - 1)
            dbmigrate.downgrade(self.url, self.repository, changeset)

    def __test(self):
        if not self.dry_run:
            src = self.__database_version()
            dst = self.__model_version()
            self.__upgrade(dst)
            self.__downgrade(src)

    def __status(self):
        if self.verbose:
            model_version    = self.__model_version()
            database_version = self.__database_version()
            print('Model version:    %d' % model_version)
            print('Database version: %d' % database_version)

    def __model_version(self):
        return int(dbmigrate.version(self.repository).value)

    def __database_version(self):
        return int(dbmigrate.db_version(self.url, self.repository))
