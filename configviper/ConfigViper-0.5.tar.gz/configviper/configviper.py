# -*- coding: utf-8 -*-
#
# src/configviper/configviper.py
# https://bitbucket.org/danielgoncalves/configviper
#
# ConfigViper  Copyright (C) 2012  Daniel Gonçalves <daniel@base4.com.br>
#
# This file is part of ConfigViper.
#
# ConfigViper is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as 
# published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.
#
# ConfigViper is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ConfigViper. If not, see <http://www.gnu.org/licenses/>.
#

import codecs
import hashlib
import json
import logging
import os
import pprint
import shutil
import socket
import threading
import warnings

import converters
from lockfile import lockfile


try:
    from logging import NullHandler
except ImportError:
    # keeps Python 2.6 working
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

ROOT_LOGGER = 'configviper'

logging.getLogger(ROOT_LOGGER).addHandler(NullHandler())


class PathOverrun(Exception):
    """This exception will be raised by :meth:`~ConfigViper.set` method when a
    config-path overrun an existing config-path that points to a value other
    than a dict (or *object* in JSON lingo). For example, consider the
    following Python dictionary::

        >>> d = { 'a': { 'b': 1 } } # "a.b" = 1 (int)

    If you try to overrun "b" with an aditional "c", you'll got a 
    ``PathOverrun`` exception, like this::

        >>> conf = ConfigViper()
        >>> conf.set('a.b', 1)
        >>> conf.get('a.b')
        1
        >>> conf.set('a.b.c', 2)
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "configviper.py", line 137, in set
            'value.' % path)
        configviper.PathOverrun: '"a.b.c" config-path segment overrun an existing value.'

    """

    def __init__(self, value):
        self.value = value


    def __str__(self):
        return repr(self.value)


class ProxyProperty(object):
    """A proxy support for access configuration paths as object attributes."""

    def __init__(self, proxy_map, path, configviper_instance):
        super(ProxyProperty, self).__init__()
        self._proxy_map = proxy_map
        self._path = [path,]
        self._configviper_instance = configviper_instance


    def __repr__(self):
        return pprint.saferepr(self._proxy_map)


    def __getattr__(self, name):
        
        if not name in self._proxy_map:
            raise AttributeError('"%s%s%s" is unknown' % (
                    self.path, 
                    self._configviper_instance.path_separator, 
                    name,))

        # value will be returned only if full-path to "name" has a converter
        value = self._proxy_map[name]
        converter = ConfigViper._sv_converters.get(
                self._fullpath_to(name), None)

        if converter is not None:
            # return value converted
            return converter.to_python(value)

        # there's no converter associated to "name";
        # in that case, if value is a dict return this instance updated
        if isinstance(value, dict):
            self._proxy_map = value
            self._path.append(name)
            return self

        # value isn't a dict;
        # return value converted with the default converter
        converter = self._configviper_instance.get_converter(
                self._fullpath_to(name))

        return converter.to_python(value)


    @property
    def path(self):
        """The config-path until current proxy instance."""
        return self._configviper_instance.path_separator.join(self._path)


    def _fullpath_to(self, name):
        fullpath = name
        if self._path:
            fullpath = '%s%s%s' % (self.path, 
                    self._configviper_instance.path_separator, name,)
        return fullpath


