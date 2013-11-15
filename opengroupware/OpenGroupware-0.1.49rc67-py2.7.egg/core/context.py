#
# Copyright (c) 2009, 2012, 2013
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import sys
import time
import logging
import uuid
from sqlalchemy import and_, or_
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from pytz import timezone
from datetime import datetime, timedelta
from coils.foundation import \
    AuthenticationToken, \
    Backend, \
    Contact, \
    Team, \
    CompanyAssignment, \
    ServerDefaultsManager, \
    AuditEntry, \
    UserDefaultsManager, \
    OGO_ROLE_WORKFLOW_DEVELOPERS, \
    OGO_ROLE_DATA_MANAGER, \
    OGO_ROLE_SYSTEM_ADMIN, \
    OGO_ROLE_HELPDESK, \
    OGO_ROLE_WORKFLOW_ADMIN
from exception import *
from ldapauthenticator import LDAPAuthenticator
from dbauthenticator import DBAuthenticator
from bundlemanager import BundleManager
from accessmanager import AccessManager
from linkmanager import LinkManager
from propertymanager import PropertyManager
from typemanager import TypeManager
from lockmanager import LockManager, AdministrativeLockManager
from command import Command
from packet import Packet

from useragents import lookup_user_agent

OGO_ROLE_TEAM_ASSIGNMENT = \
    {OGO_ROLE_SYSTEM_ADMIN: 'OGoAdministrativeTeam',
     OGO_ROLE_HELPDESK: 'OGoHelpDeskRoleName',
     OGO_ROLE_WORKFLOW_ADMIN: 'OGoWorkflowAdministrativeTeam',
     OGO_ROLE_WORKFLOW_DEVELOPERS: 'OGoWorkflowDevelopersTeam',
     OGO_ROLE_DATA_MANAGER: 'OGoDataManagersTeam', }


