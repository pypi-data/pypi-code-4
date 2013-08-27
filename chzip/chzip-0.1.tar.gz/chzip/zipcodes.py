#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Implementation classes that do the heavy lifting of the module"""

import datetime
import shutil
import os

import chzip.common


class Downloader(chzip.common.Downloader):
    """The Downloader of Swiss Post MAT[CH] ZIP resources."""
    # Output name of the downloaded files (without extension)
    # and the direct URL for download
    files = {
        'plz_light': 'https://match.post.ch/download?file=10000',
        #'plz_plus_1': 'https://match.post.ch/download?file=10001',
        #'plz_plus_2': 'https://match.post.ch/download?file=10002'
    }

    # Download and unzip the first file from the archive
    # Returns the extracted filename
    def _download_and_unzip(self, filename, extract_dir):
        # Download
        url = self.files[filename]
        zip_name = filename + '.zip'
        zip_path = self._download(url, extract_dir, zip_name)

        inst = ResourceInstaller(zip_path, extract_dir, filename)
        inst.unzip()
        return inst

    def download_and_unpack(self, download_dir):
        """Downloads the ZIP files from MAT[CH], extract the 
        text file, populate the internal SQLite3 database,
        and delete all the intermediary files.
        
        :param str download_dir: Resource directory that will contain both the temporary
                                 files (which will be deleted) and the database."""
        for filename in self.files:
            db_path = os.path.join(download_dir, ZipCodesDatabase.DEFAULT_FILENAME)
            try:
                os.remove(db_path)
            except:
                pass

            inst = self._download_and_unzip(filename, download_dir)
            inst.install()

            # Transform raw text file to a SQLite3 database
            self._to_sqlite3(inst.extracted_txt_path(), db_path)
            inst.delete()

    def upgrade_and_unpack(self, download_dir, force=False):
        """Does the same as :py:meth:`download_and_unpack`
        but returns immediately if files are up-to-date and do not delete previous
        database. This can be handy in cases of failure, so is the recommended way
        to update the database.
        
        :param str download_dir: Resource directory that will contain both the temporary
                             files (which will be deleted) and the database.
        :param bool force: Set to true to force update even if files are up-to-date."""
        if self.is_up_to_date and not force:
            print('chzip is already up-to-date, then do upgrade will be done. '
                  'You can force it to upgrade by setting the \'force\' argument '
                  'to True.')
            return

        for filename in self.files:
            inst = self._download_and_unzip(filename, download_dir)
            # Transform raw text file to a SQLite3 database
            self._to_sqlite3(inst.extracted_txt_path(),
                             os.path.join(download_dir, filename + '.new.db'))
            # Here unlike `download_and_unpack` the file is only replaced
            # at the end.
            inst.install()
            shutil.move(os.path.join(download_dir, filename + '.new.db'),
                        os.path.join(download_dir, ZipCodesDatabase.DEFAULT_FILENAME))
            inst.delete()

    def is_up_to_date(self, abs_resource_file):
        """:returns: true if the specified file is up-to-date."""
        # ZIP codes files are up-to-date if lastly modified in the current month
        return self._get_lastchange_datetime(
            abs_resource_file).month == datetime.datetime.now().month

    def _to_sqlite3(self, txt_file, db_path):
        # Create and fill database
        db = ZipCodesDatabase(db_path, txt_file)
        # Close database
        del db  # or db.close()


### Unzipper - Installer

import zipfile


class ResourceInstaller:
    """Unzip the file downloaded from Swiss Post and install it at the
    appropriate location.

    Usage: call :py:meth:`unzip` and :py:meth:`install` for a complete installation."""

    def __init__(self, zip_path, extract_dir, extract_to_filename):
        self.zip_path = zip_path
        self.extract_dir = extract_dir
        self.filename = extract_to_filename
        self.wanted_extracted_name = extract_to_filename + '.txt'
        self.installed = False

    def unzip(self):
        """Unzip the first file from ZIP to the specified directory
        
        :returns: the filename extracted"""

        with zipfile.ZipFile(self.zip_path) as zip:
            first_filename = zip.namelist()[0]
            zip.extract(first_filename, self.extract_dir)
            self.really_extracted_filename = first_filename
            return first_filename

    def install(self):
        """Move file to its definitive location"""
        # Move extracted file to the name from above
        shutil.move(self.real_path(), self.wanted_path())
        self.installed = True

    def wanted_path(self):
        """:returns: the desired path of the extracted text file."""
        return os.path.join(self.extract_dir, self.wanted_extracted_name)

    def real_path(self):
        """:returns: the path of the extracted text file, before moving it.

        So this is the real path of the file just after unzipping.

        If you want to work on the file before installing, call this method
        else call :py:meth:`wanted_path`. :py:meth:`extracted_txt_path` will 
        figure this out for you."""
        return os.path.join(self.extract_dir, self.really_extracted_filename)

    def extracted_txt_path(self):
        """:returns: always returns the location of the text file, no matter if :py:meth:`install` was called or not."""
        if self.installed:
            return self.wanted_path()
        else:
            return self.real_path()

    def delete(self):
        """Delete temporary files"""
        for f in [self.zip_path,
                  os.path.join(self.extract_dir,
                               self.wanted_extracted_name),
                  os.path.join(self.extract_dir,
                               self.really_extracted_filename)]:
            try:
                self._delete(f)
            except OSError:
                pass

    def _delete(self, file):
        os.remove(file)


