from .endpoint import EndpointMixin, maybe_quote
from .gerrit_entity import GerritEntity, Self

from .accounts import Account

# gerrit-documentation.googlecode.com/svn/Documentation/2.7/rest-api-groups.html

class Group(GerritEntity, EndpointMixin):
    id = str
    name = unicode
    url = str
    options = dict
    description = unicode
    group_id = int
    owner = unicode
    owner_id = str
    members = [Account]
    includes = [Self]

    def endpoint_id(self):
        return self.id or self.group_id or maybe_quote(self.name)
