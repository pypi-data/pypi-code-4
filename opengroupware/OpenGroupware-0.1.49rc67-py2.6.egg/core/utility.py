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
import getopt
import os
import urlparse

from sqlalchemy.exc import IntegrityError

from coils.foundation import *
from context import Context
from broker import Broker
from bundlemanager import BundleManager
from accessmanager import AccessManager
from context import AdministrativeContext
from exception import CoilsException

urlparse.uses_query.append('ogo')


def initialize_COILS():
    initialize_COILS({})


def initialize_COILS(options={}):
    Backend.__alloc__(**options)
    if (Context._mapper is None):
        Context._mapper = BundleManager()
        Context._mapper.load_bundles()
    #if (Context._accessManager == None):
    #    Context._accessManager = AccessManager(AdministrativeContext())


def initialize_tool(name, argv, arguments=['', []]):

    def receive_message(message):
        return broker.packet_from_message(message)

    storeroot = None
    add_modules = []
    ban_modules = []
    short_args = 's:i:x:{0}'.format(arguments[0])
    long_args = ["store=", "add-bundle=", "ban-bundle="]
    long_args.extend(arguments[1])
    parameters = {}
    try:
        opts, args = getopt.getopt(argv, short_args, long_args)
    except getopt.GetoptError, e:
        print e
        sys.exit(2)
    for opt, arg in opts:
            if opt in ("-s", "--store"):
                storeroot = arg
            elif opt in ("-i", "--add-bundle"):
                add_modules.append(arg)
            elif opt in ("-x", "--ban-bundle"):
                ban_modules.append(arg)
            else:
                parameters[opt] = arg

    initialize_COILS({'store_root': storeroot,
                      'extra_modules': add_modules,
                      'banned_modules': ban_modules, })

    broker = Broker()
    broker.subscribe('tool.{0}.{1}'.format(name, os.getpid()), receive_message)
    return AdministrativeContext(broker=broker), parameters

# shlex's split is broken in regards to Unicode in late Python 2.5 and
# most of Python 2.6.x.  It will turn everyting into UCS-4 regardless of
# input, so we need to specifically encode all the results to avoid this
# bug.  Python 2.7 doesn't have this problem.
from shlex import split as _split
utf8_split = lambda a: [b.decode('utf-8') for b in _split(a.encode('utf-8'))]


def parse_ogo_uri(uri, default_params=None):
    result = urlparse.urlparse(uri)

    if result.scheme != 'ogo':
        raise CoilsException(
            'URI has scheme "{0}", not "ogo"'.format(result.scheme, ))

    if result.path:
        path = result.path[1:]
    else:
        path = ''

    parameters = {}
    if default_params:
        parameters.update(default_params)
    if result.query:
        for k, v in urlparse.parse_qsl(result.query):
            parameters[k.lower()] = v

    return result.netloc, path, parameters


def walk_ogo_uri_to_folder(
    context,
    uri,
    create_path=False,
    default_params=None,
):

    '''
    This method walks an OGo URI to a target folder, optionally it can create
    the required path.  It uses a save-point/transactions to ensure that the
    path is created in a concurrent fashion.
    '''

    number, path, params, = parse_ogo_uri(uri, default_params=default_params)

    project = None
    if number.isdigit():
        object_id = long(number)
        project = context.r_c('project::get', id=long(number), )
    if not project:
        project = context.r_c('project::get', number=number, )
    if not project:
        raise CoilsException(
            'Project "{0}" from URI "{1}" not available.'.
            format(number, uri))

    root_folder = context.run_command('project::get-root-folder',
                                      project=project)
    if not root_folder:
        raise CoilsException(
            'Root folder of OGo#{0} [Project] not available.'.
            format(project.object_id, ))

    if not path:
        return root_folder, params

    path_components = path.split('/')

    resume = True
    target = None
    while resume:
        tx = context.db_session().begin_nested()

        target = root_folder
        dirty = False

        try:
            for path_component in path_components:
                if not path_component:
                    '''
                    Something like " fred//george" will be treated like
                    "fred/george" we skip the empty parts continue
                    '''
                    continue

                folder = context.run_command('folder::ls',
                                             folder=target,
                                             name=path_component,
                                             lockmode='update', )
                if folder and len(folder) == 1:
                    folder = folder[0]
                    if not isinstance(folder, Folder):
                        raise CoilsException(
                            'folder path includes a non-folder OGo#{0} [{1}]'
                            'in URI "{2}"'.
                            format(folder.object_id,
                                   folder.__entityName__,
                                   uri))

                    target = folder
                elif create_path:
                    # Create new folder to complete the path
                    target = context.run_command(
                        'folder::new',
                        folder=target,
                        values={'name': path_component, })
                    dirty = True
                else:
                    raise CoilsException(
                        'Cannot find path component "{0}" from URI "{1}"'.
                        format(path_component, uri, ))

        except IntegrityError as exc:
            tx.rollback()
            resume = True
        except Exception as exc:
            tx.rollback()
            target = None
            raise exc
        else:
            if dirty:
                tx.commit()
            else:
                tx.close()
            resume = False

    return target, params


def walk_ogo_uri_to_target(
    context,
    uri,
):

    '''
    This method walks an OGo URI to a target folder, optionally it can create
    the required path.  It uses a save-point/transactions to ensure that the
    path is created in a concurrent fashion.
    '''

    number, path, params, = parse_ogo_uri(uri, default_params={})

    project = None
    if number.isdigit():
        object_id = long(number)
        project = context.r_c('project::get', id=long(number), )
    if not project:
        project = context.r_c('project::get', number=number, )
    if not project:
        raise CoilsException(
            'Project "{0}" from URI "{1}" not available.'.
            format(number, uri))

    result = context.run_command('project::get-path',
                                 project=project,
                                 path=path,
                                 create=False,)
    return result


def walk_ogo_uri_to_target(
    context,
    uri,
):

    '''
    This method walks an OGo URI to a target folder, optionally it can create
    the required path.  It uses a save-point/transactions to ensure that the
    path is created in a concurrent fashion.
    '''

    number, path, params, = parse_ogo_uri(uri, default_params={})

    project = None
    if number.isdigit():
        object_id = long(number)
        project = context.r_c('project::get', id=long(number), )
    if not project:
        project = context.r_c('project::get', number=number, )
    if not project:
        raise CoilsException(
            'Project "{0}" from URI "{1}" not available.'.
            format(number, uri))

    result = context.run_command('project::get-path',
                                 project=project,
                                 path=path,
                                 create=False,)
    return result