class Context(object):
    '''
    The context class is the class through which all Logic operations
    are performed.
    '''

    __slots__ = ('_orm',
                 '_pm',
                 '_log',
                 '_queue',
                 '_audit_queue',
                 '_timezone',
                 # Flag for logging Logic command times to standard-error
                 # [Debugging option]
                 '_F_perfprint',
                 # The user agent UUID, used to user-agent specific caching
                 '_agent_id',
                 # A copy of the user-agent description dictionary
                 '_agent_data',
                 # The user's preferences / defaults
                 '_defaults',
                 # Additional parameters provided at creation
                 '_meta',
                 # Reference to the LockManager
                 '_lockman',
                 # Reference to the AccessManager
                 '_am',
                 # Reference to the TypeManager
                 '_tm',
                 # User Defaults manager
                 '_dm',
                 # Server Defauls Manager
                 '_sdm',
                 # Flag is the Context is dirty (has performed changes)
                 '_dirty',
                 # Record the depth of the current Command call stack
                 '_stack_depth',
                 # Cache the current account object
                 '_C_login',
                 # Cache the e-mail address of the current context
                 '_C_email',
                 # Cache the cluster id of this server group
                 '_C_cluster_id',
                 # Cache the context ids of the current contexts
                 '_C_context_ids',
                 # The original identity of the user, allows for unsudo
                 '_C_identity_id',
                 # The operational identity of the user, allows for sudo
                 '_C_current_id',
                 # Cache roles of the context
                 '_C_roles')

    _mapper = None
    _orm = None

    def __init__(
            self,
            identity_id,
            metadata,
            broker=None,
            orm=None,
            server_defaults_manager=None,
            user_defaults_manager=None,
            link_manager=None,
            lock_manager=None,
            type_manager=None,
            property_manager=None
    ):
        self._orm = orm  # SQLAlchemy ORM
        self._dm = user_defaults_manager  # Server Defaults Manager
        self._sdm = server_defaults_manager  # Server Defaults Manager
        self._lm = link_manager  # Link Manager
        self._pm = property_manager  # Property Manager
        self._tm = type_manager  # Type Manager
        self._lockman = lock_manager  # Lock Manager
        self._C_roles = None
        self._C_cluster_id = None
        self._C_context_ids = []
        self._C_email = None
        self._C_login = None
        self._stack_depth = 0
        self._C_identity_id = identity_id
        self._log = logging.getLogger('context')
        self._F_perfprint = None
        self._audit_queue = {}

        self._dirty = False
        self._queue = []
        self._meta = metadata
        self._callbacks = {}
        self._uuid = uuid.uuid4().hex
        self._log.debug('Context {0} created'.format(self._uuid))
        if (Context._mapper is None):
            Context._mapper = BundleManager()
        self._am = None

        self._load_context_ids(self._C_identity_id)

        '''
        Store a reference to our AMQ broker if one was provided
        In use access to the broker is performed via the amq_broker
        property of the CTX object
        '''
        if ('amq_broker' not in metadata) and (broker is None):
            self._log.debug('AMQ broker not available in context.')
        else:
            self._meta['amq_broker'] = metadata.get('amq_broker', broker)
        '''
        Lookup the user agent if a user_agent string is provided
        If no user_agent was provided the CTX will default to the default
        user agent behaviour. This can be modified with a subsequent call to
        set_user_agent with a user agent string.
        '''
        if 'connection' in metadata:
            agent_name = metadata['connection'].get('user_agent', None)
        else:
            agent_name = None
        self._agent_id, self._agent_data = lookup_user_agent(agent_name)
        self.log.info(
            'User agent {0} [{1}] select for context (Agent: "{2}")'.
            format(self.user_agent_id,
                   self.user_agent_description['name'],
                   agent_name))

    def __del__(self):
        self.close()

    #
    # Security Context Management Methods
    #

    def _load_context_ids(self, identity_id):
        if self._am:
            self._am.flush()  # Flush access_manager's rights cache
        self._C_roles = None  # Flush roles cache
        del self._C_context_ids[:]
        self._C_current_id = identity_id
        self._C_context_ids.append(identity_id, )

    def su(self, context_ids=None, identity_id=None, go_anon=False):

        if go_anon:
            del self._C_context_ids[:]
            self._C_context_ids = [0, ]
            self._C_current_id = 0
            return self.account_id, self.context_ids

        if not context_ids and not identity_id:
            # If no parameters were passed to SUDO, then nothing changes
            return self.account_id, self.context_ids

        if not self.is_admin:
            if identity_id:
                if identity_id not in self._C_context_ids:
                    raise AccessForbiddenException(
                        'Cannot assume identity OGo#{0}'.format(identity_id))
            else:
                context_ids = \
                    set([int(x) for x in
                         context_ids]).intersection(set(self._C_context_ids))
                if not context_ids:
                    raise AccessForbiddenException(
                        'No available contextIds resulting from SU attempt')

        del self._C_context_ids[:]

        if identity_id:
            self._load_context_ids(identity_id)
            context_ids = set([int(x) for x in context_ids])
        else:
            if not go_anon:
                self._C_context_ids.append(self._C_current_id)
            self._C_context_ids.extend(context_ids)

        return self._C_current_id, self._C_context_ids

    def unsu(self):
        self._load_context_ids(self._C_identity_id)

    @property
    def context_ids(self):
        return self._C_context_ids

    @property
    def account_id(self):
        return self._C_current_id

    @property
    def identity_id(self):
        return self._C_identity_id

    def _fetch_roles(self):
        role_list = set()
        teams = self.db_session().\
            query(Team).\
            enable_eagerloads(False).all()
        for role_id, default_name in OGO_ROLE_TEAM_ASSIGNMENT.items():
            team_name = \
                self.server_defaults_manager.\
                string_for_default(default_name,
                                   value='OGoAdministrators')
            team = [x for x in teams if x.name == team_name]
            if team:
                if team[0].object_id in self.context_ids:
                    role_list.add(role_id)
        return role_list

    def has_role(self, role):
        '''
        Return True if a context holds the role, or one of the roles specified
        via the role parameter (if role is an iterable).
        :param role: the role id or iterable of role ids. If the value is an
        iterable True will be returned in the context holds any of the role
        ids specified via the iterable [list, set, tuple, ] value.
        '''

        # Administrator just has all roles
        if 10000 in self.context_ids:
            return True

        if self._C_roles is None:
            self._C_roles = self._fetch_roles()

        if isinstance(role, int) or isinstance(role, long):
            if role in self._C_roles:
                return True
        elif self._C_roles.intersection(role):
            return True

        return False

    @property
    def roles(self):
        if self._C_roles is None:
            self._C_roles = self._fetch_roles()
        return self._C_roles

    @property
    def login(self):
        return self.get_login()

    def get_login(self):
        return None

    @property
    def email(self):

        if not self._C_email:
            if hasattr(self._C_login, 'company_values'):
                cv = self._C_login.company_values.get('email1', None)
                if cv:
                    self._C_email = cv.string_value
                else:
                    self._C_email = None
        return self._C_email

    @property
    def is_admin(self):
        return self.has_role(OGO_ROLE_SYSTEM_ADMIN)

    #
    # Transaction Management Methods
    #

    def close(self):
        '''
        Close the current context, after this method is called the Context
        object can no longer be used.  This will drop all pending callbacks
        and close the ORM connection.
        '''
        self._log.debug('Closing context {0}'.format(self._uuid))
        self._callbacks = {}
        if (self._orm is not None):
            self._orm.close()
            self._orm = None
        if self._am:
            self._am.flush()

    @property
    def session_id(self):
        '''
        Return the quasi-unique id for this session; used primarily for
        auditing, debugging, and logging.
        '''
        return self._uuid

    @property
    def is_dirty(self):
        '''
        Returns true if uncommitted changes have been made via this context
        object.
        '''
        return self._dirty

    def dirty(self):
        self._dirty = True

    def db_session(self):
        if (self._orm is None):
            self._log.debug('Allocating new database session.')
            self._orm = Backend.db_session()
            '''
            This is in order to help debug ORM QueuePool issues like Issue#134
            '''
            self._log.debug(self._orm.connection().engine.pool.status())
        return self._orm

    def db_close(self):
        if self._orm:
            self._orm.close()
            self._orm = None
            self._log.debug(
                'ORM connection closed; should be released to pool.')

    @property
    def cluster_id(self):
        '''
        Return the quasi-unique id of the OpenGroupware server cluster.
        '''
        if self._C_cluster_id is None:
            prop = \
                self.property_manager.get_server_property(
                    'http://www.opengroupware.us/global',
                    'clusterGUID')
            if (prop is None):
                raise CoilsException(
                    'No cluster id has been generated for this server.')
            self._C_cluster_id = prop.get_value()
        return self._C_cluster_id

    @property
    def tm(self):
        return self.type_manager

    @property
    def type_manager(self):
        '''
        Returns a reference to a TypeManager object.
        '''
        if (self._tm is None):
            self._tm = TypeManager(self)
        return self._tm

    @property
    def access_manager(self):
        '''
        Returns a reference to an AccessManager object.
        '''
        if (self._am is None):
            self._am = AccessManager(self)
        return self._am

    @property
    def link_manager(self):
        '''
        Returns a reference to a LinkManager object that can be used to
        manage object links between objects.
        '''
        if (self._lm is None):
            self._lm = LinkManager(self)
        return self._lm

    @property
    def pm(self):
        return self.property_manager

    @property
    def property_manager(self):
        '''
        Returns a reference to the PropertManager object.
        '''
        if (self._pm is None):
            self._pm = PropertyManager(self)
        return self._pm

    @property
    def lock_manager(self):
        '''
        Returns a reference to the LockManager object.
        '''
        if (self._lockman is None):
            self._lockman = LockManager(self)
        return self._lockman

    @property
    def log(self):
        return self._log

    def begin(self):
        pass

    def queue_for_commit(self, source, target, data):
        self._queue.append((source, target, data, ))

    def audit_at_commit(self, object_id, action, message):
        object_id = long(object_id)
        if object_id not in self._audit_queue:
            self._audit_queue[object_id] = {}
        if action not in self._audit_queue[object_id]:
            self._audit_queue[object_id][action] = []
        self._audit_queue[object_id][action].append(message)

    def flush(self):
        self.db_session().flush()

    def commit(self):
        self.db_session().flush()
        self._log.debug('Context commit requested.')

        for object_id, events in self._audit_queue.items():
            for action, messages in events.items():
                log_entry = AuditEntry()
                log_entry.context_id = object_id
                log_entry.action = action
                log_entry.actor_id = self.account_id
                log_entry.message = '\n'.join(messages)
                self.db_session().add(log_entry)

        self.db_session().commit()
        self._log.debug('Context commit completed.')

        if self._am:
            self._am.flush()

        if self._queue:
            if self.amq_available:
                for notice in self._queue:
                    self.send(notice[0], notice[1], notice[2], )
            self._queue = []

        self._audit_queue = {}
        return

    def rollback(self):
        self.db_session().rollback()
        if self._am:
            self._am.flush()
        return

    def run_command(self, command_name_x, **params):
        ''' Run the named command with the provided parameters.

            :param command_name_x: The fully qualified name of the command to
            run, such as "contact::new"
            :param params: The paramters to be provided to the command object
        '''
        command = Context._mapper.get_command(command_name_x)
        if isinstance(command, Command):
            start = time.time()
            self._stack_depth += 1
            command.prepare(self, **params)
            command.run()
            command.epilogue()
            result = command.get_result()
            end = time.time()
            # TODO: Make this log to a separate file
            if self._F_perfprint is None:
                self._F_perfprint = \
                    self.server_defaults_manager.bool_for_default(
                        'CoilsCommandTimingToStdError')
            if self._F_perfprint:
                sys.stderr.write(
                    '{0:>{1}} {2}s\n'.
                    format(command_name_x,
                           len(command_name_x) + (self._stack_depth * 2),
                           (end - start)))
            self._log.debug(
                'duration of %s was %0.3f' % (command_name_x, (end - start)))
            self._stack_depth += -1
            if self.amq_available:
                self.send(
                    None,
                    'coils.administrator/performance_log',
                    {'lname': 'logic',
                     'oname': command_name_x,
                     'runtime': (end - start),
                     'error': False, })
                self.send(
                    None,
                    'coils.administrator/performance_log',
                    {'lname': 'user',
                     'oname': self.login,
                     'runtime': (end - start),
                     'error': False, })

            command = None
            return result
        else:
            self._log.error('No such command as {0}'.format(command_name_x))
            raise CoilsException(
                'No such command as {0}'.format(command_name_x))
        return None

    def r_c(self, command_name_x, **params):
        return self.run_command(command_name_x, **params)

    @property
    def server_defaults_manager(self):
        if not self._sdm:
            self._sdm = ServerDefaultsManager()
        return self._sdm

    @property
    def defaults_manager(self):
        if not self._dm:
            self._dm = UserDefaultsManager(self.account_id)
        return self._dm

    def get_timezone(self):
        '''
        By default the timezone for a Context is UTC.  But the UserContext
        overrides this method to let the user use a configured time zone.
        '''
        return timezone('UTC')

    def get_utctime(self):
        '''
        Returns UTC time, localized.
        '''
        return timezone('UTC').localize(datetime.now())

    def get_timestamp(self):
        '''
        Return an integer UTC timestamp value
        '''
        return int(self.get_utctime().strftime('%s'))

    def as_localtime(self, time):
        '''
        Return the specified time localized to the user's timezone.
        '''
        if (time is None):
            return self.get_localtime()
        return time.astimezone(self.get_timezone())

    def get_offset_from(self, time):
        '''
        Return the offset in seconds from UTC to the user's timezone for
        the specified time.
        '''
        return \
            (86400 -
             (self.get_localtime().replace(tzinfo=timezone('UTC')) -
              self.get_utctime()).seconds) * -1

    def get_localtime(self):
        '''
        Return the current time localized to the users' time zone
        '''
        return timezone('utc').\
            localize(datetime.now()).\
            astimezone(self.get_timezone())

    @property
    def amq_broker(self):
        return self._meta['amq_broker']

    @property
    def amq_available(self):
        if ('amq_broker' in self._meta):
            return True
        return False

    def send(self, source, target, data, callback=None):
        if (self.amq_available):
            packet = Packet(source, target, data)
            self.amq_broker.send(packet, callback=self.callback)
            if (callback is not None):
                self._callbacks[packet.uuid] = callback
            return packet.uuid
        else:
            raise CoilsException('Service bus not available to context.')
        return None

    def callback(self, uuid, source, target, data):
        if (uuid in self._callbacks):
            if (self._callbacks[uuid](uuid, source, target, data)):
                del self._callbacks[uuid]
                return True
            else:
                return False
        self.log.warn(
            'Request for callback on packet {0} which has no callback.'.
            format(uuid))

    def wait(self, timeout=1000):
        start = time.time()
        end = start + (timeout / 1000.0)
        while ((len(self._callbacks)) > 0 and (time.time() < end)):
            self.amq_broker.wait(timeout=timeout)
        return (len(self._callbacks) > 0)

    def get_favorited_ids_for_kind(self, kind, refresh=True):
        # Anonymous doesn't have favorites
        if (self.account_id == 0):
            return []
        kind = kind.lower()
        if (kind == 'contact'):
            kind = 'person'
        default_name = '{0}_favorites'.format(kind.lower())
        if (
            (refresh is False) and
            (hasattr(self, '_cache_{0}'.format(default_name)))
        ):
            return getattr(self, '_cache_{0}'.format(default_name))
        fav_ids = \
            [int(x) for x in
             self.defaults_manager.default_as_list(default_name, [])]
        setattr(self, '_cache_{0}'.format(default_name), fav_ids)
        return fav_ids

    def set_favorited_ids_for_kind(self, kind, object_ids):
        kind = kind.lower()
        if kind == 'contact':
            kind = 'person'
        default_name = '{0}_favorites'.format(kind.lower())
        if isinstance(object_ids, basestring):
            object_ids = object_ids.split(',')
        favorite_ids = [int(x) for x in object_ids]
        default_name = '{0}_favorites'.format(kind.lower())
        self.defaults_manager.set_default_value(default_name, favorite_ids)
        self.defaults_manager.sync()

    def favorite(self, object_id):
        kind = self.type_manager.get_type(object_id)
        if kind:
            favorites = self.get_favorited_ids_for_kind(kind)
            if object_id not in favorites:
                favorites.append(object_id)
                self.set_favorited_ids_for_kind(kind, favorites)

    def unfavorite(self, object_id):
        object_id = int(object_id)
        kind = self.type_manager.get_type(object_id)
        if kind:
            favorites = self.get_favorited_ids_for_kind(kind)
            if object_id in favorites:
                favorites.remove(object_id)
                self.set_favorited_ids_for_kind(kind, favorites)
            if object_id not in favorites:
                favorites.append(object_id)

    def send_administrative_notice(
        self,
        subject=None,
        message=None,
        urgency=9,
        category='unspecified',
        attachments=[]
    ):
        # TODO: Support attachments
        try:
            self.send(None,
                      'coils.administrator/notify',
                      {'urgency':  urgency,
                       'category': category,
                       'subject':  subject,
                       'message':  message, })
        except Exception, e:
            self.log.error(
                'Exception attempting to send administrative notice')
            self.log.exception(e)

    def set_user_agent(self, agent_string):
        self._agent_id, self._agent_data = lookup_user_agent(agent_string)

    @property
    def user_agent_id(self):
        return self._agent_id

    @property
    def user_agent_description(self):
        return self._agent_data


