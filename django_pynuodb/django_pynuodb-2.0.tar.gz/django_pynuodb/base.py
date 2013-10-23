"""
NuoDB database backend for Django.

Requires pynuodb: https://github.com/nuodb/nuodb-python
"""
import logging
import sys

from django.db import utils
from django.db.backends import *
from django.db.backends.signals import connection_created
from operations import DatabaseOperations
from client import DatabaseClient
from creation import DatabaseCreation
from version import get_version
from introspection import DatabaseIntrospection
from django.utils.encoding import force_str
from django.utils.safestring import SafeText, SafeBytes
from django.utils import six
from django.utils.timezone import utc

try:
    import pynuodb as Database
except ImportError as e:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured("Error loading pynuodb module: %s" % e)

DatabaseError = Database.DatabaseError
IntegrityError = Database.IntegrityError

logger = logging.getLogger('django.db.backends')

def utc_tzinfo_factory(offset):
    if offset != 0:
        raise AssertionError("database connection isn't set to UTC")
    return utc

class CursorWrapper(object):
    """
    A thin wrapper around pynuodb's normal cursor class so that we can catch
    particular exception instances and re-raise them with the right types.
    """

    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, query, args=()):
        try:
            query = str(query)
            query = query % (("?",) * query.count("%s"))
            return self.cursor.execute(query, args)
        except Database.IntegrityError as e:
            six.reraise(utils.IntegrityError, utils.IntegrityError(*tuple(e.args)), sys.exc_info()[2])
        except Database.DatabaseError as e:
            six.reraise(utils.DatabaseError, utils.DatabaseError(*tuple(e.args)), sys.exc_info()[2])

    def executemany(self, query, args):
        try:
            return self.cursor.executemany(query, args)
        except Database.IntegrityError as e:
            six.reraise(utils.IntegrityError, utils.IntegrityError(*tuple(e.args)), sys.exc_info()[2])
        except Database.DatabaseError as e:
            six.reraise(utils.DatabaseError, utils.DatabaseError(*tuple(e.args)), sys.exc_info()[2])

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            return getattr(self.cursor, attr)

    def __iter__(self):
        return iter(self.cursor)

class DatabaseFeatures(BaseDatabaseFeatures):
    allows_group_by_pk = True
    uses_savepoints = True
    allow_sliced_subqueries = False
    supports_select_related = False
    supports_unspecified_pk = True
    supports_forward_references = False
    supports_subqueries_in_group_by = False
    supports_bitwise_or = False
    supports_timezones = False
    needs_datetime_string_cast = False
    requires_rollback_on_dirty_transaction = True
    has_select_for_update = True
    supports_transactions = True
    can_introspect_foreign_keys = False

class DatabaseWrapper(BaseDatabaseWrapper):
    vendor = 'nuodb'
    operators = {
        'exact': '= %s',
        'iexact': '= UPPER(%s)',
        'contains': 'LIKE %s',
        'icontains': 'LIKE UPPER(%s)',
        'regex': '~ %s',
        'iregex': '~* %s',
        'gt': '> %s',
        'gte': '>= %s',
        'lt': '< %s',
        'lte': '<= %s',
        'startswith': 'LIKE %s',
        'endswith': 'LIKE %s',
        'istartswith': 'LIKE UPPER(%s)',
        'iendswith': 'LIKE UPPER(%s)',
    }

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)

        self.features = DatabaseFeatures(self)
        autocommit = self.settings_dict["OPTIONS"].get('autocommit', False)
        self.features.uses_autocommit = autocommit
        self.ops = DatabaseOperations(self)
        self.client = DatabaseClient(self)
        self.creation = DatabaseCreation(self)
        self.introspection = DatabaseIntrospection(self)
        self.validation = BaseDatabaseValidation(self)
        self._nuodb_version = None

    def close(self):
        if self.connection is None:
            return

        try:
            self.connection.close()
            self.connection = None
        except Database.Error:
            # In some cases (database restart, network connection lost etc...)
            # the connection to the database is lost without giving Django a
            # notification. If we don't set self.connection to None, the error
            # will occur a every request.
            self.connection = None
            logger.warning('pynuodb error while closing the connection.',
                exc_info=sys.exc_info()
            )
            raise

    def _get_nuodb_version(self):
        if self._nuodb_version is None:
            self._nuodb_version = get_version(self.connection)
        return self._nuodb_version
    
    nuodb_version = property(_get_nuodb_version)

    def _cursor(self):
        settings_dict = self.settings_dict
        if self.connection is None:
            if not settings_dict['NAME']:
                from django.core.exceptions import ImproperlyConfigured
                raise ImproperlyConfigured(
                    "settings.DATABASES is improperly configured. "
                    "Please supply the NAME value.")
            conn_params = {
                'database': settings_dict['NAME'],
            }
            conn_params.update(settings_dict['OPTIONS'])
            if 'autocommit' in conn_params:
                del conn_params['autocommit']
            
            if settings_dict.has_key('SCHEMA'):
                options = {"schema": settings_dict['SCHEMA']}
            else:
                options = {"schema": "user"}
            
            if settings_dict['DBA_USER']:
                conn_params['user'] = settings_dict['DBA_USER']
            if settings_dict['DBA_PASSWORD']:
                conn_params['password'] = force_str(settings_dict['DBA_PASSWORD'])
            if settings_dict['HOST']:
                conn_params['host'] = settings_dict['HOST']
            if settings_dict['PORT']:
                options['port'] = settings_dict['PORT']
            tz = 'UTC' if settings.USE_TZ else settings_dict.get('TIME_ZONE')
#             options['timezone'] = tz
            conn_params['options'] = options
            self.connection = Database.connect(**conn_params)
            if tz:
                try:
                    get_parameter_status = self.connection.get_parameter_status
                except AttributeError:
                    conn_tz = None
                else:
                    conn_tz = get_parameter_status('TimeZone')
            self._get_nuodb_version()
            connection_created.send(sender=self.__class__, connection=self)
        cursor = self.connection.cursor()
        cursor.tzinfo_factory = utc_tzinfo_factory if settings.USE_TZ else None
        return CursorWrapper(cursor)

    def _set_isolation_level(self, level):
        """
        Do all the related feature configurations for changing isolation
        levels. This doesn't touch the uses_autocommit feature, since that
        controls the movement *between* isolation levels.
        """
        assert level in range(5)
        try:
            if self.connection is not None:
                pass
#                 self.connection.set_isolation_level(level)
        finally:
            self.isolation_level = level
            self.features.uses_savepoints = bool(level)

    def _commit(self):
        if self.connection is not None:
            try:
                return self.connection.commit()
            except Database.IntegrityError as e:
                six.reraise(utils.IntegrityError, utils.IntegrityError(*tuple(e.args)), sys.exc_info()[2])
