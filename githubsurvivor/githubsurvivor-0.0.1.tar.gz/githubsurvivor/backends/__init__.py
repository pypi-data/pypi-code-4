"""
This package contains backends for different issue tracking APIs.

Implementations provide a way to import users and issues into the local
database. The importer looks like this:

    class Importer:

        def import_users(self):
            # import all leaderboard users from repo

        def import_issues(self)
            # import all issues from repo
"""

from githubsurvivor import config

def configured_backend():
    "Import and return the configured backend."
    module_name = 'githubsurvivor.backends.%s' % config.BACKEND
    return __import__(module_name, fromlist=module_name)

def issue_importer():
    return configured_backend().issue_importer()

def web_theme():
    backend_name = config.BACKEND
    return {'html_classname': backend_name,
            'appname': '%s SURVIVOR' % backend_name.upper(),
            'logo_url': '/img/%s/logo.png' % backend_name}
