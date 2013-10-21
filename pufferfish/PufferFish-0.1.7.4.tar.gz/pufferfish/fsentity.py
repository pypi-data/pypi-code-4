#!/usr/bin/env python
# -*- coding: utf-8 -*-

import elixir
import logging
import magic
import mimetypes
import os
import re
import shutil

from elixir import Field, Unicode, Entity, Integer, using_options

from session import add_session_hooks
log = logging.getLogger(__name__)

__all__ = [ 'FileSystemEntity' ]

class FileSystemEntity(Entity):
    using_options(abstract=True)

    id = Field(Integer, autoincrement=True, primary_key=True)
    content_type = Field(Unicode(128))
    name = Field(Unicode(128), required=True)
    size = Field(Integer)

    # we keep a shared list of object added to know which
    # directory on disk must be removed when a transation
    # is committed or rollback-ed
    tmp_objects = {"added": [], "removed": [], "updated": {}, "failed": [] }

    @classmethod
    def __after_rollback__(cls, session):
        """ called after a transaction is rolled back.
            To keep files in sync with database, it is needed to:
            - remove new added files as respective objects in database
              don't exist 
            - restore original files that have been updated during the transaction
        """
        try:
            log.debug("%s running __after_rollback__" % cls)
            tmp_objects = cls.tmp_objects
            # delete new files as we are rolling back
            for path in tmp_objects["added"]:
                if os.path.isdir(path):
                    log.debug("%s is in the added state but transaction has been rolled back. Removing",
                                 path)
                    try:
                        shutil.rmtree(path)
                    except Exception as e:
                        cls.tmp_objects['failed'].append((path,None))
                        log.critical("Cannot remove %s: %s", path, e)
                        log.exception("Exception was")
                        
            # restore original version of updated files
            for id_ in tmp_objects['updated']:
                (name, original, updated ) = tmp_objects['updated'][id_]
                log.debug("%s is in the updated state but transaction has been rolled back." +\
                              " Moving back old file from %s", name, original)
                try:
                    shutil.rmtree(updated)
                    shutil.move(original, updated)
                except Exception as e:
                    cls.tmp_objects['failed'].append((original, updated))
                    log.critical("Cannot move %s to %s: %s", original, updated, e)
                    log.exception("Exception was")

            tmp_objects['updated'] = {}
            tmp_objects['added'] = []
            tmp_objects['removed'] = []

        finally:
            log.debug("__after_rollback_ ended. Paths in failed state: %s", cls.tmp_objects['failed'])

    @classmethod
    def __after_commit__(cls, session):
        """ called after a transaction has been committed to disk
            To keep files in sync with database, it is needed to:
            - remove files belonging to files removed during the transaction
            - remove original files of those files that have been updated
              old files were preserved in case of a rollback
        """
        try:
            log.debug("%s running __after_commit__" % cls)
            tmp_objects = cls.tmp_objects
            # transaction has been committed, remove files from disc
            for path in tmp_objects["removed"]:
                log.debug("%s is in the removed state and transaction has been committed. Removing",
                             path)
                try: 
                    shutil.rmtree(path)
                except Exception as e:
                    cls.tmp_objects['failed'].append((path,None))
                    log.critical("Cannot remove %s: %s", path, e)
                    log.exception("Exception was")

            # remove old files that have been updated
            for id_ in tmp_objects['updated']:
                (name, original, updated ) = tmp_objects['updated'][id_]
                log.debug("%s has been updated and transaction committed. Removing %s",
                              name, original)
                try:
                    shutil.rmtree(original)
                except Exception as e:
                    cls.tmp_objects['failed'].append((original,None))
                    log.critical("Cannot remove %s: %s", original, e)
                    log.exception("Exception was")

            tmp_objects['updated'] = dict()
            tmp_objects['removed'] = []
            tmp_objects['added'] = []

        finally:
            log.debug("__after__commit__ ended. Paths in failed state: %s", cls.tmp_objects['failed'])

    @classmethod
    def set_paths(cls, base, private=""):
        if not base.startswith("/"):
            raise ValueError("base must be an absolute path")
        cls.base_path = base
        cls.private_path = private
   
    def __open_source(self, source):
        self.__close_source = False
        if issubclass(type(source), basestring):
            source = open(source)
            self.__close_source = True
        return source
    
    @property
    def source(self):
        self.setup_paths()
        return self.__open_source(self.path)

    @source.setter
    def source(self, newsource):
        self.update_file(newsource)

    def __init__(self, *args, **kwargs):
            
        if "source" not in kwargs:
            raise TypeError("takes at least source argument")

        if "name" not in kwargs:
            temp_name = True
            kwargs['name'] = "temporary"
        else:
            temp_name = False
            kwargs['name'] = self.clean_name(kwargs['name'])

        source = self.__open_source(kwargs.pop("source"))
        session = kwargs.pop('session', elixir.session) 
        super(FileSystemEntity, self).__init__(*args, **kwargs)

        # flush the session, so that the DBMS assigns us an unique ID
        session.add(self)
        session.flush()

        self.content_type = magic.from_buffer(source.read(1024), mime=True)
        log.debug("content_type: %s", self.content_type)
        source.seek(0)

        if temp_name:
            self.name = self.id
        self.setup_paths()

        try:
            os.makedirs(self.dir)
        except OSError as e:
            # 17 means directory exist
            if e.errno != 17:
                raise e

            confl = "%s%s" % (self.dir, "_conflict")
            while os.path.isdir(confl):
                confl = "%s%s" % (confl, "_")
            log.error("%s already exists, while it should not as the primary key %d as " +\
                      "been just generated. This is problably a bug. "+ \
                      "Moving %s to %s", self.dir, self.id, self.dir, confl)

            shutil.move(self.dir, confl)
            os.makedirs(self.dir)

        # add the path to the list of those that will be
        # removed upon session rollback
        self.__class__.tmp_objects['added'].append(self.dir)

        self.update_file(source)
        del temp_name
    
    def clean_name(self, value):
         value = value.replace(" ", "_")
         return re.sub('[^\w\._]+', '', value)
    
    def delete(self):
        self.setup_paths()
        # add the path to the list of those that will be
        # removed upon session commit
        self.__class__.tmp_objects['removed'].append(self.dir)
        super(FileSystemEntity, self).delete()

    def __protect_original(self):
        # if file already exists, rename it first
        # so we can handle rollbacks and restore the original ones
        if os.path.isfile(self.path) and \
            not self.id in self.tmp_objects['updated']:
            original = "%s__original" % (self.dir)
            shutil.copytree(self.dir, original)
            self.tmp_objects['updated'][self.id] = (self.name, original, self.dir)

    def update_file(self, source):
        self.setup_paths()
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

    def __split_name(self):
        plain_name, extension = os.path.splitext(self.name)
        extension = extension.lower()
        object.__setattr__(self, "plain_name", plain_name)
        object.__setattr__(self, "extension", extension.lower())

    def __update_file_name(self, value):
        if hasattr(self, "path"):
            log.debug("Setting file name to %s", value)
            old_path = self.path
            old_plain_name = self.plain_name
            super(FileSystemEntity, self).__setattr__("name", value)
            self.setup_paths(force=True)
            
            log.debug("old_path: %s", os.path.exists(old_path))
            if os.path.exists(old_path):
                self.__protect_original()
                log.debug("rename file %s -> %s", old_path, self.path)
                os.rename(old_path, self.path)
                if hasattr(self, "rename_thumbnail"):
                    self.rename_thumbnail(old_plain_name, self.plain_name)
        else:
            super(FileSystemEntity, self).__setattr__("name", value)
        
    def setup_paths(self, force=False):
        # call object.__setattr__ as this function could have been called from
        # __setattr__
        if force or not hasattr(self, "__path_configured"):
            object.__setattr__(self, "base_path", self.__class__.base_path)
            if hasattr(self.__class__, "private_path"):
                object.__setattr__(self, "private_path", self.__class__.private_path)
            else:
                object.__setattr__(self, "private_path", "")
            self.__split_name()
            object.__setattr__(self, "dir", os.path.join(self.base_path, "%d" % self.id))
            object.__setattr__(self, "path", os.path.join(self.dir, self.name))
            object.__setattr__(self, "url", str(self.path.replace(self.private_path, "")))
            object.__setattr__(self,"__path_configured", True)

    def __setattr__(self, attr, value):
        if attr == "name":
            if value == self.name:
                return

            value = self.clean_name(unicode(value))
            ext = os.path.splitext(value)[1]
            if ext == "" and self.content_type:
                ext = mimetypes.guess_extension(self.content_type)
                if ext == ".jpe":
                    ext = ".jpg"
                value = "%s%s" % (self.id, ext)
            self.__update_file_name(value)

        else:
            super(FileSystemEntity, self).__setattr__(attr, value)

    def __getattr__(self, attr):
        if attr in ("url", "path", "dir"):
            self.setup_paths()
            return getattr(self, attr)
        else:
            raise AttributeError(attr)

    def to_dict(self):
        return dict(name=self.name, url=self.url, path=self.path,
                    size=self.size, content_type=self.content_type)
