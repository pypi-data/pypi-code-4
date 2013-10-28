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
    >>> relative_path("/foo", "/foo/foobar")
    foo/foobar
    >>> relative_path("/foo/", "/foo/foobar")
    foo/foobar
    """
    #return os.path.relpath(file_path, path)
    p = file_path.replace(path, '')
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

def insert_to_sqlite(cursor, table, **kwargs):
    """
        creates and executes an sql query with kwargs

        usage:
        insert_to_sqlite(cur, "files", file_path='foo', file_hash='f')
        will execute
        cursor.execute("insert into files(file_path, file_hash) values(?, ?)", ('foo', 'f'))
        so its just syntatic sugar
    """
    query_params = []
    values = []
    qmarks = []
    for k, v in kwargs.iteritems():
        query_params.append(k)
        values.append(v)
        qmarks.append('?')

    query = "insert into %s(%s) values (%s)" % (table, ','.join(query_params), ','.join(qmarks) )
    cursor.execute(query, tuple(values))

def normalize_file_path(file_path):
    if on_windows:
        return file_path.replace(os.path.sep, '/')
    return file_path


class SyncIndex(object):

    def __init__(self, path):
        self.ignore_rules = []
        self.root_path = path
        self.cache_path = os.path.join(self.root_path, '.kd-cache')
        self.exclude_paths = ['.kd-cache']
        self.blobs_root = os.path.join(self.root_path, '.kd-cache', 'blobs')
        self.load_ignore_rules()
        self.build()

    def can_ignore(self, path):
        for rule in self.ignore_rules:
            if matcher.matches(self.relpath(path), rule):
                return True

    def load_ignore_rules(self):
        p = os.path.join(self.root_path, '.kd-ignore')
        if os.path.exists(p):
            with open(p) as f:
                self.ignore_rules = matcher.parse_ignore_file(f.readlines())


    def relpath(self, file_path):
        return relative_path(self.root_path, file_path)

    def file_exists_in_db(self, file_path, file_type):
        cur = self.db.cursor()
        cur.execute("""
            select * from files where file_path=? and file_type=? limit 1
        """, (normalize_file_path(file_path), file_type))
        row = cur.fetchone()
        if row:
            return row
        return None

    def save_blob(self, hash, blob):
        """
        saves file contents to .kd-cache/blobs/ directory
        """
        blobdir = os.path.join(self.blobs_root, hash[0:2])
        if not os.path.exists(blobdir):
            os.mkdir(blobdir)

        with open(os.path.join(self.blobs_root, hash[0:2], hash), 'w') as f:
            f.write(zlib.compress(blob))

    def add_file_to_db(self, file_path, file_type, hash, operation='create',
                             link_src=None, blob=None, diff=None, modified_at=None):
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

        now = datetime.datetime.utcnow()
        if file_type == 'f':
            assert blob is not None or diff is not None
        
        latest_revision = 0

        cur = self.db.cursor()
        filemeta = self.get_file_meta(file_path)
        if filemeta:

            if file_type == 'f':
                if filemeta['hash'] == hash:
                    # nothing has changed...
                    return
            elif file_type == 'd':
                # we have it already on db, so just pass
                return
            cur.execute('''
                update files set hash=?, revision=revision+1, modified_at=?, is_deleted=0
                where file_path=?
            ''', (hash, modified_at, file_path))
            cur.execute('''
                select revision from files where file_path=?
            ''', (file_path,))
            row = cur.fetchone()
            latest_revision = row['revision']
        else:
            insert_to_sqlite(cur, "files", file_path=file_path, 
                                    file_type=file_type, 
                                    hash=hash, 
                                    revision=0, 
                                    created_at=now, 
                                    modified_at=now )

        if blob:
            self.save_blob(hash, blob)

        insert_to_sqlite(cur, 'revisions', file_path=file_path, 
                                file_type=file_type, 
                                hash=hash, 
                                revision=latest_revision, 
                                operation=operation, 
                                created_at=now,
                                diff=diff, 
                                modified_at=now)
        self.db.commit()

    def get_blob(self, hash, unzip=True):
        p = os.path.join(self.blobs_root, hash[0:2], hash)
        if not os.path.exists(p):
            return None
        f = open(p, 'r')
        zipped = f.read()
        if unzip:
            return zlib.decompress(zipped)
        else:
            return zipped

    def get_file_contents(self, file_path, unzip=True):
        cur = self.db.cursor()
        cur.execute("""
            select * from files where file_path=? and file_type=? limit 1
        """, (file_path, 'f'))
        row = cur.fetchone()
        if row:
            return self.get_blob(row['hash'], unzip)

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
        self.add_file_to_db(normalized_file_path, 'f', githash(content), blob=content,
                            operation='update', 
                            diff=pickled_diffs,
                            modified_at=modified_at)
        return diffs

    def add_file(self, file_path, diff_or_blob='blob'):
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
        cur = self.db.cursor()
        filemeta = self.get_file_meta(file_path, file_type)
        if filemeta:
            now = datetime.datetime.utcnow()
            cur.execute('''
                update files set is_deleted=1, revision=revision+1, modified_at=?
                where file_path=? and file_type=?
            ''', (now, file_path, file_type))

            insert_to_sqlite(cur, 'revisions',
                                    file_path=file_path,
                                    file_type=file_type,
                                    operation='delete',
                                    created_at=now,
                                    modified_at=now)
            self.db.commit()

    def get_file_meta(self, file_path, file_type='f'):
        cur = self.db.cursor()
        cur.execute('''select * from files where file_path=? and file_type=? and is_deleted=0''', (normalize_file_path(file_path), file_type))
        row = cur.fetchone()
        return row

    def files(self):
        cur = self.db.cursor()
        cur.execute('''select * from files where is_deleted=0 order by file_path''')
        rows = cur.fetchall()
        return rows

    def file_history(self, file_path):
        cur = self.db.cursor()
        cur.execute('''select * from revisions where file_path=?''', (normalize_file_path(file_path),) )
        rows = cur.fetchall()
        return rows

    def build(self):
        if not os.path.exists(self.cache_path):
            os.mkdir(self.cache_path)

        if not os.path.exists(self.blobs_root):
            os.mkdir(self.blobs_root)

        self.db = self.connect_to_db()

        path = self.root_path
        for root, dirs, files in os.walk(path):
            for exclude_path in self.exclude_paths:
                if exclude_path in dirs:
                    dirs.remove(exclude_path)

            for d in dirs:
                rpath = relative_path(path, os.path.join(path, root, d))
                self.add_file(rpath)

            for f in files:
                rpath = relative_path(path, os.path.join(path, root, f))
                self.add_file(rpath)

    def initialize_tables(self, db):
        cur = db.cursor()
        cur.execute("""CREATE TABLE FILES(id INTEGER PRIMARY KEY, 
                       file_path TEXT, file_type char, 
                       hash text, revision int default 0, 
                       link_src text,
                       created_at datetime, modified_at datetime,
                       is_deleted integer default 0
                       )""")

        cur.execute("""
                    CREATE TABLE REVISIONS(id INTEGER PRIMARY KEY,
                        file_path TEXT, file_type char, hash text, 
                        created_at datetime, modified_at datetime,
                        operation text,
                        diff text,
                        revision integer
                    )
                    """)
        cur.execute('''create index ndx_revisions_file_path on REVISIONS(file_path) ''')
        cur.execute('''create index ndx_files_file_path on files(file_path) ''')
        db.commit()


    def connect_to_db(self):
        p = os.path.join(self.root_path, '.kd-cache', 'files.db')
        con = sqlite3.connect(p, detect_types=sqlite3.PARSE_DECLTYPES)
        con.row_factory = sqlite3.Row
        try:
            con.execute('select * from FILES limit 1')
        except sqlite3.OperationalError as e:
            if 'no such table' in e.message:
                self.initialize_tables(con)
            else:
                raise
        return con

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
                        raise

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
                    if (meta['modified_at'] >= f['modified_at']):
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

if __name__ == '__main__':
    path = sys.argv[1]
    
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    index = SyncIndex(path)
    index.build()