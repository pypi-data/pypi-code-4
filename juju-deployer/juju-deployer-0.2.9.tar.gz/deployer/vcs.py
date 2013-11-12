import subprocess
import os

from bzrlib.workingtree import WorkingTree

from .utils import ErrorExit


class Vcs(object):

    err_update = (
        "Could not update branch %(path)s from %(branch_url)s\n\n %(output)s")
    err_branch = "Could not branch %(branch_url)s to %(path)s\n\n %(output)s"
    err_is_mod = "Couldn't determine if %(path)s was modified\n\n %(output)s"
    err_pull = (
        "Could not pull branch @ %(branch_url)s to %(path)s\n\n %(output)s")
    err_cur_rev = (
        "Could not determine current revision %(path)s\n\n %(output)s")

    def __init__(self, path, origin, log):
        self.path = path
        self.log = log
        self.origin = origin

    def _call(self, args, error_msg, cwd=None, stderr=()):
        try:
            stderr = stderr is None and stderr or subprocess.STDOUT
            output = subprocess.check_output(
                args, cwd=cwd or self.path, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            #print "vcs err", " ".join(args), "[dir: %s]" % cwd
            self.log.error(error_msg % self.get_err_msg_ctx(e))
            raise ErrorExit()
        return output.strip()

    def get_err_msg_ctx(self, e):
        return {
            'path': self.path,
            'branch_url': self.origin,
            'exit_code': e.returncode,
            'output': e.output,
            'vcs': self.__class__.__name__.lower()}

    def get_cur_rev(self):
        raise NotImplementedError()

    def update(self, rev=None):
        raise NotImplementedError()

    def branch(self):
        raise NotImplementedError()

    def pull(self):
        raise NotImplementedError()

    def is_modified(self):
        raise NotImplementedError()

    # upstream missing revisions?


class Bzr(Vcs):

    def get_cur_rev(self):
        params = ["bzr", "revno", "--tree"]
        return self._call(params, self.err_cur_rev)

    def update(self, rev=None):
        params = ["bzr", "up"]
        if rev:
            params.extend(["-r", str(rev)])
        self._call(params, self.err_update)

    def pull(self):
        params = ["bzr", "pull", "--remember", self.origin]
        self._call(params, self.err_pull)

    def branch(self):
        params = ["bzr", "branch", self.origin, self.path]
        cwd = os.path.dirname(os.path.dirname(self.path))
        if not cwd:
            cwd = "."
        self._call(params, self.err_branch, cwd)

    def is_modified(self):
        # To replace with bzr cli, we need to be able to detect
        # changes to a wc @ a rev or @ trunk.
        tree = WorkingTree.open(self.path)
        return tree.has_changes()


class Git(Vcs):

    def get_cur_rev(self):
        params = ["git", "rev-parse", "HEAD"]
        return self._call(params, self.err_cur_rev)

    def update(self, rev=None):
        params = ["git", "reset", "--merge"]
        if rev:
            params.append(rev)
        self._call(params, self.err_update)

    def pull(self):
        params = ["git", "pull", "master"]
        self._call(params, self.err_pull)

    def branch(self):
        params = ["git", "clone", self.branch]
        self._call(params, self.err_branch, os.path.dirname(self.path))

    def is_modified(self):
        params = ["git", "stat", "-s"]
        return bool(self._call(params, self.err_is_mod).strip())

    def get_origin(self):
        params = ["git", "config", "--get", "remote.origin.url"]
        return self._call(params, "")