class AnonymousContext(Context):

    def __init__(
        self,
        metadata={},
        broker=None,
        orm=None,
        server_defaults_manager=None,
        user_defaults_manager=None,
        link_manager=None,
        lock_manager=None,
        type_manager=None,
        property_manager=None,
    ):
        Context.__init__(
            self,
            0,
            metadata,
            broker=broker,
            orm=orm,
            server_defaults_manager=server_defaults_manager,
            user_defaults_manager=user_defaults_manager,
            link_manager=link_manager,
            lock_manager=lock_manager,
            type_manager=type_manager,
            property_manager=property_manager,
        )

    def get_login(self):
        return 'Coils\\Anonymous'


class NetworkContext(Context):
    def __init__(
        self,
        metadata={},
        broker=None,
        orm=None,
        server_defaults_manager=None,
        user_defaults_manager=None,
        link_manager=None,
        lock_manager=None,
        type_manager=None,
        property_manager=None
    ):
        Context.__init__(
            self,
            8999,
            metadata,
            broker=broker,
            orm=orm,
            server_defaults_manager=server_defaults_manager,
            user_defaults_manager=user_defaults_manager,
            link_manager=link_manager,
            lock_manager=lock_manager,
            type_manager=type_manager,
            property_manager=property_manager,
        )

    def get_login(self):
        return 'Coils\\Network'

    @property
    def email(self):
        email = self.server_defaults_manager.\
            string_for_default('AdministrativeEMailAddress',
                               value='root@localhost')
        return email