### Database

import csv
import sqlite3
import codecs
from chzip.common import Locality


class ZipCodesDatabase:
    DEFAULT_FILENAME = 'zipcodes.db'

    def __init__(self, db_path=None, csv_path=None):
        """A database of zipcodes.

        Provide the `csv_path` argument the first time to convert the CSV
        text file to a SQLite3 table.

        Afterwards, use the generated database file. Get it with ``db_path``."""

        self.db_path = db_path

        if csv_path is not None:
            if db_path is None:
                raise ValueError('The db_path must be specified to convert '
                                 'the CSV file to a database.')
            self._create_db()
            self._import(csv_path)
        elif db_path is not None:
            # Open the existing database
            self._open()
        else:
            raise ValueError(
                'db_path or csv_path + db_path must be provided.')

    def _open(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
        except sqlite3.OperationalError as err:
            raise Exception('Cannot open database %s. Did you call '
            'chzip.download_and_unpack_all() ?' % self.db_path)

    def _create_db(self):
        self._open()
        cursor = self.conn.cursor()
        cursor.execute('CREATE TABLE zipcodes'
                       '(onrp integer, type integer, zip integer,'
                       'short_name text, long_name text, canton text)')
        self.conn.commit()
        cursor.close()

    # def _slow_import(self, csv_path):  # creating objects
    #                                      can be useful to test insert()
    #     with codecs.open(csv_path, 'rb', 'iso-8859-1') as csvfile:
    #         csv_reader = csv.reader(csvfile, delimiter='\t')
    #         for row in csv_reader:
    #             l = Locality()
    #             l._onrp = int(row[0])
    #             l._zip_type_number = int(row[1])
    #             l.zip = int(row[2])
    #             # row[3] is additional NPA number. Ignored.
    #             l.short_name = row[4]
    #             l.long_name = row[5]
    #             l.canton = row[6]
    #             self.insert(l)

    # as import but avoids closing the connection and creating objects
    def _import(self, csv_path):
        with codecs.open(csv_path, 'rb', 'iso-8859-1') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter='\t')

            cursor = self.conn.cursor()
            items = []

            for row in csv_reader:
                item = (row[0], row[1], row[2], row[4], row[5], row[6])
                items.append(item)

            cursor.executemany("INSERT INTO zipcodes ("
                               "onrp, type, zip, short_name, long_name, canton"
                               ") values (?, ?, ?, ?, ?, ?)", items)
            self.conn.commit()
            cursor.close()

    # TODO: "with safe_cursor(self.conn) as cursor:"
    # to avoid creating the cursor, committing to DB and closing the cursor

    def insert(self, locality):
        """Inserts a locality in the database"""
        l = locality
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO zipcodes (onrp, type, zip, '
                       'short_name, long_name, canton)'
                       'VALUES (?, ?, ?, ?, ?, ?)',
                       (l._onrp, l._zip_type_number, l.zip,
                        l.short_name, l.long_name, l.canton))
        self.conn.commit()
        cursor.close()

    def query(self, search=None, where_stmt=None):
        """Returns records matching search as Localities.

        .. :param dict: Dictionnary whose keys are column names and value the
        value in the table."""
        cursor = self.conn.cursor()

        if search:
            where_str, fields = self.__dict_to_where_clause(search)
            cursor.execute('SELECT * from zipcodes WHERE ' + where_str, fields)
        elif where_stmt:
            cursor.execute('SELECT * from zipcodes WHERE ' + where_stmt)
        else:
            cursor.execute('SELECT * from zipcodes')

        results = self._raw_list_to_locality_list(cursor)
        cursor.close()
        return results

    def __dict_to_where_clause(self, dic):
        """Returns the where part of the query AND the fields for the DB-API
        query method."""
        where_str = '1=1'
        fields = []

        for term in dic:
            value = dic[term]
            if value:
                where_str += ' AND ' + term + '= ?'
                fields.append(value)

        return where_str, fields

    def all(self):
        """Returns all records from database as Localities."""
        return self.query()

    def _row_to_locality(self, row):
        l = Locality()
        l._onrp = int(row[0])
        l._zip_type_number = int(row[1])
        #l.zip_type done automatically by _zip_type_number setter
        l.zip = int(row[2])
        l.short_name = row[3]
        l.long_name = row[4]
        l.canton = row[5]
        return l

    def _raw_list_to_locality_list(self, iterable):
        """Convert the list of rows from the zipcodes tables to a list of
        Localities."""
        localities = []
        for item in iterable:
            localities.append(self._row_to_locality(item))
        return localities

    def close(self):
        """To close the database manually."""
        try:
            self.conn.close()
        except:
            pass

    def __del__(self):
        self.close()
