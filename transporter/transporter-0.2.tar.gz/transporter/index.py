"""
this creates an index folder named .kd-cache in the folder list

currently it uses sqlite3 to build up the path of files. this might
change in the future but for now, its easy

we have 2 tables in schema:

    files
        id

    revisions
        file_path -> files.file_path 


"""
import os
import sys
import logging
import zlib
import datetime
import diff_match_patch
import cPickle as pickle
import errno
from hashlib import sha1
import matcher
import platform

on_windows = platform.system() == 'Windows'

try:
    import sqlite3
except:
    print "you need to install sqlite3 module, please refer to docs"
    raise


def githash(data):
    s = sha1()
    s.update("blob %u\0" % len(data))
    s.update(data)
    return s.hexdigest()

def githash_file(path):
    """
    returns githash of file and contents of file 
    """
    with open(path, 'r') as f:
        data = f.read()
        h = githash(data)
    return h, data

def relative_path(path, file_path):
    """
    returns relative path of the file to file_path
    >>> relative_path("/foo/", "/foo/foo/foobar")
    'foo/foobar'
    >>> relative_path("/foo/", "/foo/foobar")
    'foobar'
    """
    p = file_path.replace(path, '', 1)
    if not (len(p) > 0):
        raise Exception('relative path problem - [%s],[%s] ' % (path, file_path))

    if p[0] == os.path.sep:
        return p[1:]
    else:
        return p

def file_type(path):
    if os.path.islink(path):
        return 'l'
    if os.path.isdir(path):
        return 'd'
    if os.path.isfile(path):
        return 'f'

def normalize_file_path(file_path):
    if on_windows:
        return file_path.replace(os.path.sep, '/')
    return file_path

from dbo import DBObject, Column, Database

class Revision(DBObject):
    __tablename__ = 'revisions'
    columns = {
        'id': Column('integer', primary=True),
        'file_path': Column('text', index=True),
        'file_type': Column('char'),
        'hash': Column('text'),
        'created_at': Column('datetime'),
        'modified_at': Column('datetime'),
        'operation': Column('text'),
        'from_hash': Column('text'),
        'to_hash': Column('text'),
        'from_permissions': Column('int'),
        'to_permissions': Column('int'),
        'diff': Column('text'),
        'revision': Column('integer')
    }

class File(DBObject):

    __tablename__ = 'files'

    columns = {
        'id': Column('integer', primary=True),
        'file_path': Column('text', index=True),
        'file_type': Column('char'),
        'hash': Column('text'),
        'revision': Column('int', default=0),
        'link_src': Column('text'),
        'created_at': Column('datetime'),
        'permissions': Column('int'),
        'modified_at': Column('datetime'),
        'is_deleted': Column('integer', default=0)
    }

    def add_revision(self, operation, **kwargs):
        if 'diff' in kwargs:
            diff = kwargs['diff']
        else:
            diff = None

        r = Revision(file_path=self.file_path,
                     file_type=self.file_type,
                     from_hash=self.hash,
                     hash=self.hash,
                     revision=self.revision,
                     operation=operation,
                     created_at=kwargs['modified_at'],
                     diff=diff,
                     modified_at=kwargs['created_at'])
        return r