class AdministrativeContext(Context):

    def __init__(
        self,
        metadata={},
        broker=None,
        orm=None,
        server_defaults_manager=None,
        user_defaults_manager=None,
        link_manager=None,
        lock_manager=None,
        type_manager=None,
        property_manager=None
    ):
        Context.__init__(
            self,
            10000,
            metadata,
            broker=broker,
            orm=orm,
            server_defaults_manager=server_defaults_manager,
            user_defaults_manager=user_defaults_manager,
            link_manager=link_manager,
            lock_manager=lock_manager,
            type_manager=type_manager,
            property_manager=property_manager,
        )

    def _load_context_ids(self, account_id):
        Context._load_context_ids(self, account_id)
        self._C_context_ids.append(10003)

    def get_login(self):
        return 'Coils\\Administrator'

    @property
    def email(self):
        email = self.server_defaults_manager.\
            string_for_default('AdministrativeEMailAddress',
                               value='root@localhost')
        return email

    @property
    def lock_manager(self):
        '''
        Returns a reference to the LockManager object.
        '''
        if (self._lockman is None):
            self._lockman = AdministrativeLockManager(self)
        return self._lockman


class UserContext(Context):

    def __init__(
        self,
        account_id,
        metadata,
        broker=None,
        orm=None,
        server_defaults_manager=None,
        user_defaults_manager=None,
        link_manager=None,
        lock_manager=None,
        type_manager=None,
        property_manager=None,
    ):
        Context.__init__(
            self,
            account_id,
            metadata,
            broker=broker,
            orm=orm,
            server_defaults_manager=server_defaults_manager,
            user_defaults_manager=user_defaults_manager,
            link_manager=link_manager,
            lock_manager=lock_manager,
            type_manager=type_manager,
            property_manager=property_manager,
        )

    def _load_context_ids(self, account_id):
        Context._load_context_ids(self, account_id)
        # Load the list of context ids; myself, teams, and proxied contacts
        # An account is always itself
        # Add the ids of all the teams the user is a memeber of
        query = self.db_session().\
            query(Team).\
            join(CompanyAssignment).\
            filter(CompanyAssignment.child_id == account_id, ).\
            enable_eagerloads(False)
        for team in query.all():
            self._C_context_ids.append(team.object_id)
        query = None
        '''
        Add the ids of all the other users who have added this user as a proxy
        '''
        for contact in self.run_command('account::get-proxied-contacts'):
            self._C_context_ids.append(contact.object_id)

    def get_defaults(self):
        if (self._defaults is None):
            self._defaults = self.run_command('account::get-defaults')
        return self._defaults

    def get_timezone(self):
        '''
        Return the configured timezone of the user.
        '''
        if self._timezone is None:
            tzname = \
                self.defaults_manager.string_for_default('timezone',
                                                         value='UTC')
            self._timezone = timezone(tzname)
        return self._timezone

    @property
    def account_object(self):
        if not self._C_login:
            db = self.db_session()
            query = db.query(Contact).\
                filter(
                    and_(
                        Contact.object_id == self.account_id,
                        Contact.is_account == 1,
                        Contact.status != 'archived'))
            self._C_login = query.first()
        return self._C_login

    def get_login(self):
        return self.account_object.login


