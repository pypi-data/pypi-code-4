#!/usr/bin/python
import os
import sys
import sqlite3
import requests
import helpers


class Packer(object):
    name = 'packer'
    version = '0.1.0'
    database_name = 'database.db'
    package_index_url = 'http://www.google.com/search'
    home = '{}/.packer'.format(os.path.expanduser('~'))
    dirs = {
        'PATH': 'path',
        'TEMP': 'temp',
        'PACKAGES': 'packages',
    }

    def __str__(self):
        return '{} ({})'.format(self.name, self.version)

    @classmethod
    def create_db(cls):
        db = sqlite3.connect(cls.database_name)
        with db:
            db.execute('''CREATE TABLE IF NOT EXISTS packages (name text)''')
            db.execute('''INSERT OR ROLLBACK INTO packages VALUES (?)''', (cls.name,))
        return db

    @classmethod
    def remove_db(cls):
        os.remove(cls.database_name)

    @classmethod
    def get_or_create_db(cls):
        if not os.path.exists(cls.database_name):
            return cls.create_db()
        return sqlite3.connect(cls.database_name)

    @classmethod
    def find_prev_install(cls):
        return os.path.exists(cls.home)

    @classmethod
    def install(cls):
        [os.makedirs('{}/{}'.format(cls.home, cls.dirs[d])) for d in cls.dirs]


    def __init__(self):
        if not self.find_prev_install():
            self.install()
        os.chdir(self.home)
        self.database = self.get_or_create_db()

    def list(self):
        packages = []
        for row in self.database.execute('SELECT * FROM packages'):
            p = helpers.Package._make(row)
            packages.append(p)
        return packages

    def search(self, name):
        # Check for if the package is installed locally
        for row in self.database.execute('SELECT * FROM packages WHERE name=?', (name,)):
            return helpers.Package._make(row)
        # Look in package index
        response = requests.get(self.package_index_url, params={'q':name})
        return response

    def close(self):
        self.database.commit()
        self.database.close()

    def __delete__(self):
        self.close()


if __name__ == '__main__':
    print 'Creating Packer instance'
    packer = Packer()
    print 'Listing Packages'
    pkgs = packer.list()
    print pkgs
    print 'Closing Packer instance'
    packer.close()
