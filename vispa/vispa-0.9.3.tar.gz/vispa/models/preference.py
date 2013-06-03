# -*- coding: utf-8 -*-

# imports
from sqlalchemy import Column, schema
from sqlalchemy.types import Integer, Unicode, DateTime
from datetime import datetime
from vispa.models import Base
from vispa.helpers.db import insertion_safe
import json as JSON

class VispaPreference(Base):

    __tablename__  = 'vispa_preference'
    profile_id     = Column(Integer, schema.ForeignKey('profile.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, primary_key=True)
    section        = Column(Unicode(64), nullable=False, primary_key=True)
    value          = Column(Unicode(300), nullable=False, default=u'{}')
    timestamp      = Column(DateTime, nullable=False, default=datetime.now)
    created        = Column(DateTime, nullable=False, default=datetime.now)
    __table_args__ = (schema.PrimaryKeyConstraint(profile_id, section),)

    @staticmethod
    def get_by_profile_id(session, profile_id, section=None):
        preferences = session.query(VispaPreference).filter_by(profile_id=profile_id).all()
        if not section:
            return preferences
        for preference in preferences:
            if isinstance(preference, VispaPreference):
                if preference.section == section:
                    return preference
        return None

    @staticmethod
    def get_data_by_profile_id(session, profile_id, section=None, parse_json=False):
        data = {}
        preferences = VispaPreference.get_by_profile_id(session, profile_id, section=section)
        if isinstance(preferences, list):
            for preference in preferences:
                if parse_json:
                    data[preference.section] = JSON.loads(preference.value)
                else:
                    data[preference.section] = preference.value
            return data
        elif isinstance(preferences, VispaPreference):
            if parse_json:
                return JSON.loads(preferences.value)
            else:
                return preferences.value
        return None

    @staticmethod
    def set_value(session, profile_id, section, value, update=True):
        safe, key = insertion_safe(section, value)
        if not safe:
            return False
        # entry already exists?
        preference = VispaPreference.get_by_profile_id(session, profile_id, section=section)
        if isinstance(preference, VispaPreference):
            preference.value = value
            if update:
                preference.timestmap = datetime.now()
        else:
            preference = VispaPreference(profile_id=profile_id, section=section, value=value)
            session.add(preference)
        session.commit()
        return preference


class ExtensionPreference(Base):

    __tablename__  = 'extension_preference'
    profile_id     = Column(Integer, schema.ForeignKey('profile.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, primary_key=True)
    key            = Column(Unicode(64), nullable=False, primary_key=True)
    value          = Column(Unicode(300), nullable=False, default=u'{}')
    timestamp      = Column(DateTime, nullable=False, default=datetime.now)
    created        = Column(DateTime, nullable=False, default=datetime.now)
    __table_args__ = (schema.PrimaryKeyConstraint(profile_id, key),)

    @staticmethod
    def get_by_profile_id(session, profile_id, key=None):
        preferences = session.query(ExtensionPreference).filter_by(profile_id=profile_id).all()
        if not key:
            return preferences
        for preference in preferences:
            if isinstance(preference, ExtensionPreference):
                if preference.key == key:
                    return preference
        return None

    @staticmethod
    def get_data_by_profile_id(session, profile_id, key=None, parse_json=False):
        data = {}
        preferences = ExtensionPreference.get_by_profile_id(session, profile_id, key=key)
        if isinstance(preferences, list):
            for preference in preferences:
                if parse_json:
                    data[preference.key] = JSON.loads(preference.value)
                else:
                    data[preference.key] = preference.value
            return data
        elif isinstance(preferences, ExtensionPreference):
            if parse_json:
                return JSON.loads(preferences.value)
            else:
                return preferences.value
        return None

    @staticmethod
    def set_value(session, profile_id, key, value, update=True):
        safe, _key = insertion_safe(key, value)
        if not safe:
            return False
        # entry already exists?
        preference = ExtensionPreference.get_by_profile_id(session, profile_id, key=key)
        if isinstance(preference, ExtensionPreference):
            preference.value = value
            if update:
                preference.timestmap = datetime.now()
        else:
            preference = ExtensionPreference(profile_id=profile_id, key=key, value=value)
            session.add(preference)
        session.commit()
        return preference