class AuthenticatedContext(UserContext):
    _auth_class = None
    _auth_options = None
    _defaults = None
    _timezone = None

    def __init__(
        self,
        identity_id,
        metadata,
        broker=None,
        orm=None,
        server_defaults_manager=None,
        user_defaults_manager=None,
        link_manager=None,
        lock_manager=None,
        type_manager=None,
        property_manager=None,
    ):
        UserContext.__init__(
            self,
            identity_id,
            metadata,
            broker=broker,
            orm=orm,
            server_defaults_manager=server_defaults_manager,
            user_defaults_manager=user_defaults_manager,
            link_manager=link_manager,
            lock_manager=lock_manager,
            type_manager=type_manager,
            property_manager=property_manager,
        )
        self._session_id = uuid.uuid4().hex


class AssumedContext(UserContext):
    _defaults = None
    _timezone = None

    def __init__(
        self,
        context_id,
        metadata={},
        broker=None,
        orm=None,
        server_defaults_manager=None,
        user_defaults_manager=None,
        link_manager=None,
        lock_manager=None,
        type_manager=None,
        property_manager=None
    ):
        UserContext.__init__(
            self,
            context_id,
            metadata,
            broker=broker,
            orm=orm,
            server_defaults_manager=server_defaults_manager,
            user_defaults_manager=user_defaults_manager,
            link_manager=link_manager,
            lock_manager=lock_manager,
            type_manager=type_manager,
            property_manager=property_manager,
        )


