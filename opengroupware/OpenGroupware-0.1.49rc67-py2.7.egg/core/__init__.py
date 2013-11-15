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
#
from command import Command

from context import \
    Context, AnonymousContext, \
    AuthenticatedContext, \
    AdministrativeContext, \
    AssumedContext, \
    AccessForbiddenException, \
    NetworkContext, \
    OGO_ROLE_SYSTEM_ADMIN, \
    OGO_ROLE_HELPDESK, \
    OGO_ROLE_WORKFLOW_ADMIN, \
    OGO_ROLE_WORKFLOW_DEVELOPERS, \
    OGO_ROLE_DATA_MANAGER, \
    CreateAuthenticatedContext

from bundlemanager import BundleManager

from accessmanager import AccessManager

from entityaccessmanager import EntityAccessManager

from authenticator import Authenticator

from dbauthenticator import DBAuthenticator

from ldapauthenticator import LDAPAuthenticator

from propertymanager import PropertyManager

from typemanager import TypeManager

from exception import *

from utility import \
    walk_ogo_uri_to_folder, \
    initialize_COILS, \
    initialize_tool, \
    parse_ogo_uri, \
    utf8_split, \
    walk_ogo_uri_to_target

from service import Service

from threadedservice import ThreadedService

from packet import Packet

from content_plugin import ContentPlugin

from objinfomanager import ObjectInfoManager

from broker import Broker

from worker import MultiProcessWorker

from logic import \
    ActionCommand, CreateCommand, DeleteCommand, \
    GetCommand, SearchCommand, UpdateCommand,\
    MacroCommand, SetCommand, \
    RETRIEVAL_MODE_SINGLE, RETRIEVAL_MODE_MULTIPLE, \
    AsyncronousCommand

from master import MasterService

from coils.foundation import \
    BLOBManager, Appointment, Contact, Enterprise, \
    Project, Task, AuditEntry, ObjectProperty, \
    CompanyValue, Resource, Participant, TaskAction, \
    ServerDefaultsManager, UserDefaultsManager, \
    Route, Process, Message, StandardXML, ACL, KVC, \
    fix_microsoft_text, Attachment, UniversalTimeZone, \
    ProjectAssignment, ProjectInfo, ProcessLogEntry, SMTP, \
    ObjectProperty, DocumentVersion, Document, Folder, \
    change_to_backend_usergroup, Collection, CollectionAssignment, \
    CTag, Team, Backend, Note, SQLConnectionFactory, \
    LDAPConnectionFactory, ObjectInfo, CompanyAssignment, \
    ORMEntity, Address, UTCDateTime, Telephone, Folder, \
    ObjectLink, CompanyInfo, DateInfo, Lock, \
    COILS_TIMEZONES, RouteGroup

from project7000 import \
    get_object_from_project7000_path, \
    get_yaml_struct_from_project7000, \
    send_email_using_project7000_template