class SyncIndex(object):

    def __init__(self, path):
        self.ignore_rules = ['.kd-cache/']
        self.root_path = path
        self.cache_path = os.path.join(self.root_path, '.kd-cache')
        self.blobs_root = os.path.join(self.root_path, '.kd-cache', 'blobs')
        self.load_ignore_rules()
        self.build()

    def can_ignore(self, path):

        if (path == self.root_path):
            return True

        for rule in self.ignore_rules:
            if matcher.matches(self.relpath(path), rule):
                return True

    def load_ignore_rules(self):
        p = os.path.join(self.root_path, '.kd-ignore')
        if os.path.exists(p):
            with open(p) as f:
                self.ignore_rules += matcher.parse_ignore_file(f.readlines())
        self.ignore_rules += '.kd-cache/'

    def relpath(self, file_path):
        return relative_path(self.root_path, file_path)

    def save_blob(self, hash, blob):
        """
        saves file contents to .kd-cache/blobs/ directory
        """
        blobdir = os.path.join(self.blobs_root, hash[0:2])
        if not os.path.exists(blobdir):
            os.mkdir(blobdir)

        with open(os.path.join(self.blobs_root, hash[0:2], hash), 'wb') as f:
            f.write(zlib.compress(blob))


    def add_file_to_db(self, file_path, file_type, hash, operation='create',
                             link_src=None, blob=None, diff=None,
                             modified_at=None):
        """
            adds file to files table in db

            :param file_path: files relative path
            :param file_type: char l, f, d
            :param hash: if its file githash of file 
            :param link_src: if its link, link's source

            :param blob: contents of the file
            :param diff: diff of the file from the latest revision
            :param operation: create, modify, delete

        """

        logging.debug("add file to db [%s]", file_path)

        if self.can_ignore(file_path):
            logging.debug("ignoring file because of ignore rules")
            return

        now = datetime.datetime.utcnow()
        if file_type == 'f':
            assert blob is not None or diff is not None
        
        filemeta = self.get_file_meta(file_path)
        if filemeta:
            # update operation...
            if file_type == 'f':
                if filemeta.hash == hash:
                    # nothing has changed...
                    return
            elif file_type == 'd':
                # we have it already on db, so just pass
                return
            with self.database.context() as db:
                filemeta.hash = hash
                filemeta.revision = filemeta.revision+1
                filemeta.modified_at = modified_at
                filemeta.is_deleted = 0
                revision = filemeta.add_revision(operation, created_at=now, modified_at=now, diff=None)
                db.add(filemeta)
                db.add(revision)
                db.save()
        else:
            # insert operation
            with self.database.context() as db:
                f = File(file_path=file_path, file_type=file_type, hash=hash, revision=0, created_at=now,
                         modified_at=now)
                revision = f.add_revision(operation, created_at=now, modified_at=now, diff=diff)
                db.add(f)
                db.add(revision)
                db.save()

        if blob:
            self.save_blob(hash, blob)

    def get_blob(self, hash, unzip=True):
        p = os.path.join(self.blobs_root, hash[0:2], hash)
        if not os.path.exists(p):
            return None
        f = open(p, 'rb')
        zipped = f.read()
        if unzip:
            return zlib.decompress(zipped)
        else:
            return zipped

    def get_file_contents(self, file_path, unzip=True):
        f = self.database.get(File, file_path=file_path, file_type='f')
        if f:
            return self.get_blob(f.hash, unzip)

    def update_with_file_path(self, file_path):
        with open(os.path.join(self.root_path, file_path), 'r') as f:
            patches = self.update_file(file_path, f.read())
            return patches

    def update_file(self, file_path, content):
        """
            when we update a file, we save the content in a new blob,
            insert diff in a new revision row
            and update files hash

            :return patches
        """
        normalized_file_path = normalize_file_path(file_path)
        oldcontent = self.get_file_contents(normalized_file_path)
        if not oldcontent:
            raise Exception("not found %s" % file_path)

        if oldcontent == content:
            return

        dmp = diff_match_patch.diff_match_patch()
        dmp.Diff_Timeout = 0
        diffs = dmp.patch_make(oldcontent, content)
        pickled_diffs = pickle.dumps(diffs)
        logging.debug("updating file %s to hash:%s", normalized_file_path, githash(content))
        real_path = os.path.join(self.root_path, file_path)
        modified_at = os.path.getmtime(real_path)

        self.add_file_to_db(normalized_file_path, 'f', githash(content),
                            blob=content,
                            operation='update', 
                            diff=pickled_diffs,
                            modified_at=modified_at)
        return diffs

    def add_file(self, file_path):
        """
            add file to database, when its created
        """
        logging.debug("adding file %s - [%s]", file_path, normalize_file_path(file_path))
        p = os.path.join(self.root_path, file_path)
        t = file_type(p)
        if t == 'f':
            filehash, data = githash_file(p)
            self.add_file_to_db(normalize_file_path(file_path), t, filehash,
                    operation='create',
                    blob=data                    
                )
            return filehash, data
        elif t == 'l':
            self.add_file_to_db(normalize_file_path(file_path), t, hash=None,
                                link_src=os.readlink(os.path.join(self.root_path, file_path)),
                                operation='create')
        elif t == 'd':
            self.add_file_to_db(normalize_file_path(file_path), t, hash=None,
                                operation='create')
        else:
            raise Exception("unknown file type")

    def remove_file(self, file_path, file_type):
        f = self.get_file_meta(file_path, file_type)
        if f:
            now = datetime.datetime.utcnow()
            with self.database.context() as db:
                f.is_deleted = 1
                f.revision = f.revision + 1
                f.modified_at = now
                revision = f.add_revision("delete", created_at=now, modified_at=now)
                db.add(f)
                db.add(revision)
                db.save()

    def get_file_meta(self, file_path, file_type='f'):
        return self.database.get(File, file_path=normalize_file_path(file_path), file_type=file_type)

    def files(self):
        return self.database.get_all(File, is_deleted=0, order_by='file_path')

    def file_history(self, file_path):
        return self.database.get_all(Revision, file_path=file_path)

    def build(self):
        if not os.path.exists(self.cache_path):
            os.mkdir(self.cache_path)

        if not os.path.exists(self.blobs_root):
            os.mkdir(self.blobs_root)

        self.connect_to_db()

        path = self.root_path
        for root, dirs, files in os.walk(path):
            for d in dirs:
                rpath = relative_path(path, os.path.join(path, root, d))
                if not self.can_ignore(rpath + os.path.sep):
                    self.add_file(rpath)

            for f in files:
                rpath = relative_path(path, os.path.join(path, root, f))
                if not self.can_ignore(rpath):
                    self.add_file(rpath)

    def connect_to_db(self):
        p = os.path.join(self.root_path, '.kd-cache', 'files.db')
        self.database = Database(path=p, models=[File, Revision])

    def sync_files(self, files, remote):
        '''
        tries to sync file list on the local repo,
        we do this by looking at utc timestamps of the file to see
        which one is newer.

        :param files: list of file properties
        :param remote: instance of RemoteIndex

        there are a couple of different situations,

        file doesnt exist on local:
            best scenerio, we just put the file

        file newer than local:
            request patch

        file older than local:
            ignore, we'll sync in reverse direction later

        file deleted on the otherside, but we have it existing:
            if file delete operation is newer than the local mtime,
            we delete the file

        file deleted on local, but we have it existing on remote:
            if file mod. time on the other side is newer than
            our local deletion time, we fetch the file

        '''
        # we first split file list to types...
        directories = []
        links = []
        blobs = []

        for f in files:
            if f['file_type'] == 'f':
                blobs.append(f)
            elif f['file_type'] == 'l':
                links.append(f)
            elif f['file_type'] == 'd':
                directories.append(f)

        for d in directories:
            meta = self.get_file_meta(d['path'])
            print ">>>", meta
            if not meta:
                # great we never seen that directory, 
                # so lets create it...
                logging.debug("creating directory %s", d['path'])
                try:
                    os.makedirs(os.path.join(self.root_path, d['path']))
                except OSError as exc: 
                    if exc.errno == errno.EEXIST and os.path.isdir(d['path']):
                        pass
                    else: 
                        print "exception while creating directory", exc

        for f in blobs:
            logging.debug("checking if we have path %s", f['path'])
            if f['file_type'] == 'f':
                meta = self.get_file_meta(f['path'])
                print ">>>> meta:", meta
                if not meta:
                    # best scenerio, we never had that file
                    # just download and save...
                    remote.fetch_file(f['path'], f['hash'])
                else:
                    # now the file we have might be newer on our side,
                    # or might be deleted
                    # so we have to check the timestamps and decide what to do
                    if (meta.modified_at >= f['modified_at']):
                        # ours is newer, nothing to do, it will
                        # create a patch on the other side and apply
                        pass
                    else:
                        # theirs is newer, now we have to create a patch
                        # and apply to ourselves.
                        pass


        for l in links:
            # TODO: check links...
            pass


class RemoteIndex(object):
    '''
    interface...
    '''
    def __init__(self):
        pass

    def fetch_file(self, path):
        pass

    def updated_local_file(self, file_path, data, patch):
        pass

#if __name__ == '__main__':
#    path = sys.argv[1]
#
#    logging.basicConfig(level=logging.DEBUG,
#                        format='%(asctime)s - %(message)s',
#                        datefmt='%Y-%m-%d %H:%M:%S')
#
#    index = SyncIndex(path)
#    index.build()