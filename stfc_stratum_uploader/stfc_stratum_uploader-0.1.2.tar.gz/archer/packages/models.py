from contextlib import closing
import re
import os
import shutil
import tarfile

from django.db import models
from django.conf import settings
from archer.projects.models import Project
from archer.core import exceptions


class Package(models.Model):
    def __get_upload_path(self, filename):
        return os.path.join(settings.MEDIA_ROOT, ".%s" % self.project, filename).replace('/./', '/')

    class Status:
        """Enumeration for Package status"""
        new, uploaded, unpacking, deployed, cancelled, deleted, undeployed, error = range(8)

    class ContentsError(exceptions.ApplicationError):
        pass

    __STATUSES = dict((value, name) for name, value in vars(Status).items() if not name.startswith('__'))

    project = models.ForeignKey(Project)
    file = models.FileField(upload_to=__get_upload_path, max_length=1024)
    status = models.IntegerField(
        choices=__STATUSES.items(),
        blank=False,
        null=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = (
            ('deploy_package', 'Deploy package'),
            ('remove_package', 'Remove package'),
        )

    def status_name(self):
        return Package.__STATUSES[self.status]

    def can_remove(self):
        return self.status in [Package.Status.deployed, Package.Status.undeployed, Package.Status.uploaded]

    def can_deploy(self):
        if self.status in [Package.Status.uploaded, Package.Status.undeployed, Package.Status.cancelled,
                           Package.Status.deployed]:
            return os.path.isfile(self.file.path) and tarfile.is_tarfile(self.file.path)
        return False

    def filepath(self):
        """
            Returns path to the file but hides the path to MEDIA directory.
            """
        return re.sub('^%s' % settings.MEDIA_ROOT, '', self.file.path)

    def filename(self):
        """
            Returns name of the file without full path.
            """
        replace = os.path.join(settings.MEDIA_ROOT, self.project.alias_path()[1::]) + '/'
        return re.sub('^%s' % replace, '', self.file.path)

    def get_file_list(self):
        """
            Returns list of files in the tarfile.
            """
        path = self.file.path
        if not os.path.isfile(path):
            return None
        if not tarfile.is_tarfile(path):
            return None
        tar = tarfile.open(path)
        names = tar.getnames()
        return names

    def deploy(self, subdir='', force=False):
        """
            Unpacks the tar file at the project directory.
            Any previous content is deleted.

            Returns True if deployment succeeded.
            Raises IOError if file does not exist.
            Raises archer.core.exceptions.ValidationError if file is not a tar file.
            """
        import tarfile

        if self.can_deploy or force:
            file_path = self.file.path
            if not os.path.isfile(file_path):
                self.status = Package.Status.error
                self.save()
                raise IOError('package file ' + self.filepath() + ' does not exist')
            if not tarfile.is_tarfile(file_path):
                self.status = Package.Status.error
                self.save()
                raise Package.ContentsError('package file ' + self.filepath() + ' is not tarball file')
            try:
                # self.project.clear_dir(subdir)
                with closing(tarfile.open(file_path)) as tar:
                    self.status = Package.Status.unpacking
                    self.save()

                    dir = self.project.subdir(subdir)
                    for f in tar:
                        if f.name.startswith('/'):
                            raise Package.ContentsError('Tar contains disallowed paths starting with "/"!')
                        normpath = os.path.normpath(f.name)
                        if normpath.startswith('../'):
                            raise Package.ContentsError('Tar contains disallowed paths using ".."!')
                        content_path = os.path.join(dir, f.name)
                        if not os.access(content_path, os.W_OK):
                            shutil.rmtree(content_path, ignore_errors=True)

                    tar.extractall(path=dir)

                    self.status = Package.Status.deployed
                    self.save()
                    return True
            except (Package.ContentsError, tarfile.TarError, IOError, OSError) as e:
                self.status = Package.Status.error
                self.save()
                raise e
        else:
            return False

    def remove(self):
        """
            Removes package file from MEDIA directory.
            """
        result = False
        if os.path.isfile(self.file.path):
            os.unlink(self.file.path)
            result = True
        self.status = Package.Status.deleted
        self.save()
        return result

    def __unicode__(self):
        return self.filename()
