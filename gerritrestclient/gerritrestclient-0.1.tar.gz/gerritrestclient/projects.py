from .endpoint import EndpointMixin, endpoint_setup
from .gerrit_entity import GerritEntity

from .accounts import Account

# gerrit-documentation.googlecode.com/svn/Documentation/2.7/rest-api-projects.html

class Project(GerritEntity, EndpointMixin):
    id = str
    name = unicode
    parent = unicode
    description = unicode
    branches = {unicode: str}


class DashboardSection(GerritEntity):
    name = unicode
    query = unicode

@endpoint_setup(parent='Group')
class Dashboard(GerritEntity, EndpointMixin):
    id = str
    project = unicode
    defining_project = unicode
    ref = unicode
    path = unicode
    description = unicode
    foreach = unicode
    url = unicode
    default = bool
    title = unicode
    sections = [DashboardSection]

