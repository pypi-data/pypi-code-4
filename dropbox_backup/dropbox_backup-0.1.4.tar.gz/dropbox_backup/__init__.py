"""Dropbox Backup

Usage:
  dropbox_backup create [--backup-path=/home/backups] [--token=] [--mysql] [<name:path>]...
  dropbox_backup upload [--backup-path=/home/backups] [--token=]
  dropbox_backup (-h | --help)
  dropbox_backup --version

Options:
  -h --help             Show this screen.
  --version             Show version.

  --backup-path=PATH    Path where backups are stored.
  --token=TOKEN         Dropbox token used to upload files.
  --mysql               Create a mysql backup.

"""

import json, os, requests, re
import ConfigParser
from docopt import docopt

from dropbox_backup import settings
from dropbox_backup.utils import filesizeformat, md5_checksum, get_config_option

# Get version
import pkg_resources
__version__ = pkg_resources.require("dropbox_backup")[0].version

# -----------------------------------------------------------------------------

# [general]
# backup_path=/home/backups
# backup=true
# dropbox_token=yJ4zQ9g4-cIAAAAAAAAAATS8xnCF1iRqn9cKOJ7icif7tCRzWANQ1J65naspOhDh

# [backup_packs]
# git:/home/git/repositories
# nginx:/etc/nginx
# minecraft:/home/minecraft

def main():
    arguments = docopt(__doc__, version=__version__)

    backup_path = arguments['--backup-path'] if arguments['--backup-path'] else settings.BACKUP_PATH
    token = arguments['--token'] if arguments['--token'] else None
    mysql = True if arguments['--mysql'] else False
    packs = [group.split(':') for group in arguments['<name:path>']] if len(arguments['<name:path>']) > 0 else None

    if os.path.exists(settings.CONF_FILE):
        config = ConfigParser.RawConfigParser()
        config.read(settings.CONF_FILE)

        backup_path = get_config_option(config, 'general', 'backup_path', fallback=backup_path)
        token = get_config_option(config, 'general', 'dropbox_token', fallback=token)
        mysql = get_config_option(config, 'general', 'mysql', fallback=mysql)
        packs = get_config_option(config, 'backup_packs', fallback=packs)

    if token is None or packs is None:
        raise Exception('Unable to find token or <name:path>')

    if (arguments['create']): # Create action
        backup_manager = BackupManager(backup_path=backup_path, packs=packs, mysql=mysql)
        backup_manager.process_packs()
    elif (arguments['upload']): # Create upload
        uploader = DropboxUploader(backup_path=backup_path, token=token)
        uploader.upload_packs()

# -----------------------------------------------------------------------------

class BackupManager(object):
    def __init__(self, backup_path, packs, mysql):
        self.backup_path = backup_path
        self.packs = packs
        self.mysql = mysql

    def process_packs(self):
        os.chdir(self.backup_path)

        for name, path in self.packs:
            file_name = "%s.tar.gz" % name
            if name and path:
                print "\tmaking pack for %s..." % path
                os.system('sudo tar -c %s 2> /dev/null | gzip -n9 > %s' % (path, os.path.join(self.backup_path, file_name)))

        if self.mysql:
            file_name = "mysql.sql"
            os.system('mysqldump --all-databases 2> /dev/null > %s' % os.path.join('/tmp', file_name))
            os.system('gzip -n9 %s > %s' % (os.path.join('/tmp', file_name), os.path.join(self.backup_path, "%s.gz" % file_name)))

class DropboxUploader(object):
    def __init__(self, backup_path, token):
        self.backup_path = backup_path
        self.token = token

    def sign(self):
        return {"Authorization": "Bearer %s" % self.token}

    def upload_packs(self):
        # MD5 checksum
        md5_checksum_file_path = os.path.join(self.backup_path, ".md5_checksum.json")
        if os.path.exists(md5_checksum_file_path):
            md5_fp = open(md5_checksum_file_path, "r")
            md5_data = json.load(md5_fp)
            md5_fp.close()
        else:
            md5_data = {}

        md5_new_data = {}
        for file in os.listdir(self.backup_path):
            file_path = os.path.join(self.backup_path, file)
            md5_new_data[file] = md5_checksum(file_path)

        # Upload files
        for file in os.listdir(self.backup_path):
            if not re.match(r'^.*\.tar\.gz$', file):
                continue
            if md5_data.get(file) != md5_new_data[file]:
                print "\tuploading %s..." % file
                md5_data[file] = md5_new_data[file]
                file_path = os.path.join(self.backup_path, file)
                self.upload_file(file_path)
            else:
                print "\tno change for %s" % file

        # Rewrite MD5 file
        md5_fp = open(md5_checksum_file_path, "w+")
        md5_fp.write(json.dumps(md5_data, indent=2, sort_keys=True))
        md5_fp.close()

    def upload_file(self, file_path):
        f = open(file_path, "rb")
        size = os.stat(file_path).st_size

        chunk = f.read(settings.CHUNK_SIZE)
        r = requests.put("%s/chunked_upload" % settings.DROPBOX_CONTENT_URL, data=chunk, headers=self.sign())
        data = json.loads(r.text)
        upload_id = data.get("upload_id")
        offset = data.get("offset")
        self.print_state(offset, size)

        while(True):
            f.seek(offset)
            chunk = f.read(settings.CHUNK_SIZE)

            r = requests.put("%s/chunked_upload" % settings.DROPBOX_CONTENT_URL, params={"upload_id": upload_id, "offset": offset}, data=chunk, headers=self.sign())
            data = json.loads(r.text)
            offset = data.get("offset")

            self.print_state(offset, size)
            if offset == size:
                break

        r = requests.post(
            "%s/commit_chunked_upload/sandbox/%s" % (settings.DROPBOX_CONTENT_URL, file_path.split('/')[-1]),
            params={
                "upload_id": upload_id,
                "overwrite": True,
            },
            headers=self.sign())

        f.close()

    def print_state(self, offset, size):
        # print "%s / %s" % (filesizeformat(offset), filesizeformat(size))
        pass
