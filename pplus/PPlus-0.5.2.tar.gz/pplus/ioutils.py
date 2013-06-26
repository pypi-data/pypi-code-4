"""File System related utilities (caching and configuration file parsing)."""

# Author: Salvatore Masecchia <salvatore.masecchia@disi.unige.it>,
#         Grzegorz Zycinski <grzegorz.zycinski@disi.unige.it>
# License: new BSD.

import os
import tempfile
import shutil


def read_config_file(config_file_path):
    """Reads configuration file and returns a dictionary representation.

    For each 'section' and for each 'option' the resulting dictionary
    contain the read value mapped with the key 'SECTION.OPTION'.

    """
    import ConfigParser
    cp = ConfigParser.SafeConfigParser()
    with open(config_file_path, 'r') as cfl:
        cp.readfp(cfl)

    config_options = {}
    for s in cp.sections():
        for o in cp.options(s):
            key = "%s.%s" % (s.upper(), o.upper())
            config_options[key] = cp.get(s, o)

    return config_options


## Local Cache utils --
class PPlusTemporaryCachedFile(object):

    def __init__(self, pc, key, mode, buffering, overwrite):
        """Temporary writable cached file.

        An instance of this class is returned by the
        :meth:`pplus.PPlusConnection.write_remotely` method.

        The class wraps a standard temporary file opened in the local cache.
        The user code may use it as a standard file object (even in a ``with``
        statement) which will be transferred on the shared disk when closed.

        Parameters
        ----------
        pc : PPlusConnection object
            instance of PPlusConnection
        key : str
            identifier of the file to use when transferred on shared disk
        mode : str, ['wb', 'w']
            file mode, 'b' means binary mode. The mode is not checked, because
            it is correctly passed by :class:`pplus.PPlusConnection`
        buffering : int
            buffer size to use while opening file.
        overwrite : bool
            if True, overwrite any existing remote file already associated
            with 'key' silently; otherwise, raise an error
            Check is done only during transferring.

        """

        self._fobj = tempfile.NamedTemporaryFile(mode=mode,
                                                 bufsize=buffering,
                                                 dir=pc.cache_path,
                                                 delete=False)
        self._pc = pc
        self._key = key
        self._overwrite = overwrite

    def __iter__(self):
        return self._fobj.__iter__()

    def __getattr__(self, attr):
        return getattr(self._fobj, attr)

    def __enter__(self):
        return self._fobj.__enter__()

    def __exit__(self, type, value, traceback):
        out = self._fobj.__exit__(type, value, traceback)
        self._transfer()
        return out

    def close(self):
        out = self._fobj.close()
        self._transfer()
        return out

    def _transfer(self):
        self._pc.put(self._key, self._fobj.name, self._overwrite)
        remove_if_exists(self._fobj.name)


def copy_if_not_exists(src_path, dst_path, clean=True):
    """Copy ``src_path`` to ``dst_path`` only if the latter does not exist.

    ``clean`` parameters refers to the cache mutex status.
    """
    if not clean:
        remove_if_exists(dst_path)
    if not os.path.exists(dst_path):
        shutil.copyfile(src_path, dst_path)


def remove_if_exists(file_path, clean=True):
    """Remove ``file_path`` from the local cache.

    ``clean`` parameters refers to the cache mutex status.
    """
    # clean is unused, but need to be here for the locking protocol
    if os.path.exists(file_path):
        os.remove(file_path)


def create_local_experiment_dirs(path, clean=True):
    """Create local cache directories structure having ``path`` as root.

    ``clean`` parameters refers to the cache mutex status.
    """
    if not clean and os.path.exists(path):
        shutil.rmtree(path)
    if not os.path.exists(path):
        os.mkdir(path)
        os.chmod(path, 0777)
        os.mkdir(os.path.join(path, 'logs'))
        os.chmod(os.path.join(path, 'logs'), 0777)
    # mode 0777 for local (master node) and pplus (workers) user.. mandatory?