class ConfigViper(object):
    """
    """

    _sv_filename = str()
    """The configuration filename used by all instances of ``ConfigViper``."""
        
    _sv_pathname = str()
    """Path to look for configuration file."""

    _sv_save_on_set = True
    """The auto save on set or during stabilization process."""

    _sv_path_separator = '.'
    """Config-path separator."""

    _sv_converters = {}
    """Converters dict."""

    _sv_encoding = 'utf-8'
    """Encoding which is to be used for the file."""

    _sv_ignore_encoding = False
    """If ignore encoding the JSON file will be opened with the Python's
    built-in ``open`` function. Otherwise the file will be opened with
    the ``codecs.open``."""

    @staticmethod
    def configure(pathname='', filename='', separator='.', 
            auto_save=True, encoding='utf-8', ignore_encoding=False, **kwargs):
        """Set parameters that will be used by all instances of ``ConfigViper``.
        This method is intended to be called only once, when the host 
        application is preparing everything up to be ran.

        :param pathname: The full directory path where the configuration file
            should be placed. If not set, defaults to user's home directory 
            at ``~/.configviper``.

        :param filename: The configuration file name (usually) with ``.json``
            extension. If not set, defaults to ``configviper.json``.

        :param separator: The config-path separator. Defaults to ``.``.

        :param auto_save: When a value is set (:meth:`~ConfigViper.set` method)
            or when :meth:`~ConfigViper.stabilize` method is called the
            configuration file will be automatically saved. 
            Defaults to ``True``.

        :param encoding: String. Encoding which is to be used for the file.
            Defaults to ``"UTF-8"``.

        :param ignore_encoding: Boolean. If ignore encoding the JSON file will
            be opened with the Python's built-in ``open`` function. Otherwise,
            the file will be opened with the ``codecs.open``, wich is the
            default behavior.

        """
        if 'make_backups' in kwargs:
            warnings.warn('ConfigViper: parameter make_backups ignored. '
                    'In release 0.6 the presence of this parameter will '
                    'raise an error.')

        if 'keep_backups' in kwargs:
            warnings.warn('ConfigViper: parameter keep_backups ignored. '
                    'In release 0.6 the presence of this parameter will '
                    'raise an error.')

        ConfigViper._sv_pathname = pathname
        ConfigViper._sv_filename = filename
        ConfigViper._sv_path_separator = separator
        ConfigViper._sv_save_on_set = bool(auto_save)
        ConfigViper._sv_converters = {}
        ConfigViper._sv_encoding = encoding
        ConfigViper._sv_ignore_encoding = ignore_encoding
        
        if not ConfigViper._sv_pathname:
            # set default path name
            ConfigViper._sv_pathname = os.path.expanduser(
                    os.path.join('~', '.configviper'))

        if not ConfigViper._sv_filename:
            # set default configuration file name
            ConfigViper._sv_filename = 'configviper.json'


    def __init__(self):
        super(ConfigViper, self).__init__()
        
        self._config_map = {}
    
        self._pathname = ConfigViper._sv_pathname
        self._filename = ConfigViper._sv_filename
        self._confname = os.path.join(self._pathname, self._filename)
        self._save_on_set = bool(ConfigViper._sv_save_on_set)
        self._stop_saving__save_on_set_flag = self._save_on_set
        self._path_separator = ConfigViper._sv_path_separator
        self._encoding = ConfigViper._sv_encoding
        self._ignore_encoding = ConfigViper._sv_ignore_encoding

        # ensure path name exists
        if not os.path.exists(self._pathname):
            os.makedirs(self._pathname)
            
        # if config file exists then load
        if os.path.exists(self._confname):
            try:
                logger = logging.getLogger(ROOT_LOGGER)
                if self._ignore_encoding:
                    with open(self._confname, 'rb') as f:
                        self._config_map = json.load(f)
                else:
                    with codecs.open(self._confname, 'rb', 
                            encoding=self._encoding) as f:
                        self._config_map = json.load(f, self._encoding)
            except:
                logger.exception('error loading existing file '
                        '("%s", encoding="%s", ignore_encoding=%s)',
                                self._confname, 
                                self._encoding, 
                                self._ignore_encoding)
                raise


    def __repr__(self):
        return pprint.saferepr(self._config_map)
            

    def __getattr__(self, name):
        if not name in self._config_map:
            raise AttributeError('"%s" is unknown' % name)

        # value will be returned only if "name" has a converter
        value = self._config_map[name]
        converter = ConfigViper._sv_converters.get(name, None)
        if converter is not None:
            # return value converted
            return converter.to_python(value)

        # there's no converter associated to "name";
        # in that case, if value is a dict return a new proxy instance
        if isinstance(value, dict):
            return ProxyProperty(value, name, self)

        # value isn't a dict;
        # return value converted with the default converter
        converter = self.get_converter(name)
        return converter.to_python(value)


    def exists(self, path):
        """Test if given config-path already exists."""
        names = path.split(self._path_separator)
        tail = names[:-1]
        head = names[-1]

        data = self._config_map
        for name in tail:
            if not name in data:
                return False
            data = data.get(name)

        # check final config-path component
        return head in data
    
            
    def get(self, path):
        """Get value for the given config-path."""
        # assuming path as 'a.b.c.d', so names will be ['a', 'b', 'c', 'd']
        names = path.split(self._path_separator)
        tail = names[:-1]  # ['a', 'b', 'c']
        head = names[-1]   # 'd'

        data = self._config_map
        for name in tail:
            data = data[name]
    
        # data will end up as { 'd': 3.15 }
        converter = self.get_converter(path)
        return converter.to_python(data[head])
        

    def set(self, path, value):
        """Set value for the given config-path. Be careful to not overrun an
        existing config-path that points to a value that's not a dictionary or
        a :exc:`PathOverrun` exception will be raised. 
        """
        # assuming path as 'a.b.c.d', so names will be ['a', 'b', 'c', 'd']
        names = path.split(self._path_separator)
        tail = names[:-1]  # ['a', 'b', 'c']
        head = names[-1]   # 'd'
        
        data = self._config_map
        for i, name in enumerate(tail):
            # "data" element should be a dict
            if not isinstance(data, dict):
                seg = self._path_separator.join(tail[:(i+1)])
                raise PathOverrun('"%s" config-path segment overrun an '
                        'existing value.' % seg)

            if name in data:
                data = data[name]
            else:
                data[name] = {}
                data = data[name]
                
        if not isinstance(data, dict):
            raise PathOverrun('"%s" config-path overrun an existing value.' % path)

        converter = self.get_converter(path)
        data[head] = converter.to_json(value)
        
        if self._save_on_set:
            self.save()


    def set_auto_save(self):
        """Save configurations on every call to :meth:`set` so you do not have
        to call :meth:`save` yourself. This is the default behavior.
        """
        self._save_on_set = True
        self._stop_saving__save_on_set_flag = True
    

    def save(self):
        """Save configurations formatted as JSON to a file. This method attempts
        to be as safe as possible, using a strategy based on a temporary 
        directory that is created in the same directory as the configuration
        file itself. During the save process, the directory will looks like:

        .. code-block:: text

            ~/.configviper/configviper.json
            ~/.configviper/configviper-4b1b7b5f4a594926ac82de8ecaa439c4/c8c.backup
            ~/.configviper/configviper-4b1b7b5f4a594926ac82de8ecaa439c4/c8c.temp

        Where the ``configviper.json`` is the actual configuration file. 
        The ``configviper-4b1b7b5f4a594926ac82de8ecaa439c4`` is a temporary
        directory name that is unique to the current process.
        The file ``c8c.backup`` is a copy of ``configviper.json`` and the file
        ``c8c.temp`` is the file where the configuration data was actually
        saved. With all that in place, the ``.temp`` file will be copied back to
        the original configuration file. If everything goes ok, the temporary
        directory will be wiped out and the save is done. If not, the backup
        file will be restored and the temporary directory will be wiped out.
        """
        # restore the save on set flag; this restore the expected behavior
        # if stop_saving() has been called before;
        self._save_on_set = self._stop_saving__save_on_set_flag

        logger = logging.getLogger(ROOT_LOGGER)

        temp_dir = self.get_unique_dir_name()
        temp_filename = self.get_unique_temp_filename()
        temp_backup = self.get_unique_backup_filename()

        try:
            # remove temp dir (if already exists)
            if os.path.isdir(temp_dir):
                logger.debug('preparing for save: remove existing temp dir...')
                shutil.rmtree(temp_dir)

            # create temp dir (w unique name for the current process)
            logger.debug('preparing for save: creating temp dir...')
            os.mkdir(temp_dir)

            # make a backup for the current file (if we have one)
            if os.path.isfile(self._confname):
                logger.debug('preparing for save: making backup...')
                shutil.copyfile(self._confname, temp_backup)

            # write current data to a temp file
            logger.debug('preparing for save: writing temp file...')
            with lockfile(temp_filename, 'wb',
                    encoding=self._encoding,
                    ignore_encoding=self._ignore_encoding) as locker:
                data = json.dumps(self._config_map, sort_keys=True, indent=4)
                locker.file_object.write(data)

            # copy the new (temp) file over the current one
            logger.debug('saving: copying temp file to current file...')
            shutil.copyfile(temp_filename, self._confname)

        except BaseException as original_exception:
            logger.exception('error saving '
                    '(temp dir="%s", temp file="%s", backup file="%s")',
                            temp_dir,
                            temp_filename,
                            temp_backup)
            try:
                # restore backup over the current configurations file and
                # remove temp dir if succeeded
                logger.debug('restoring backup "%s" over "%s"',
                        temp_backup, self._confname)
                shutil.copyfile(temp_backup, self._confname)

                logger.debug('removing temp dir "%s"', temp_dir)
                shutil.rmtree(temp_dir)
            except:
                # log the current exception...
                logger.exception('error restoring backup after save failure '
                        '(copying from "%s" to "%s")',
                                temp_backup, 
                                self._confname)

            # ...and re-raise the original
            raise original_exception

        else:
            # at this point, save was successful
            logger.debug('saving done!')

            try:
                if os.path.isdir(temp_dir):
                    shutil.rmtree(temp_dir)
            except:
                # mutes any errors explicitly (just logs it)
                logger.exception('muted error: removing temp dir after '
                        'successful save (temp dir "%s")', temp_dir)


    def stop_saving(self):
        """Stop saving on every :meth:`set`. This is particularly useful when
        you need to set various configurations at once, to avoid the overburden
        of save on every set. The next call to :meth:`save` will restore the
        normal operation according to :attr:`is_auto_save`. The pattern is::

            conf = ConfigViper()
            conf.stop_saving()
            conf.set('spam.ham.eggs', 'sausage')
            conf.set('foo.bar', 'baz')
            ..
            conf.save()

        """
        self._stop_saving__save_on_set_flag = self._save_on_set
        self._save_on_set = False
       

    def stabilize(self, values):
        """This method will merge existing config-paths with config-paths and 
        values and converters you determine. The ``values`` argument should be a
        tuple of tuples. Each sub-tuple should have three values where the first
        value is the config-path; second is their default value and third the
        converter instance for that config-path::

            from datetime import datetime
            from configviper import ConfigViper
            from configviper.converters import DATETIME_CONVERTER

            values = (
                ('path.to.config', 1, None),
                ('path.to.another', datetime.now(), DATETIME_CONVERTER),)
            
        The first sub-tuple sets config-path ``"path.to.config"``, their default
        value which is ``1``, and ``None`` as their converter, meaning that that
        config-path does not need a special converter. Second sub-tuple sets
        config-path ``"path.to.another"``, their default value which is 
        current date and time and a built-in converter for ``datetime`` objects.
        Then you call stabilization in a :class:`ConfigViper` instance::

            conf = ConfigViper()
            conf.stabilize(values)

        When you instantiate a :class:`ConfigViper` class the configuration file
        is automatically loaded. In the stabilization process, existing
        config-paths are preserved with their current values, but the converters
        are always set. So if you write your own converter be aware to write a
        converter that can handle older formats of previous versions.
        """

        # (re)init converters dict
        ConfigViper._sv_converters = {}

        # turn-off auto save on set (will be turned-on again if needed)
        auto_save = self._save_on_set
        self._save_on_set = False

        for path, value, converter in values:
            # first install converter for this config-path
            ConfigViper._sv_converters[path] = converter
            if self.exists(path):
                # leave this config-path with current value
                pass
            else:
                # set the new config-path with default value
                self.set(path, value)

        if auto_save:
            # save configurations and restore auto save on set
            self._save_on_set = True
            self.save()
    

    def register(self, path, converter):
        """This method (re)associate a converter instance with a config-path.
        If the config-path already exists then their current value: (1) will 
        be got with the current converter; (2) the new converter is set and; 
        (3) the value is settled again with the new converter in place.
        """
        path_exists = self.exists(path)

        if path_exists:
            # config-path already exists; 
            # ensure a reasonable converter replacement
            current_value = self.get(path) # a Python type

        # assign (or replace) converter for config-path
        ConfigViper._sv_converters[path] = converter

        if path_exists:
            # reset the value with the new converter in place
            # (user should be careful to write a converter capable of 
            # re-convert to JSON the current Python value old converter 
            # had converted to)
            self.set(path, current_value)


    def get_converter(self, path):
        """Get converter for the given config-path or a
        :attr:`~converters.DEFAULT_CONVERTER` if there's none.
        """
        converter = ConfigViper._sv_converters.get(path, None)
        if converter is None:
            converter = converters.DEFAULT_CONVERTER
        return converter


    def get_unique_dir_name(self):
        # grab current thread ident
        t = threading.current_thread()
        ident = getattr(t, 'ident', hash(t))
        identhex = '%x' % (ident & 0xffffffff)
        
        # collect other values
        hostname = socket.gethostname()
        pidvalue = str(os.getpid())
        
        # compound a string sequence based on collected values
        sequence = 'configviper|%s|%s|%s' % (identhex, hostname, pidvalue)
        unique_name = 'configviper-%s' % hashlib.md5(sequence).hexdigest()

        path = os.path.dirname(os.path.abspath(self._confname))
        return os.path.join(path, unique_name)
        
        
    def get_unique_temp_filename(self):
        filename = '%x.temp' % os.getpid()
        return os.path.join(self.get_unique_dir_name(), filename)


    def get_unique_backup_filename(self):
        filename = '%x.backup' % os.getpid()
        return os.path.join(self.get_unique_dir_name(), filename)


    @property
    def pathname(self):
        """The path name where configuration file should be saved by 
        this instance. File name is determined by :attr:`filename` attribute.
        See attribute :attr:`config_filename`.
        """
        return self._pathname

        
    @property
    def filename(self):
        """The configuration file name this instance is using. The path
        where the file is placed is determined by :attr:`pathname` attribute.
        See attribute :attr:`config_filename`.
        """
        return self._filename

        
    @property
    def config_filename(self):
        """The full path and file name this instance is using. See attributes
        :attr:`pathname` and :attr:`filename`.
        """
        return self._confname


    @property
    def backup_filename(self):
        """The full path and file name for the backup. 
        See :attr:`is_make_backups` and :meth:`save`.
        """
        # TODO: remove this property in 0.6 release
        warnings.warn('ConfigViper: backup_filename property will be'
                'removed in 0.6 release.')
        return '' # self._backupname
    

    @property
    def path_separator(self):
        """The config-path separator this instance is using."""
        return self._path_separator

    
    @property
    def is_auto_save(self):
        """Indicates whether or not the configuration file should be saved
        immediately before :meth:`set` method is called. This flag is also
        considered when :meth:`stabilize` method is called.
        """
        return self._save_on_set or self._stop_saving__save_on_set_flag


    @property
    def is_make_backups(self):
        """Indicates whether a backup should be made right before actual
        save operation. The :meth:`save` method is capable of doing a backup
        and restore from that backup if the actual save operation fails.
        See :attr:`is_keep_backups`. The backup file will have the same name as
        the original configuration file with ``.backup`` appended.
        """
        # TODO: remove this property in 0.6 release
        warnings.warn('ConfigViper: is_make_backups property will be '
                'removed in 0.6 release.')
        return False # self._make_backups


    @property
    def is_keep_backups(self):
        """Indicate whether the backup file should be kept when the :meth:`save`
        method completes, even if an error occurs. See :attr:`is_make_backups`.
        """
        # TODO: remove this property in 0.6 release
        warnings.warn('ConfigViper: is_keep_backups property will be '
                'removed in 0.6 release.')
        return False # self._keep_backups

