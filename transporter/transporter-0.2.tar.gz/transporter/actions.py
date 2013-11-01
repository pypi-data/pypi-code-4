import os
import pickle
import diff_match_patch
from tornado.log import app_log as logger
import logging
import errno

logger.setLevel(logging.DEBUG)


class Actions(object):
    """
    handles file action commands
    """
    def __init__(self, index, send_cmd_fn=None, remote=None):
        self.index = index
        self.send_cmd = send_cmd_fn
        self.remote = remote

    def cmd_set_name(self, name):
        self.client_name = name

    def cmd_removed_file(self, file_path, file_type):
        fpath = os.path.join(self.index.root_path, file_path)
        if os.path.exists(fpath):
            os.remove(fpath)

    def cmd_directory_created(self, file_path):
        meta = self.index.get_file_meta(file_path)
        if meta:
            # check if we have
            pass
        fpath = os.path.join(self.index.root_path, file_path)

        # TODO: check permissions...
        if os.path.exists(fpath):
            return

        try:
            os.makedirs(fpath)
        except Exception as e:
            logging.exception("exception while creating directories %s", file_path)

    def cmd_file_created(self, file_path, data, blob):
        file = self.index.get_file_meta(file_path)
        if not file:
            # everything is cool if we stll dont have the file
            # just save the file, watcher will take care of the rest
            fpath = os.path.join(self.index.root_path, file_path)

            dirpath = os.path.dirname(fpath)
            logging.debug("basepath:", dirpath)
            if not os.path.exists(dirpath):
                # sometimes we get file created first, then,
                # mkdir, so if that happens, just recovering
                # create dir with default perms.
                try:
                    os.makedirs(dirpath)
                except Exception as e:
                    logger.exception("exception while creating directories for %s", file_path)

            with open(fpath, 'w') as f:
                f.write(blob)
        else:
            if file.hash == data['hash']:
                logger.debug("same hash, ignoring.")
                return

            # houston we might have a problem...
            # we have the file but some client thinks
            # it wasnt in the index
            logger.error("client says new file but we have the file - [%s] - [%s]", file_path, data['hash'])

    def cmd_file_modified(self, file_path, data, pickled_patch):
        file = self.index.get_file_meta(file_path)
        if not file:
            # TODO: we might not have the file yet,
            # or not indexed yet... etc.
            # then we should ask the client to send us the
            # whole thing..
            pass
        else:

            if file.hash == data['hash']:
                logger.debug("same hash, ignoring.")
                return

            # we apply the patches to our local file.
            # file watcher should take care of the rest - reindexing etc..
            patches = pickle.loads(str(pickled_patch))
            fpath = os.path.join(self.index.root_path, file_path)
            with open(fpath, 'r') as f:
                data = f.read()

            with open(fpath, 'w') as f:
                dmp = diff_match_patch.diff_match_patch()
                dmp.Diff_Timeout = 0
                newdata, results = dmp.patch_apply(patches, data)
                f.write(newdata)

    def cmd_fetch_file(self, file_path, hash):
        file = self.index.get_file_meta(file_path)
        blob = self.index.get_blob(file.hash)
        assert file.hash == hash
        ret = {
                'path': file.file_path,
                'hash': file.hash,
                'revision': file.revision,
                'file_type': file.file_type,
                'link_src': file.link_src,
                'modified_at': file.modified_at,
                'blob': blob
        }
        self.send_cmd('fetch_file_reply', file_path, ret)

    def cmd_send_file_reply(self, file_path, data):
        logger.debug('saving file %s ', file_path)
        with open(os.path.join(self.index.root_path, file_path), 'w') as f:
            f.write(data['blob'])

    def cmd_send_file(self, file_path, hash):
        file = self.index.get_file_meta(file_path)
        blob = self.index.get_blob(file.hash)
        assert file.hash == hash
        ret = {
                'path': file.file_path,
                'hash': file.hash,
                'revision': file.revision,
                'file_type': file.file_type,
                'link_src': file.link_src,
                'modified_at': file.modified_at,
                'blob': blob
        }
        self.send_cmd('send_file_reply', file_path, ret)

    def cmd_fetch_file_reply(self, file_path, data):
        logger.debug('saving file %s ', file_path)
        meta = self.index.get_file_meta(file_path)
        if not meta:
            realpath = os.path.join(self.index.root_path, file_path)

            if not os.path.exists(os.path.split(realpath)[0]):
                print "trying to create directory", os.path.split(realpath)[0]
                try:
                    os.makedirs(realpath)
                except OSError as exc:
                    if exc.errno == errno.EEXIST and os.path.isdir(realpath):
                        pass
                    else:
                        print "exception while creating directory", exc

            with open(realpath, 'w') as f:
                f.write(data['blob'])
        else:
            # do a merge operation...
            patches = self.index.update_file(file_path, data['blob'])
            fpath = os.path.join(self.index.root_path, file_path)
            with open(fpath, 'r') as f:
                data = f.read()

            with open(fpath, 'w') as f:
                dmp = diff_match_patch.diff_match_patch()
                dmp.Diff_Timeout = 0
                newdata, results = dmp.patch_apply(patches, data)
                f.write(newdata)


    def cmd_sync_files(self, files):
        self.index.sync_files(files, self.remote)

    def cmd_get_file_list(self):
        files = self.index.files()
        ret = []
        for file in files:
            ret.append({
                'path': file.file_path,
                'hash': file.hash,
                'revision': file.revision,
                'file_type': file.file_type,
                'link_src': file.link_src,
                'modified_at': file.modified_at
            })
        self.send_cmd('file_list',  ret)
