#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2011 Giacomo Bagnoli <g.bagnoli@asidev.com>

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import logging
import magic
import mimetypes
import os
import re
import shutil
import threading

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy.event import listen
from sqlalchemy.orm import Session
from sqlalchemy.schema import Sequence

from . exc import UninitializedError

log = logging.getLogger(__name__)
__all__ = ['FileSystemEntity']


class FileSystemEntity(object):

    id_seq = Sequence("pufferfish_id_seq")
    id = Column(Integer, id_seq, primary_key=True)
    content_type = Column(Unicode(128))
    name = Column(Unicode(128), nullable=False)
    size = Column(Integer)

    # we keep a shared dict of object added to know which
    # directory on disk must be removed when a transation
    # is committed or rollback-ed
    _state = dict()
    _mutex = threading.Lock()
    temporary_name = "_FileSystemEntity_temporary_name"

    @classmethod
    def _add_as(cls, state, obj):
        with cls._mutex:
            if cls.__name__ not in cls._state:
                cls._state[cls.__name__] = dict(
                                added=dict(),
                                updated=dict(),
                                deleted=dict(),
                                failed=list()
                )
            cls._state[cls.__name__][state][obj.id] = obj

    @classmethod
    def after_attach(cls, session, instance):
        if isinstance(instance, FileSystemEntity) \
        and (not hasattr(instance, "session")
             or not instance.session is session):
            log.debug("instance %s attaching to session %s", instance, session)
            instance.session = session

    @classmethod
    def after_rollback(cls, session):
        """ called after a transaction is rolled back.
            To keep files in sync with database, it is needed to:
            - remove new added files as respective objects in database
              don't exist
            - restore original files that have been updated during
               the transaction
        """
        try:
            cls._mutex.acquire()
            if cls.__name__ not in cls._state:
                return
            log.debug("%s running after_rollback" % cls)
            state = dict(cls._state[cls.__name__])
            # delete new files as we are rolling back
            for obj in state["added"].values():
                if obj.session is not session:
                    log.debug("Skipping obj %s as it is attached "
                              "to another session %s", obj, session)
                    continue

                if os.path.isdir(obj.dir):
                    log.debug("%s is in the added state but transaction has "
                              "been rolled back. Removing", obj.dir)
                    try:
                        shutil.rmtree(obj.dir)
                    except Exception:
                        cls._state['failed'].append(obj)
                        log.exception("Error in rollback for %s" % obj)
                del cls._state[cls.__name__]['added'][obj.id]

            # restore original version of updated files
            for obj in state['updated'].values():
                if obj.session is not session:
                    log.debug("Skipping obj %s as it is attached "
                              "to another session %s", obj, session)
                    continue

                log.debug("%s is in the updated state but transaction has "
                          "been rolled back. Moving back old file from %s",
                          obj.name, obj.original_dir)
                try:
                    shutil.rmtree(obj.dir)
                    shutil.move(obj.original_dir, obj.dir)

                except Exception:
                    cls._state['failed'].append(obj)
                    log.exception("Cannot move %s to %s",
                                  obj.original_dir, obj.dir)
                else:
                    del obj.original_dir

                del cls._state[cls.__name__]['updated'][obj.id]

            # no need to do anything on deleted objects
            for obj in state['deleted'].values():
                if obj.session is session:
                    del cls._state[cls.__name__]['deleted'][obj.id]

        finally:
            cls._mutex.release()
            if cls.__name__ in cls._state:
                log.debug("after_rollback_ ended. Paths in failed state: %s",
                        cls._state[cls.__name__]['failed'])

    @classmethod
    def after_commit(cls, session):
        """ called after a transaction has been committed to disk
            To keep files in sync with database, it is needed to:
            - remove files belonging to files removed during the transaction
            - remove original files of those files that have been updated
              old files were preserved in case of a rollback
        """
        try:
            cls._mutex.acquire()
            if cls.__name__ not in cls._state:
                return
            log.debug("%s running after_commit" % cls)
            state = dict(cls._state[cls.__name__])
            # transaction has been committed, remove files from disc
            for obj in state["deleted"].values():
                if obj.session is not session:
                    log.debug("Skipping obj %s as it is"
                              "attached to another session %s",
                              obj, session)
                    continue

                log.debug("%s is in the removed state and transaction has " +\
                          "been committed. Removing", obj)
                try:
                    shutil.rmtree(obj.dir)
                except Exception as e:
                    cls._state['failed'].append(obj)
                    log.exception("Cannot remove %s", obj, e)

                del cls._state[cls.__name__]['deleted'][obj.id]

            # remove old files that have been updated
            for obj in state['updated'].values():
                log.debug("%s has been updated and transaction committed. " +\
                          "Removing %s", obj.name, obj.original_dir)
                try:
                    shutil.rmtree(obj.original_dir)

                except Exception as e:
                    cls._state['failed'].append(obj)
                    log.exception("Cannot remove original path of %s", obj)

                else:
                    del obj.original_dir

                del cls._state[cls.__name__]['updated'][obj.id]

            # no need to do anything on deleted objects
            for obj in state['added'].values():
                if obj.session is session:
                    del cls._state[cls.__name__]['added'][obj.id]

        finally:
            cls._mutex.release()
            if cls.__name__ in cls._state:
                log.debug("after_commit ended. Paths in failed state: %s",
                        cls._state[cls.__name__]['failed'])

    @classmethod
    def set_paths(cls, base, private="", url_prefix=None):
        if not base.startswith("/"):
            raise ValueError("base must be an absolute path: %s", base)
        cls.base_path = base
        cls.private_path = private
        cls.url_base = cls.base_path.replace(cls.private_path, '')
        if url_prefix and not url_prefix.startswith('/'):
            url_prefix = '/' + url_prefix
        cls.url_prefix = url_prefix

    @classmethod
    def initialize(cls, base, private="", url_prefix=None):
        log.info("Initializing %s", cls.__name__)
        log.debug("%s base=%s, private=%s",
                 cls.__name__, base, private)
        cls.set_paths(base, private, url_prefix)
        listen(cls, 'init', cls.after_init)
        listen(cls, 'after_delete', cls.after_delete)
        listen(Session, 'after_rollback', cls.after_rollback)
        listen(Session, 'after_commit', cls.after_commit)
        listen(Session, 'after_attach', cls.after_attach)

    @classmethod
    def after_delete(cls, mapper, connection, target):
        # add the path to the list of those that will be
        # removed upon session commit
        cls._add_as('deleted', target)

    def __open_source(self, source):
        self.__close_source = False
        if issubclass(type(source), basestring):
            source = open(source)
            self.__close_source = True
        return source

    @property
    def source(self):
        return self.__open_source(self.path)

    @source.setter
    def source(self, newsource):
        self.update_file(newsource)
        pass

    @property
    def path(self):
        try:
            return self.__path
        except AttributeError:
            self.__path = os.path.join(self.dir, self.name)
            return self.__path

    @property
    def dir(self):
        try:
            return self.__dir
        except AttributeError:
            self.__dir = os.path.join(self.base_path, "%d" % self.id)
            return self.__dir

    @property
    def url_dir(self):
        try:
            return self.__url_dir
        except AttributeError:
            dir_ = self.url_base
            if self.url_prefix:
                dir_ = '{0}/{1}'.format(self.url_prefix, self.url_base)
            self.__url_dir = '{0}/{1}'.format(dir_, self.id)
            return self.__url_dir

    @property
    def url(self):
        try:
            return self.__url
        except AttributeError:
            self.__url = "{0}/{1}".format(self.url_dir, self.name)
            return self.__url

    @property
    def plain_name(self):
        try:
            return self.__plain_name
        except AttributeError:
            self.__plain_name = os.path.splitext(self.name)[0]
            return self.__plain_name

    @property
    def extension(self):
        try:
            return self.__extension
        except AttributeError:
            self.__extension = os.path.splitext(self.name)[1].lower()
            return self.__extension

    def __remove_gen_paths(self):
        del self.__path
        del self.__dir
        del self.__plain_name
        try:
            del self.__url
        except:
            pass
        try:
            del self.__extension
        except:
            pass

    def __init__(self, *args, **kwargs):
        kwargs.pop("source", None)
        kwargs.pop("session", None)
        super(FileSystemEntity, self).__init__(*args, **kwargs)

    @classmethod
    def after_init(cls, self, args, kwargs):
        try:
            if self.id:
                log.debug("%s seems to be already initialized", self)

        except AttributeError:
            pass

        else:
            cls.create_new(self, args, kwargs)

    @classmethod
    def create_new(cls, self, args, kwargs):
        log.debug("Running post-constructor on %s, (args:%s, kwargs:%s)",
                  cls.__name__, args, kwargs)

        if "source" not in kwargs:
            if not self.id:
                raise TypeError('Source parameter is required')
            return

        if "name" not in kwargs:
            temp_name = True
            kwargs['name'] = cls.temporary_name
        else:
            temp_name = False
            kwargs['name'] = self.clean_name(kwargs['name'])

        source = self.__open_source(kwargs.pop("source"))
        session = kwargs.pop('session')
        object.__setattr__(self, "name", kwargs['name'])

        if 'id' in kwargs:
            object.__setattr__(self, 'id', kwargs['id'])

        session.add(self)
        if not self.id:
            # flush the session, so that the DBMS assigns us an unique ID
            session.flush()

        self.content_type = magic.from_buffer(source.read(1024), mime=True)
        log.debug("content_type: %s", self.content_type)
        source.seek(0)

        if temp_name:
            self.name = str(self.id)

        try:
            os.makedirs(self.dir)
        except OSError as e:
            # 17 means directory exist
            if e.errno != 17:
                raise e

            confl = "%s%s" % (self.dir, "_conflict")
            while os.path.isdir(confl):
                confl = "%s%s" % (confl, "_")
            log.error("%s already exists, while it should not as the "
                      "primary key %d has been just generated. This is "
                      "problably a bug. Moving %s to %s",
                      self.dir, self.id, self.dir, confl)

            shutil.move(self.dir, confl)
            os.makedirs(self.dir)

        # add the path to the list of those that will be
        # removed upon session rollback
        self._add_as('added', self)

        self.update_file(source)
        del temp_name

    def clean_name(self, value):
        value = value.replace(" ", "_")
        return re.sub('[^\w\._]+', '', value)

    def __protect_original(self):
        # if file already exists, rename it first
        # so we can handle rollbacks and restore the original ones
        if os.path.isfile(self.path) and \
            self.__class__.__name__ in self._state and \
            not self in self._state[self.__class__.__name__]['updated']:
            original = "%s__original" % (self.dir)
            shutil.copytree(self.dir, original)
            self.original_dir = original
            self._add_as('updated', self)

    def update_file(self, source):
        self.__protect_original()

        source = self.__open_source(source)

        if hasattr(self, "create_thumbnail"):
            source = self.create_thumbnail(source)

        self.save_file(source)
        if self.__close_source:
            source.close()
        self.size = os.path.getsize(self.path)

    def save_file(self, source):
        with open(self.path, "wb") as p:
            shutil.copyfileobj(source, p)

    def __update_file_name(self, value):
        log.debug("Setting file name to %s", value)
        try:
            old_path = self.path
        except AttributeError:
            raise UninitializedError('%s has not been initialized' %
                                     self.__class__.__name__)
        old_plain_name = self.plain_name
        old_extension = self.extension
        object.__setattr__(self, 'name', value)
        self.__remove_gen_paths()

        if old_path != self.path:
            log.debug("old_path: %s", os.path.exists(old_path))
            if os.path.exists(old_path):
                self.__protect_original()
                log.debug("rename file %s -> %s", old_path, self.path)
                os.rename(old_path, self.path)
                if hasattr(self, "rename_thumbnail"):
                    self.rename_thumbnail(old_plain_name, old_extension,
                                         self.plain_name)

    def __getattr__(self, attr):
        if attr == 'session':
            session = Session.object_session(self)
            super(FileSystemEntity, self).__setattr__(attr, session)
            return session

        raise AttributeError(attr)

    def __setattr__(self, attr, value):
        if attr == "name":
            if value == self.name:
                return

            value = self.clean_name(unicode(value))
            ext = os.path.splitext(value)[1]
            if ext == "" and self.content_type is not None:
                ext = mimetypes.guess_extension(self.content_type)
                if ext == ".jpe":  # pragma: nocover
                    ext = ".jpg"
                value = "%s%s" % (self.id, ext.lower())
            self.__update_file_name(value)

        else:
            super(FileSystemEntity, self).__setattr__(attr, value)

    def to_dict(self):
        return dict(id=self.id, name=self.name, url=self.url, path=self.path,
                    size=self.size, content_type=self.content_type)