def CreateAuthenticatedContext(metadata, password_cache=None):
    '''
    Attempt to create an AuthenticatedContext from the provided request
    metadata.  Currently this will try to match an existing session and then
    fallback to using an Authorizor.  If authorizor approves the request it
    will attempt to be matched to a preexisting session.
    '''

    authenticated_id = None
    session_id = None

    def get_authenticated_session(metadata, account_id):

        if (
            (not account_id) and
            (not 'sessiontoken' in metadata['authentication'])
        ):
            return None

        db = Backend.db_session()
        query = db.query(AuthenticationToken).\
            filter(AuthenticationToken.expiration > datetime.now())

        if 'sessiontoken' in metadata['authentication']:
            query = query.filter(AuthenticationToken.token ==
                                 metadata['authentication']['sessiontoken'])
        elif account_id:
            query = query.filter(AuthenticationToken.account_id == account_id)
        else:
            raise CoilsUnreachableCode(
                'This code point should be unreachable.')

        if 'client_address' in metadata['connection']:
            query = query.filter(
                AuthenticationToken.environment ==
                metadata['connection']['client_address'])

        try:
            token = query.one()
        except NoResultFound:
            return None
        except MultipleResultsFound:
            return None
        else:
            return token
        finally:
            db.close()

    token = get_authenticated_session(metadata=metadata, account_id=None)
    if token:
        authenticated_id = token.account_id
        session_id = token.token

    if not authenticated_id:
        auth_options = Backend.get_authenticator_options()
        class_name = '{0}Authenticator'.\
            format(auth_options['authentication'].upper())
        Backend._log.debug('Authentication class is {0}'.format(class_name, ))
        auth_class = eval(class_name)
        authorizor = auth_class(metadata, auth_options,
                                password_cache=password_cache)
        authenticated_id = authorizor.authenticated_id()

    if not authenticated_id:
        raise AuthenticationException('Unable to authenticate session')

    context = AuthenticatedContext(authenticated_id, metadata)

    if context.user_agent_description['sessionsEnabled']:

        if not session_id:
            token = get_authenticated_session(metadata=metadata,
                                              account_id=authenticated_id, )
            if token:
                session_id = token.token
            else:
                # Create a new token
                db = Backend.db_session()
                try:
                    token = AuthenticationToken()
                    token.token_id = uuid.uuid4().hex
                    token.account_id = context.account_id
                    token.expiration = datetime.now() + timedelta(hours=24)
                    if 'client_address' in metadata['connection']:
                        token.environment = \
                            metadata['connection']['client_address']
                    db.add(token)
                    db.commit()
                    session_id = token.token
                finally:
                    db.close()
    else:
        session_id = None

    return context, session_id
