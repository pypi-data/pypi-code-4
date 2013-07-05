from github import Github
import hashlib

from csat.graphml.builder import GraphMLDocument, Attribute



class IssuesGraph(object):

    def __init__(self):
        self.document = GraphMLDocument()

        self.document.attr(Attribute.GRAPH, 'merge_key')
        self.document.attr(Attribute.NODE, 'domain')

        self.document.attr(Attribute.EDGE, 'type')
        self.document.attr(Attribute.EDGE, 'timestamp')

        self.document.attr(Attribute.NODE, 'id', 'int')
        self.document.attr(Attribute.NODE, 'title')
        self.document.attr(Attribute.NODE, 'state')
        self.document.attr(Attribute.ALL, 'url')

        self.document.attr(Attribute.ALL, 'comments', 'int')

        self.document.attr(Attribute.NODE, 'email')
        self.document.attr(Attribute.NODE, 'login')
        self.document.attr(Attribute.NODE, 'name')


        self.domains = self.document.digraph(None, {'merge_key': 'domain'})

        self.users = self.domains.node(None, {
            'domain': 'people'
        }).subgraph(None, {
            'merge_key': 'email'
        })

        self._init_issues()

        self.edge_domain = self.domains

        self.issue_map = {}
        self.user_map = {}
        self.comment_map = {}

    def _init_issues(self):
        self.issues = self.domains.node(None, {
            'domain': 'change_requests'
        }).subgraph(None, {
            'merge_key': 'id'
        })

    def add_issue(self, issue):
        if issue.number not in self.issue_map:
            node = self.issues.node(None, {
                'id': issue.number,
                'title': issue.title,
                'url': issue.html_url,
                'state': issue.state
            })

            self.domains.edge(self.add_user(issue.user), node, {
                'type': 'created',
                'timestamp': issue.created_at
            })

            if issue.assignee:
                self.domains.edge(node, self.add_user(issue.assignee), {
                    'type': 'assignee',
                })

            if issue.closed_by:
                self.domains.edge(self.add_user(issue.closed_by), node, {
                    'type': 'closed',
                    'timestamp': issue.closed_at,
                })

            self.issue_map[issue.number] = node

        return self.issue_map[issue.number]

    def add_user(self, user):
        if user.id not in self.user_map:
            email = user.email
            if not email:
                email = '{}@{}'.format(user.login, self.repo_hash)
            node = self.users.node(None, {
                'email': email,
                'url': user.html_url,
                'name': user.name,
                'login': user.login,
                'comments': 0,
            })
            self.user_map[user.id] = node
        return self.user_map[user.id]

    def add_comment(self, comment):
        _, issue = comment._rawData['issue_url'].rsplit('/', 1)
        try:
            issue = self.issue_map[int(issue)]
        except KeyError:
            return
        user = self.add_user(comment.user)
        user['comments'] += 1

        key = (issue, user)

        if key not in self.comment_map:
            self.comment_map[key] = self.edge_domain.edge(user, issue, {
                'type': 'commented',
                'timestamp': comment.created_at,
                'url': comment.html_url,
                'comments': 0,
            })
        self.comment_map[key]['comments'] += 1

    def write_graphml(self, stream):
        self.document.to_file(stream)


class CommunicationGraph(IssuesGraph):

    def __init__(self, *args, **kwargs):
        super(CommunicationGraph, self).__init__(*args, **kwargs)
        self.edge_domain = self.users

    def _init_issues(self):
        pass

    def add_issue(self, issue):
        user = self.issue_map[issue.number] = self.add_user(issue.user)
        return user


class GithubCommentsCollector(object):

    def __init__(self, task_manager, logger, repo_name, issue_nodes,
                 issues_state, auth):
        self.tasks = task_manager
        self.log = logger
        self.repo_user, self.repo_name = repo_name.split('/')
        self.issue_state = issues_state
        self.auth = auth

        if issue_nodes:
            self.graph = IssuesGraph()
        else:
            self.graph = CommunicationGraph()

        self.graph.repo_hash = hashlib.sha1(repo_name).hexdigest()

    def fetch_issues(self, repo, state):
        for issue in repo.get_issues(state=state):
            self.fetch_issue_task.statusText = (
                'Fetching and parsing data for issue #{}...'.format(
                    issue.number)
            )
            self.graph.add_issue(issue)

    def fetch_comments(self, repo):
        for comment in repo.get_issues_comments():
            self.fetch_comment_task.statusText = (
                'Fetching and parsing data for comment #{}...'.format(
                    comment.id)
            )
            self.graph.add_comment(comment)

    def fetch_repo(self, gh):
        return gh.get_user(self.repo_user).get_repo(self.repo_name)

    def run(self):
        self.fetch_issue_task = self.tasks.new('Fetching issues')
        self.fetch_comment_task = self.tasks.new('Fetching comments')

        if not self.auth:
            self.log.warning('Accessing the Github API in unauthenticated '
                             'mode, rate limit ahead.')

        if len(self.auth) == 2:
            kwargs = {
                'client_id': self.auth[0],
                'client_secret': self.auth[1],
            }
        elif len(self.auth) == 1:
            kwargs = {
                'login_or_token': self.auth[0]
            }
        else:
            kwargs = {}

        gh = Github(**kwargs)
        repo = self.fetch_repo(gh)

        self.log.info('GitHub API rate limit is: {}'.format(gh.rate_limiting))

        self.fetch_issue_task.status = self.fetch_issue_task.RUNNING
        if self.issue_state in ('all', 'open'):
            self.fetch_issues(repo, 'open')

        if self.issue_state in ('all', 'closed'):
            self.fetch_issues(repo, 'closed')
        self.fetch_issue_task.setCompleted()

        self.fetch_comment_task.status = self.fetch_comment_task.RUNNING
        self.fetch_comments(repo)
        self.fetch_comment_task.setCompleted()

        self.log.info('GitHub API rate limit is: {}'.format(gh.rate_limiting))

        return self.graph
