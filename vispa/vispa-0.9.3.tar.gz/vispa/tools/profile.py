# -*- coding: utf-8 -*-

# imports
import cherrypy
import vispa
import os
import json
from vispa.helpers import browser
from vispa.models.profile import Profile


class ProfileTool(cherrypy.Tool):

    def __init__(self):
        cherrypy.Tool.__init__(self, 'before_handler', self._fetch, priority=75)

    def _setup(self):
        cherrypy.Tool._setup(self)
        cherrypy.request.hooks.attach('before_finalize', self._cleanup, priority=25)

    def _fetch(self):
        db = cherrypy.request.db
        """ If there's no profile_id stored in the session,
            there are multiple methods to (auto-)select a profile.
                1. select the most recent used profile that used
                   the same user agent
                2. select the most recent used profile
                3. create a new profile based on a 'best-guess'
                   of the user agent
        """
        key = "profile_id"
        if key in cherrypy.session.keys():
            profile = Profile.get_by_id(db, cherrypy.session[key])
            if isinstance(profile, Profile):
                cherrypy.request.profile = profile
                Profile.use(db, profile.id, profile=profile, agent=browser.client_agent())
                return True

        user_id = cherrypy.request.user.id
        profile = None
        # case 1
        # select the last used profile with the same agent as the current one
        profile = Profile.get_user_profiles_by_agent(db, user_id, browser.client_agent(), last=True)

        # case 2
        # select the most rectent used profile
        if not isinstance(profile, Profile):
            profile = Profile.get_user_profiles(db, user_id, last=True)

        # case 3
        # create a new profile, best-guess is ToDo
        if not isinstance(profile, Profile):
            profile = Profile.add(db, user_id, "Default", agent=browser.client_agent())

        if isinstance(profile, Profile):
            cherrypy.request.profile = profile
            cherrypy.session[key] = profile.id
            Profile.use(db, profile.id, profile=profile, agent=browser.client_agent())
            return True

        # this case should never occur
        raise Exception("No Profile found")

    def _cleanup(self):
        cherrypy.request.profile = None
