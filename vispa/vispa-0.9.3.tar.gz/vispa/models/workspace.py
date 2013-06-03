# -*- coding: utf-8 -*-

# imports
from datetime import datetime
from sqlalchemy import Column, schema
from sqlalchemy.types import Unicode, Integer, DateTime, Boolean, Text
from vispa.models import Base
from vispa.helpers.db import insertion_safe
import json


class Workspace(Base):

    __tablename__   = 'workspace'
    id              = Column(Integer, nullable=False, primary_key=True)
    user_id         = Column(Integer, schema.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    name            = Column(Unicode(100), nullable=False)
    host            = Column(Unicode(100), nullable=True, default=None)
    login           = Column(Unicode(100), nullable=True, default=None)
    key             = Column(Text, nullable=True, default=None)
    password        = Column(Unicode(100), nullable=True, default=None)
    command         = Column(Text, nullable=True, default=None)
    basedir         = Column(Text, nullable=True, default=None)
    #locations       = Column(Unicode(100), nullable=False)# e.g. public/user/shared
    created         = Column(DateTime, nullable=True, default=datetime.now)
    __table_args__  = (schema.UniqueConstraint(host, login),)

    KEYS = ['id', 'user_id', 'name', 'host', 'login', 'key', 'password', 'command', 'basedir', 'created']

    def make_dict(self, keys=None):
        converters = {'id': int, 'user_id': int}
        if not keys:
            dict((key, value) for (key, value) in self.__dict__.items() if not key.startswith('_'))
            keys = Workspace.KEYS
        d = {}
        for key in keys:
            try:
                converter = str
                if key in converters.keys():
                    converter = converters[key]
                value = getattr(self, key)
                d[key] = '' if value is None else converter(value)
            except:
                pass
        return d

    @staticmethod
    def get_by_id(session, id):
        workspace = session.query(Workspace).filter_by(id=id).first()
        if isinstance(workspace, Workspace):
            return workspace
        return None

    @staticmethod
    def get_user_workspaces(session, user_id):
        user_workspaces = session.query(Workspace).filter_by(user_id=user_id)
        public_workspaces = session.query(Workspace).filter_by(user_id=None)
        return user_workspaces.union(public_workspaces).all()

    @staticmethod
    def get_user_workspace_count(session, user_id):
        user_workspaces = session.query(Workspace).filter_by(user_id=user_id)
        public_workspaces = session.query(Workspace).filter_by(user_id=None)
        return user_workspaces.union(public_workspaces).count()

    @staticmethod
    def add(session, user_id, name, host=None, login=None, key=None, password=None, command=None, basedir=None):
        # TODO: remove the arguments that represent columns with default values
        #       those entries have to be set via the update method (?)
        safe, key = insertion_safe(name, host, login, key, password, command, basedir)
        if not safe or not name:
            return False
        # TODO: check the connection
        entries = {'user_id' : user_id,
                   'name'    : name,
                   'host'    : host,
                   'login'   : login,
                   'key'     : key,
                   'password': password,
                   'command' : command,
                   'basedir' : basedir}
        workspace = Workspace(**entries)
        session.add(workspace)
        session.commit()
        return workspace

    @staticmethod
    def remove(session, id):
        workspace = Workspace.get_by_id(session, id)
        if not isinstance(workspace, Workspace):
            return False
        session.delete(workspace)
        session.commit()
        return True

    @staticmethod
    def update(session, id, **kwargs):
        workspace = Workspace.get_by_id(session, id)
        if not isinstance(workspace, Workspace):
            return False
        safe, key = insertion_safe(**kwargs)
        if not safe:
            return False
        # test loop
        forbidden_keys = ['id', 'user_id', 'created']
        for key, value in kwargs.items():
            if not hasattr(workspace, key):
                return False
        # real loop
        for key, value in kwargs.items():
            if str(key) in forbidden_keys:
                continue
            setattr(workspace, key, value)
        session.commit()
        return True


class WorkspaceState(Base):

    __tablename__   = 'workspace_state'
    workspace_id    = Column(Integer, schema.ForeignKey('workspace.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, primary_key=True)
    user_id         = Column(Integer, schema.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, primary_key=True)
    state           = Column(Text, nullable=True, default=u'{}')
    timestamp       = Column(DateTime, nullable=True, default=datetime.now)
    __table_args__  = (schema.PrimaryKeyConstraint(workspace_id, user_id),)

    @staticmethod
    def get_by_ids(session, workspace_id, user_id):
        workspace_state = session.query(WorkspaceState).filter_by(workspace_id=workspace_id, user_id=user_id).first()
        if not isinstance(workspace_state, WorkspaceState):
            # create an entry
            workspace_state = WorkspaceState(workspace_id=workspace_id, user_id=user_id)
            session.add(workspace_state)
            session.commit()
        return workspace_state

    @staticmethod
    def get_state(session, workspace_id, user_id, decode_json=False, workspace_state=None):
        workspace_state = workspace_state or WorkspaceState.get_by_ids(session, workspace_id, user_id)
        if not isinstance(workspace_state, WorkspaceState):
            return None
        state = workspace_state.state
        return state if not decode_json else json.loads(state)

    @staticmethod
    def update_state(session, workspace_id, user_id, state, workspace_state=None):
        workspace_state = workspace_state or WorkspaceState.get_by_ids(session, workspace_id, user_id)
        if not isinstance(workspace_state, WorkspaceState):
            return False
        if isinstance(state, dict):
            current_state = json.loads(workspace_state.state)
            for id, identifier in state.items():
                if identifier is None and id in current_state.keys():
                    del current_state[id]
                elif identifier:
                    current_state[id] = identifier
            workspace_state.state = json.dumps(current_state)
        else:
            workspace_state.state = unicode(state)
        workspace_state.timestamp = datetime.now()
        session.commit()
        return True
