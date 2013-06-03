# -*- coding: utf-8 -*-

# imports
from datetime import datetime
import json as JSON
from sqlalchemy import Column, schema
from sqlalchemy.types import Unicode, Integer, DateTime, Boolean, Text
from vispa.models import Base
from vispa.helpers.db import insertion_safe
from vispa.models.preference import VispaPreference, ExtensionPreference


class Profile(Base):

    __tablename__  = 'profile'
    id             = Column(Integer, nullable=False, primary_key=True)
    user_id        = Column(Integer, schema.ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    name           = Column(Unicode(64), nullable=False)
    last_used      = Column(DateTime, nullable=False, default=datetime.now)
    last_agent     = Column(Text, nullable=True)
    created        = Column(DateTime, nullable=False, default=datetime.now)
    __table_args__ = (schema.UniqueConstraint(user_id, name),)

    @staticmethod
    def get_by_id(session, id):
        return session.query(Profile).filter_by(id=id).first()

    @staticmethod
    def get_user_profiles(session, user_id, last=False):
        profiles = session.query(Profile).filter_by(user_id=user_id).all()
        if not len(profiles):
            return False
        if not last:
            return profiles
        last_profile = None
        for profile in profiles:
            if not last_profile:
                last_profile = profile
                continue
            if profile.last_used > last_profile.last_used:
                last_profile = profile
        return last_profile

    @staticmethod
    def get_user_profiles_by_agent(session, user_id, agent, last=False):
        profiles = session.query(Profile).filter_by(user_id=user_id, last_agent=agent).all()
        if not len(profiles):
            return False
        if not last:
            return profiles
        last_profile = None
        for profile in profiles:
            if not last_profile:
                last_profile = profile
                continue
            if profile.last_used > last_profile.last_used:
                last_profile = profile
        return last_profile

    @staticmethod
    def add(session, user_id, name, agent=None):
        name = unicode(name)
        # name already set for this user?
        profiles = Profile.get_user_profiles(session, user_id)
        if profiles:
            for profile in profiles:
                if profile.name == name:
                    return False
        profile = Profile(user_id=user_id, name=name, last_agent=agent)
        session.add(profile)
        session.commit()
        return profile

    @staticmethod
    def update(session, id, profile=None, **kwargs):
        profile = profile or Profile.get_by_id(session, id)
        if not isinstance(profile, Profile):
            return False
        safe, key = insertion_safe(**kwargs)
        if not safe:
            return False
        # test loop
        forbidden_keys = ['id', 'user_id']
        for key, value in kwargs.items():
            if str(key) in forbidden_keys or not hasattr(profile, key):
                return False
        # real loop
        for key, value in kwargs.items():
            setattr(profile, key, value)
        session.commit()
        return True

    @staticmethod
    def remove(session, id, profile=None):
        profile = profile or Profile.get_by_id(session, id)
        if isinstance(profile, Profile):
            session.delete(profile)
            session.commit()
            return True
        return False

    @staticmethod
    def use(session, id, profile=None, agent=None):
        data = {'last_used': datetime.now()}
        if agent:
            data['last_agent'] = agent
        Profile.update(session, id, profile=profile, **data)
        return True

    @staticmethod
    def get_preferences(session, id, profile=None, parse_json=False):
        preferences = {}
        profile = profile or Profile.get_by_id(session, id)
        if isinstance(profile, Profile):
            # vispa_preference
            preferences['vispa_preference'] = VispaPreference.get_data_by_profile_id(session, profile.id)
            # extension_preference
            preferences['extension_preference'] = ExtensionPreference.get_data_by_profile_id(session, profile.id)
            # parse?
            if parse_json:
                parsed_preferences = {}
                for key, value in preferences.items():
                    parsed_preference = {}
                    for key2, value2 in value.items():
                        parsed_preference[key2] = JSON.loads(value2)
                    parsed_preferences[key] = JSON.dumps(parsed_preference)
                preferences = parsed_preferences
        return preferences
