# -*- encoding: utf-8 -*-
"""
@authors: Andrés Felipe Calderón andres.calderon@correlibre.org
          Sebastián Ortiz V. neoecos@gmail.com

SIIM2 Server is the web server of SIIM2 Framework
Copyright (C) 2013 Infometrika Ltda.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
#system, and standard library
import json
import uuid
from functools import wraps
from datetime import datetime
from pytz import utc

#flask
from flask.globals import current_app
from flask import (session, request, Blueprint)

#Apps import
from cid.utils.fileUtils import loadJSONFromFile
from cid.utils import helpers


#CaliopeStorage
from neomodel import DoesNotExist
from odisea.CaliopeStorage import CaliopeUser
from cid.model import SIIMModel

#Moved to package __init__.py
dispatcher = Blueprint('dispatcher', __name__, template_folder='pages')
storage_sessions = {}


@dispatcher.route('/rest', methods=['POST'])
def rest():
    current_app.logger.debug('POST:' + request.get_data(as_text=True))
    message = request.json
    res = process_message(session, message)
    return json.dumps(res)


@dispatcher.route('/ws')
def index():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        while True:
            message = ws.receive()
            if message is None:
                current_app.logger.warn('Request: ' + request.__str__() + '\tmessage: None')
                break
            try:
                messageJSON = json.loads(message)
                current_app.logger.info('Request: ' + request.__str__() + '\tmessage: ' + message
                                        + '\tmessageJSON: ' + str(messageJSON))
            except ValueError:
                current_app.logger.error('Request ' + request.__str__()
                                         + '\tmessage:' + message)
                messageJSON = json.loads('{}')

            if type(messageJSON) is dict:
                res = process_message(session, messageJSON)
                ws.send(json.dumps(res))
            elif type(messageJSON) is list:
                rv = []
                for m in messageJSON:
                    res = process_message(session, m)
                    rv.append(res)
                ws.send(json.dumps(rv))


#: TODO: Not implemented yet
def _is_fresh_session(session):
    return True


def login_error(user=False, fresh=False):
    msg = u''
    if user:
        msg += u"Session don't exists for user"
    if fresh:
        msg += u"Session is not fresh"
    res = {
        'result': 'ok',
        'msg': msg,
    }
    return res


def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if 'user' in session:
            return func(*args, **kwargs)
        else:
            return login_error(user=True)

    return decorated_view


def event_logging(func):
    @wraps(func)
    def decorated_logging(*args, **kwargs):
        print "log: %s" % (args,)
        return func(*args, **kwargs)

    return decorated_logging


def login_with_uuid(session, params):
    result = None
    error = None
    session_uuid = params['uuid']
    if session_uuid in storage_sessions:
        session['user'] = storage_sessions[session_uuid]['user']
        session['session_uuid'] = session_uuid
        response_msg = "uuid found, user=" + session['user']
        result = {'msg': response_msg, 'uuid': session_uuid}

    else:
        error = {
            'code': -32600,
            'message': "uuid not found"
        }
    return result, error


def login_with_name(session, params):
    """
    Default username after run CaliopeTestNode is
    user:password
    """
    #: TODO: Enable system to be session oriented, so one user can have multiple active sessions
    #: TODO: Check security of this autentication method
    result = None
    error = None
    if 'user' in session:
        result = {'uuid': session['session_uuid']}
        return result, error
    try:
        user = CaliopeUser.index.get(username=params['login'])
        #: TODO Add to log
        if user.password == params['password']:
            session['user'] = params['login']
            session['session_uuid'] = str(uuid.uuid4()).decode('utf-8')
            storage_sessions[session['session_uuid']] = {}
            storage_sessions[session['session_uuid']]['user'] = session['user']
            storage_sessions[session['session_uuid']]['start_time'] = datetime.now(utc)
            result = {'uuid': session['session_uuid']}
        else:
            error = {
                'code': -32600,
                'message': "The password does not match the username"
            }

    except DoesNotExist:
        error = {
            'code': -32600,
            'message': "The username does not exists"
        }
    finally:
        return result, error

#@login_required
def getPrivilegedForm(session, params):
    error = None
    result = {
        'result': 'ok',
        'form': loadJSONFromFile(current_app.config["FORM_TEMPLATES"]
                                 + "/" + params["formId"] + ".json", current_app.root_path),
        'actions': ["create"]
    }
    return result, error


@event_logging
#:TODO Implement the method with different version and domain options.
def getFormTemplate(session, params):
    result = None
    error = None

    if 'formId' in params:
        formId = params['formId']
        if 'domain' in params:
            domain = params['domain']
        else:
            domain = ''
        if 'version' in params:
            version = params['version']
        else:
            version = ''
    if formId == 'login':
        result = {
            'result': 'ok',
            'form': loadJSONFromFile(current_app.config['FORM_TEMPLATES']
                                     + "/" + "login.json", current_app.root_path),
            'actions': ["authenticate"]
        }

    elif formId == 'proyectomtv':
        result, error = getPrivilegedForm(session, params)
    elif formId == 'SIIMForm':
        result, error = getPrivilegedForm(session, params)
    else:
        error = {
            'code': -32600,
            'message': "invalid form"
        }
    return result, error


#@login_required
def createFromForm(session, params):
    error = None
    result = None

    form_id = params['formId'] if 'formId' in params else 'SIIMForm'
    form_data = params['data'] if 'data' in params else {}
    if form_id == 'SIIMForm':
        form = SIIMModel.SIIMForm(**form_data)
        #: default responde is error
        try:
            form.save()
            result = {'uuid': form.uuid}
        except Exception:
            error = {
                'code': -32600,
                'message': "Unknown error : " + Exception.params()
            }
        finally:
            return result, error
    else:
        error = {
            'code': -32600,
            'message': 'Class ' + form_id + ' not found in Model'
        }
        return result, error

    #@login_required


def editFromForm(session, params):
    error = None
    result = None
    form_id = params['formId'] if 'formId' in params else 'SIIMForm'
    form_data = params['data'] if 'data' in params else {}
    if form_id == 'SIIMForm':
        form = SIIMModel.SIIMForm.index.get(uuid=form_data['uuid'])
        form.set_form_data(form_data)
        try:
            form.save()
            result = {'uuid': form.uuid}
        except Exception:
            error = {
                'code': -32600,
                'message': "Unknown error : " + Exception.params()
            }
        finally:
            return result, error
    else:
        error = {
            'code': -32600,
            'message': 'Class ' + form_id + ' not found in Model'
        }
        return result, error

    #@login_required


def deleteFromForm(session, params):
    error = None
    result = None
    form_id = params['formId'] if 'formId' in params else 'SIIMForm'
    form_data = params['data'] if 'data' in params else {}
    if form_id == 'SIIMForm':
        form = SIIMModel.SIIMForm.index.get(uuid=form_data['uuid'])
        #form.set_form_data(form_data)
        try:
            #form.save()
            result = {'uuid': form.uuid}
        except Exception:
            error = {
                'code': -32600,
                'message': "Unknown error : " + Exception.params()
            }
        finally:
            return result, error
    else:
        error = {
            'code': -32600,
            'message': 'Class ' + form_id + ' not found in Model'
        }
        return result, error


def getFormData(session, params):
    error = None
    result = None
    form_id = params['formId'] if 'formId' in params else 'SIIMForm'
    data_uuid = params['uuid'] if 'uuid' in params else ''
    if form_id == 'SIIMForm':
        try:
            form_node = SIIMModel.SIIMForm.index.get(uuid=data_uuid)
            result = {
                'data': form_node.get_form_data(),
                #: TODO: Create a helper private method to access forms
                'form': loadJSONFromFile(current_app.config["FORM_TEMPLATES"]
                                         + "/" + params["formId"] + ".json", current_app.root_path),
                'actions': ["create", "delete", "edit"]
            }

        except DoesNotExist:
            error = {
                'code': -32600,
                'message': 'Not found in db with uuid: ' + uuid
            }
        except Exception:
            error = {
                'code': -32600,
                'message': Exception.params()
            }

        finally:
            return result, error


def process_message(session, message):
    error = None
    rv = {}
    if 'jsonrpc' not in message:
        error = {
            'result': "Invalid Request",
            'code': -32600
        }
        rv['error'] = error
        current_app.logger.warn("Message did not contain a valid JSON RPC, messageJSON: " + str(message))
    elif 'method' not in message:
        error = {
            'result': "Method not found",
            'code': -32601
        }
        rv['error'] = error
        rv['id'] = None
        current_app.logger.warn("Message did not contain a valid Method, messageJSON: " + str(message))
    elif 'id' not in message:
        error = {
            'result': "Method did not contain a valid ID",
            'code': -32602
        }
        rv['error'] = error
        rv['id'] = None
        current_app.logger.warn("Message did not contain a valid ID, messageJSON: " + str(message))
    elif 'params' not in message:
        error = {
            'result': "Method did not contain params",
            'code': -32603
        }
        rv['error'] = error
    else:
        current_app.logger.debug('Command: ' + str(message))
        method = message['method']
        rv['id'] = message['id']
        if method == 'authentication':
            result, error = login_with_name(session, message['params'])
        elif method == 'authentication_with_uuid':
            result, error = login_with_uuid(session, message['params'])
        elif method == 'getFormTemplate':
            result, error = getFormTemplate(session, message['params'])
        elif method == 'create':
            result, error = createFromForm(session, message['params'])
        elif method == 'edit':
            result, error = editFromForm(session, message['params'])
        elif method == 'delete':
            result, error = deleteFromForm(session, message['params'])
        elif method == 'getFormData':
            result, error = getFormData(session, message['params'])
        else:
            error = {
                'result': "Method not found",
                'code': -32601
            }
            rv['error'] = error
            current_app.logger.warn("Message did not contain a valid Method, messageJSON: " + str(message))

    if error is not None:
        rv['error'] = error
    else:
        rv['result'] = result

    rv['jsonrpc'] = "2.0"
    current_app.logger.debug('Result: ' + str(rv))
    return rv
