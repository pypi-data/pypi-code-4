from .endpoint import EndpointMixin, endpoint_setup
from .gerrit_entity import GerritEntity, Timestamp, Self

from .accounts import Account

# gerrit-documentation.googlecode.com/svn/Documentation/2.7/rest-api-changes.html

class Approval(Account):
    value = int


class GitPerson(GerritEntity):
    name = unicode
    email = unicode
    date = Timestamp
    tz = int
    
    
@endpoint_setup(parent='Revision')
class Comment(GerritEntity, EndpointMixin):
    id = str
    path = str
    side = str
    line = int
    in_reply_to = str
    message = unicode
    updated = Timestamp
    author = Account

class Draft(Comment): pass # Endpoint alias


class Commit(GerritEntity):
    parent = [Self]
    author = GitPerson
    committer = GitPerson
    subject = unicode
    message = unicode
    

class FetchInfo(GerritEntity):
    url = unicode
    ref = unicode
        
    
class FileInfo(GerritEntity):
    status = str
    binary = bool
    old_path = unicode
    lines_inserted = int
    lines_deleted = int
    

class Label(GerritEntity):
    approved = Account
    rejected = Account
    recommended = Account
    disliked = Account
    value = int
    optional = bool
    all = [Approval]
    values = {str: unicode}
    
    
class ChangeMessage(GerritEntity):
    id = str
    author = Account
    date = Timestamp
    message = unicode
    _revision_number = int
        
    
@endpoint_setup(parent='Change')
class Reviewer(Account, EndpointMixin):
    approvals = {unicode: str}

    
class AddReviewerResult(GerritEntity):
    reviewers = [Reviewer]
    error = unicode
    confirm = bool
    

@endpoint_setup(parent='Change')
class Revision(GerritEntity, EndpointMixin):
    draft = bool
    _number = int
    fetch = {str: FetchInfo}
    commit = Commit
    files = {unicode: FileInfo}

    def endpoint_id(self):
        return self._number
        
    
class Change(GerritEntity, EndpointMixin):
    id = str
    project = unicode
    branch = unicode
    topic = unicode
    change_id = str
    subject = unicode
    status = str
    created = Timestamp
    updated = Timestamp
    starred = bool
    reviewed = bool
    mergeable = bool
    _sortkey = str
    _number = int
    owner = Account
    labels = {unicode: Label}
    permitted_labels = {unicode: list}
    removable_reviewers = [Account]
    messages = [ChangeMessage]
    current_revision = str
    revisions = {str: Revision}
    _more_changes = bool

    def endpoint_id(self):
        return self.id or self.change_id or self._number


# Inputs

class ReviewInput(GerritEntity):
    message = unicode
    labels = {unicode: int}
    comments = {unicode: [Comment]}
    strict_labels = bool
    drafts = str
    notify = str
