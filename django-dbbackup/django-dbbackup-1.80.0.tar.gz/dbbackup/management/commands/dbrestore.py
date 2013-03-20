"""
Restore pgdump files from Dropbox.
See __init__.py for a list of options.
"""
import os
import tempfile
import gzip

from ... import utils
from ...dbcommands import DBCommands
from ...storage.base import BaseStorage
from ...storage.base import StorageError
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.core.management.base import LabelCommand
from django.db import connection
from optparse import make_option


class Command(LabelCommand):
    help = "dbrestore [-d <dbname>] [-f <filename>] [-s <servername>]"
    option_list = BaseCommand.option_list + (
        make_option("-d", "--database", help="Database to restore"),
        make_option("-f", "--filepath", help="Specific file to backup from"),
        make_option("-s", "--servername", help="Use a different servername backup"),
    )

    def handle(self, **options):
        """ Django command handler. """
        try:
            connection.close()
            self.filepath = options.get('filepath')
            self.servername = options.get('servername')
            self.database = self._get_database(options)
            self.storage = BaseStorage.storage_factory()
            self.dbcommands = DBCommands(self.database)
            self.restore_backup()
        except StorageError, err:
            raise CommandError(err)

    def _get_database(self, options):
        """ Get the database to restore. """
        database_key = options.get('database')
        if not database_key:
            if len(settings.DATABASES) >= 2:
                errmsg = "Because this project contains more than one database, you"
                errmsg += " must specify the --database option."
                raise CommandError(errmsg)
            database_key = settings.DATABASES.keys()[0]
        return settings.DATABASES[database_key]

    def restore_backup(self):
        """ Restore the specified database. """
        print "Restoring backup for database: %s" % self.database['NAME']
        # Fetch the latest backup if filepath not specified
        if not self.filepath:
            print "  Finding latest backup"
            filepaths = self.storage.list_directory()
            filepaths = self.dbcommands.filter_filepaths(filepaths, self.servername)
            if not filepaths:
                raise CommandError("No backup files found in: %s" % self.storage.backup_dir())
            self.filepath = filepaths[-1]
        # Restore the specified filepath backup
        print "  Restoring: %s" % self.filepath
        input_filename = self.filepath
        inputfile = self.storage.read_file(input_filename)

        if self.get_extension(input_filename) == '.gpg':
            unencrypted_file = self.unencrypt_file(inputfile)
            inputfile.close()
            inputfile = unencrypted_file
            input_filename = inputfile.name

        if self.get_extension(input_filename) == '.gz':
            uncompressed_file = self.uncompress_file(inputfile)
            inputfile.close()
            inputfile = uncompressed_file

        print "  Restore tempfile created: %s" % utils.handle_size(inputfile)
        self.dbcommands.run_restore_commands(inputfile)

    def get_extension(self, filename):
        _, extension = os.path.splitext(filename)
        return extension

    def uncompress_file(self, inputfile):
        """ Uncompress this file using gzip.
        The input and the output are filelike objects.
        """
        outputfile = tempfile.SpooledTemporaryFile(max_size=10 * 1024 * 1024)

        zipfile = gzip.GzipFile(fileobj=inputfile, mode="rb")
        try:
            inputfile.seek(0)
            outputfile.write(zipfile.read())
        finally:
            zipfile.close()

        return outputfile

    def unencrypt_file(self, inputfile):
        """ Unencrypt this file using gpg.
        The input and the output are filelike objects.
        """
        def get_passphrase():
            print 'input passphrase:'
            return raw_input()

        import gnupg

        temp_dir = tempfile.mkdtemp()
        try:
            new_basename = os.path.basename(inputfile.name).replace('.gpg', '')
            temp_filename = os.path.join(temp_dir, new_basename)
            try:
                inputfile.seek(0)

                g = gnupg.GPG()
                result = g.decrypt_file(file=inputfile, passphrase=get_passphrase(), output=temp_filename)

                if not result:
                    raise Exception('Decryption failed; status: %s' % result.status)

                outputfile = tempfile.SpooledTemporaryFile(max_size=10 * 1024 * 1024)
                outputfile.name = new_basename

                f = open(temp_filename)
                try:
                    outputfile.write(f.read())
                finally:
                    f.close()
            finally:
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
        finally:
            os.rmdir(temp_dir)

        return outputfile