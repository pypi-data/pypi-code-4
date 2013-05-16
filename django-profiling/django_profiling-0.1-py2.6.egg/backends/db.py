from logging import getLogger
from os import unlink, fdopen
from pstats import Stats
from tempfile import mkstemp

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.core.files import File

from dprofiling.models import Session, Profile



log = getLogger('dprofiling.backends.db')

class DatabaseBackend(object):
    def __init__(self, local=True, **kwargs):
        self.local = local
        self.tempdir = kwargs.get('tempdir', None)

    def store(self, path, profile):
        temp = None
        try:
            session = Session.on_site.get(path=path, active=True)
        except (Session.DoesNotExist, Session.MultipleObjectsReturned) as e:
            log.exception('Error retrieving the profiling session object for %s' %
                    (path,))
        try:
            temp, path = mkstemp(dir=self.tempdir)
            log.debug('Temporary file created: %s' % (path,))
            temp = fdopen(temp)
            profile.dump_stats(path)
            log.debug('Profile information dumped to temporary file')
            stored_profile = Profile(session=session, dump=File(temp))
            stored_profile.save()
            log.debug('Profile %d created' % (stored_profile.pk,))
        except Exception as e:
            log.exception('Exception while storing profile')
        finally:
            try:
                if temp:
                    temp.close()
                    unlink(path)
                    log.debug('Temporary file removed: %s' % (path,))
            except:
                log.exception('Error while removing a temporary file')

    def get_stats(self, session):
        output = StringIO()
        stats = None
        temp_files = []
        try:
            for profile in session.profiles.all():
                if profile.dump.path:
                    log.debug('Adding local profile dump')
                    path = profile.dump.path
                else:
                    log.debug('Creating a temporary file for remote profile dump')
                    temp, path = mkstemp(dir=self.tempdir)
                    temp = fdopen(temp)
                    temp_files.append((temp, path))
                    log.debug('Copying content from remote dump to tempfile')
                    temp.write(profile.dump.read())
                    log.debug('Adding tempfile profile dump')
                if stats is None:
                    log.debug('Creating a Stats object')
                    stats = Stats(path, stream=output)
                else:
                    log.debug('Appending to existing Stats object')
                    stats.add(path)
        finally:
            for temp, path in temp_files:
                log.debug('Removing temporary file at %s' % (path,))
                temp.close()
                unlink(path)

        return stats, output



