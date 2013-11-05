import os
import mimetypes
import gzip
import tempfile
import shutil
import re

from boto.s3.connection import S3Connection
from boto.s3.key import Key

excludes = r'|'.join([r'.*\.git$'])


class S3Sync:
    def __init__(self, directory, force, bucket, key_id, key):
        self.force = force
        self.connection = S3Connection(key_id, key)
        self.bucketname = bucket
        self.bucket = self.connection.get_bucket(bucket)
        self.directory = directory.rstrip('/')

    def deploy_to_s3(self):
        """
        Deploy a directory to an s3 bucket using parallel uploads.
        """
        self.tempdir = tempfile.mkdtemp('s3deploy')

        for keyname, absolute_path in self.find_file_paths():
            self.s3_upload(keyname, absolute_path)

        shutil.rmtree(self.tempdir, True)
        return True

    def s3_upload(self, keyname, absolute_path):
        """
        Upload a file to s3
        """
        mimetype = mimetypes.guess_type(absolute_path)
        options = {'Content-Type': mimetype[0]}

        if mimetype[0] is not None and mimetype[0].startswith('text/'):
            upload = open(absolute_path)
            options['Content-Encoding'] = 'gzip'
            key_parts = keyname.split('/')
            filename = key_parts.pop()
            temp_path = os.path.join(self.tempdir, filename)
            gzfile = gzip.open(temp_path, 'wb')
            gzfile.write(upload.read())
            gzfile.close()
            absolute_path = temp_path

        size = os.path.getsize(absolute_path)
        existing = self.bucket.get_key(keyname)

        if self.force or not existing or (existing.size != size):
            k = Key(self.bucket)
            k.key = keyname
            print "Uploading %s" % keyname
            k.set_contents_from_filename(absolute_path, options, policy='public-read')
        else:
            print "Skipping %s, file sizes match" % keyname

    def find_file_paths(self):
        """
        A generator function that recursively finds all files in the upload directory.
        """
        paths = []
        for root, dirs, files in os.walk(self.directory, topdown=True):
            dirs[:] = [d for d in dirs if not re.match(excludes, d)]
            rel_path = os.path.relpath(root, self.directory)

            for f in files:
                if f.startswith('.') or f.startswith('_'):
                    continue
                if rel_path == '.':
                    paths.append((f, os.path.join(root, f)))
                else:
                    paths.append((os.path.join(rel_path, f), os.path.join(root, f)))

        return paths
