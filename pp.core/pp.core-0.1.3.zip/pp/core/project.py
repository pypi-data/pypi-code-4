################################################################
# pp.core - Produce & Publish
# (C) 2013, ZOPYX Limited, www.zopyx.com
################################################################

import os
import util
import datetime

class Project(object):
    """ Presents a Produce & Publish authoring project
        with a given title. The data is stored on some
        given FS layer (e.g. in the cloud).
    """

    def __init__(self, title, fslayer, create=False):
        self.title = title
        self.fslayer = fslayer
        self.title_consolidated = util.slugify(title)
        if create:
            self.create_structure()

    @property
    def current_path(self):
        return 'projects/%s/current' % self.title_consolidated

    @property
    def versions_path(self):
        return 'projects/%s/versions' % self.title_consolidated

    @property
    def drafts_path(self):
        return 'projects/%s/drafts' % self.title_consolidated

    def create_structure(self):
        self.fslayer.makedir(self.current_path, recursive=True, allow_recreate=True)
        self.fslayer.makedir(self.drafts_path, recursive=True, allow_recreate=True)
        self.fslayer.makedir(self.versions_path, recursive=True, allow_recreate=True)

    def create_demo_content(self):
        target_filename = '%s/index.html' % self.current_path
        demo_content = open(os.path.join(os.path.dirname(__file__), 'samples', 'demo.html')).read()
        with self.fslayer.open(target_filename, 'wb') as fp:
            fp.write(demo_content)

    def create_version(self):
        """ Copy ``current`` content into a new version """
        all_versions = self.fslayer.listdir(self.versions_path)
        new_version = '%s-V-%d' % (datetime.datetime.now().strftime('%Y%m%dT%H:%M:%S'), 
                                   len(all_versions)+1)
        for name in self.fslayer.listdir(self.current_path):
            fullname = os.path.join(self.current_path, name)
            destdir = os.path.join(self.versions_path, new_version)
            self.fslayer.makedir(destdir, allow_recreate=True, recursive=True)
            destname = os.path.join(self.versions_path, new_version, name)
            with self.fslayer.open(destname, 'wb') as fp:
                fp.write(self.fslayer.open(fullname, 'rb').read())
        return new_version

    def copy_from_localfs(self, local_src, dest_path):
        self.fslayer.makedir(dest_path, allow_recreate=True, recursive=True)
        for name in os.listdir(local_src):
            fullname = os.path.join(local_src, name)
            dest_filename = '%s/%s' % (dest_path, name)
            with self.fslayer.open(dest_filename, 'wb') as fp:
                fp.write(open(fullname, 'rb').read())

    def clear_directory(self, path):
        """ Cleanup a fslayer directory """
        for name in self.fslayer.listdir(path):
            self.fslayer.remove(os.path.join(path, name))

    def all_drafts(self):
        """ List all drafts """
        return self.fslayer.listdir(self.drafts_path)

    def all_versions(self):
        """ List all versions """
        return self.fslayer.listdir(self.versions_path)


class PublishingLocation(object):
    """ A Publishing location for a given project
        (or title) is a given through a FS layer instance
        (e.g. somewhere in the cloud).
    """

    def __init__(self, title, fslayer, create=True):
        self.title = title
        self.fslayer = fslayer
        self.title_consolidated = util.slugify(title)
        if create:
            self.create_structure()

    @property
    def current_path(self):
        return 'published/%s/current' % self.title_consolidated

    @property
    def archive_path(self):
        return 'published/%s/archive' % self.title_consolidated

    def create_structure(self):
        self.fslayer.makedir(self.current_path, recursive=True, allow_recreate=True)
        self.fslayer.makedir(self.archive_path, recursive=True, allow_recreate=True)

    clear_directory = Project.clear_directory.im_func
    copy_from_localfs = Project.copy_from_localfs.im_func

    def all_archived_versions(self):
        """ List all versions """
        return self.fslayer.listdir(self.archive_path)
