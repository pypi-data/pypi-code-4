import os
import datetime
import git
import tempfile
import shutil
import re

from csat.paths import PathWalker
from csat.graphml.builder import GraphMLDocument, Attribute
from . import parser


class ModuleNotFound(KeyError):
    pass


class ModuleAlreadyTracked(KeyError):
    pass


def timestamp_to_iso(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).isoformat()


class DependencyGraph(object):
    def __init__(self, keep_history):
        self.modules = {}
        self.authors = {}
        self.modifications = {}
        self._nextid = 0
        self._nextauthorid = 0
        self._init_graph()
        self.keep_history = False

    def _init_graph(self):
        self.graph = GraphMLDocument()

        self.graph.attr(Attribute.GRAPH, 'merge_key')

        self.graph.attr(Attribute.NODE, 'domain')
        self.graph.attr(Attribute.NODE, 'commits', 'int')
        self.graph.attr(Attribute.NODE, 'package')
        self.graph.attr(Attribute.ALL, 'type')
        self.graph.attr(Attribute.ALL, 'date_added')
        self.graph.attr(Attribute.ALL, 'commit_added')
        self.graph.attr(Attribute.ALL, 'author_added')
        self.graph.attr(Attribute.ALL, 'date_removed')
        self.graph.attr(Attribute.ALL, 'commit_removed')
        self.graph.attr(Attribute.ALL, 'author_removed')
        self.graph.attr(Attribute.ALL, 'email')
        self.graph.attr(Attribute.ALL, 'count', 'int')

        self.domains = self.graph.digraph(None, {
            'merge_key': 'domain'
        })

        self.components = self.domains.node(None, {
            'domain': 'components'
        }).subgraph(None, {
            'merge_key': 'package'
        })

        self.developers = self.domains.node(None, {
            'domain': 'people'
        }).subgraph(None, {
            'merge_key': 'email'
        })

    def email_from_commit(self, commit):
        email = commit.author.email
        # TODO: hardcoded is BAAAD!
        return re.sub(r'[0-9a-f-]{36}$', 'twistedmatrix.com', email)

    def add_modification(self, commit, module):
        email = self.email_from_commit(commit)
        try:
            authorid, authornode = self.authors[email]
            authornode['commits'] += 1
        except KeyError:
            authorid = self._nextauthorid
            authornode = self.developers.node(authorid, {
                'email': email,
                'commits': 1,
            })
            self.authors[email] = [authorid, authornode]
            self._nextauthorid += 1

        modulenode = self.module(module)

        try:
            edge = self.modifications[authornode, modulenode]
            edge['commits'] += 1
        except KeyError:
            edge = self.domains.edge(authornode, modulenode, {
                'type': 'modification',
                'count': 1,
            })
            self.modifications[authornode, modulenode] = edge

    def add_module(self, commit, module):
        email = self.email_from_commit(commit)
        try:
            if not self.modules[module][2] and not self.keep_history:
                raise KeyError
            else:
                self.modules[module][2] = True
        except KeyError:
            self.modules[module] = [self._nextid, set(), True]
            self.components.node(self._nextid, {
                'package': module.get_import_path(),
                'type': 'package',
                # TODO: Nor really true
                'date_added': timestamp_to_iso(commit.committed_date),
                'commit_added': commit.hexsha,
                'author_added': email,
            })
            self._nextid += 1
        else:
            # TODO: Update commit metadata
            pass

    def id(self, module):
        return self.modules[module][0]

    def module(self, module):
        return self.components.nodes[self.modules[module][0]]

    def dependency(self, source, target):
        try:
            key = self.module(source), self.module(target)
            return self.components.edges[key]
        except KeyError:
            return set()

    def remove_module(self, commit, module):
        spec = self.modules[module]
        assert not spec[1]
        spec[2] = False
        node = self.module(module)
        if self.keep_history:
            node['date_removed'] = timestamp_to_iso(commit.committed_date)
            node['commit_removed'] = commit.hexsha
            node['author_removed'] = self.email_from_commit(commit)
        else:
            self.components.remove_node(node)

    def get_dependencies(self, module):
        try:
            _, deps, active = self.modules[module]
            if not active:
                raise ModuleNotFound(module)
        except KeyError:
            raise ModuleNotFound(module)
        return deps

    def add_dependency(self, commit, source, target):
        self.add_module(commit, target)

        self.get_dependencies(source).add(target)
        self.components.edge(self.module(source), self.module(target), {
            'type': 'dependency',
            'date_added': timestamp_to_iso(commit.committed_date),
            'commit_added': commit.hexsha,
            'author_added': self.email_from_commit(commit),
        })

    def add_dependencies(self, commit, source, targets):
        for target in targets:
            self.add_dependency(commit, source, target)

    def remove_dependency(self, commit, source, target):
        self.get_dependencies(source).remove(target)
        if self.keep_history:
            for edge in self.dependency(source, target):
                edge['date_removed'] = timestamp_to_iso(commit.committed_date)
                edge['commit_removed'] = commit.hexsha
                edge['author_removed'] = self.email_from_commit(commit)
        else:
            self.dependency(source, target).clear()

    def remove_dependencies(self, commit, source, targets):
        for target in targets:
            self.remove_dependency(commit, source, target)

    def write_graphml(self, stream):
        return self.graph.normalized().to_file(stream)


class GitPythonCollector(object):

    def __init__(self, task_manager, logger, repo_url, rev, package,
                 keep_history):
        self.tasks = task_manager
        self.log = logger
        self.repo_url = repo_url
        self.clone_path = None
        self.git = None
        self.rev = rev
        self.package_path = package.strip('/')
        try:
            self.base_path, self.package_name = self.package_path.rsplit('/',
                                                                         1)
        except ValueError:
            self.base_path, self.package_name = '', self.package_path
        self.graph = DependencyGraph(keep_history=keep_history)

    def init_repo(self):
        self.checkout_task.statusText = ('Cloning repository to temporary '
                                         'location...')
        self.checkout_task.status = self.checkout_task.RUNNING
        self.clone_path = tempfile.mkdtemp(prefix='csat-pygit-')
        self.log.info('Cloning to temporary directory at {!r}'.format(
            self.clone_path))
        self.repo = git.Repo.clone_from(self.repo_url, self.clone_path)
        self.checkout_task.setCompleted()
        self.git = self.repo.git

    def run(self):
        # Init tasks
        self.checkout_task = self.tasks.new('Source checkout')
        self.commit_task = self.tasks.new('Parsing commits')

        try:
            self.init_repo()
            commits = self.bootstrap()
            self.analyze(commits)
        finally:
            # Cleanup
            self.log.info('Removing temporary repository at {}'.format(
                self.clone_path))
            shutil.rmtree(self.clone_path)

        return self.graph

    def bootstrap(self):
        self.commit_task.statusText = 'Getting commit summary...'

        self.count = 0
        for commit in self.repo.iter_commits(self.rev):
            self.count += 1

        if not self.count:
            raise ValueError('The provided revision specifier does not '
                             'contain any commits.')

        self.commit_task.steps = self.count + 1

        commits = self.repo.iter_commits(self.rev, max_count=self.count,
                                         reverse=True)
        commits = enumerate(commits)
        skip = False

        for i, commit in commits:
            self.git.checkout(commit.hexsha, force=True)
            package_dir = os.path.join(self.repo.working_dir, self.base_path)
            if os.path.exists(package_dir):
                self.log.info('First commit set to [{}]: {}'.format(
                    commit.hexsha[:6], commit.summary.encode('utf-8')))
                self.handle_initial_commit(commit)
                break
            elif not skip:
                skip = True
                self.log.warning('Package directory not found at initial '
                                 'commit [{}], fast forwarding...'
                                 .format(commit.hexsha[:6]))
            self.commit_task.statusText = (
                'Finding initial commit (skipping {}/{})...'.format(
                    i + 1, self.count))
            self.commit_task.makeStep()
        else:
            self.log.critical('Package directory not found in any commit in '
                              'the given revspec.')
            raise RuntimeError('Package not found')
        self.commit_task.makeStep()
        return commits

    def analyze(self, commits):
        for i, commit in commits:
            try:
                summary = commit.summary.encode('utf-8')
            except LookupError:
                # Sometimes our git library does not want to play along
                summary = ''

            self.log.debug('Analyzing commit [{}]: {}'.format(
                commit.hexsha[:6], summary))
            self.commit_task.statusText = 'Analyzing commit {}/{}...'.format(
                i + 1, self.count)
            self.git.checkout(commit.hexsha, force=True)
            paths = self.get_modified_paths(commit.parents[0])
            self.handle_commit(commit, paths)
            self.commit_task.makeStep()

        self.log.info('Last commit is [{}]: {}'.format(
            commit.hexsha[:6], commit.summary.encode('utf-8')))
        self.commit_task.setCompleted()

    def get_modified_paths(self, commit):
        for diff in commit.diff():
            if diff.renamed:
                self.log.error('RENAMED {}'.format(diff.path))

            #if diff.a_blob is None:
            #    # File was created
            #    self.log.error('CREATED {}'.format(diff.b_blob.path))

            if diff.b_blob is None:
                # File was deleted
                deleted = True
                path = diff.a_blob.path
            else:
                deleted = False
                path = diff.b_blob.path

            path = path[len(self.base_path) + 1:] if self.base_path else path

            if self.filter_path(path):
                yield path, deleted

    def filter_path(self, path):
        # Keep only python files
        if not path.endswith('.py'):
            return False

        # Keep only files in the package
        if not path.startswith('{}/'.format(self.package_name)):
            return False

        # Exclude test files
        if '/test/' in path or path.endswith('test.py'):
            return False

        return True

    def get_dependent_modules(self, commit, module):
        imports = module.get_imports()
        imports = (imp for imp in imports if imp.is_submodule(
            self.package_name))
        depends_on = set()
        package_dir = os.path.join(self.repo.working_dir, self.base_path)

        try:
            for imp in imports:
                paths = imp.get_paths()
                for p in paths:
                    if os.path.exists(os.path.join(package_dir, p)):
                        depends_on.add(parser.Module(p, package_dir))
                        break
                else:
                    location = '{}:{}:{} @ {}'.format(
                        module.path, imp.node.lineno, imp.node.col_offset,
                        commit.hexsha[:6])

                    path_list = '\n'.join(' * {}'.format(p) for p in paths)
                    msg = (
                        'Could not find target for \'{}\' in {}, tried:\n{}'
                        .format(imp.code(), location, path_list)
                    )
                    self.log.warn(msg)
        except SyntaxError as e:
            location = '{}:{}:{}'.format(e.filename, e.lineno, e.offset)
            code = '>>> ' + e.text + ' ' * (e.offset + 3) + '^'
            error = '{}\n{}'.format(location, code)
            self.log.error('Could not parse module {!r} in commit {} ({})\n{}'
                           .format(module.get_import_path(), commit.hexsha[:6],
                                   e.msg, error))
        except ValueError as e:
            self.log.error('Could not parse module {!r} in commit {} ({})'
                           .format(module.get_import_path(), commit.hexsha[:6],
                                   e))

        return depends_on

    def handle_initial_commit(self, commit):
        package_dir = os.path.join(self.repo.working_dir, self.base_path)
        walker = PathWalker(package_dir, fullpath=False)
        walker.filter(filename=r'.*\.py')
        walker.exclude(directory=r'\.git')
        walker.exclude(directory=r'test')
        walker.exclude(directory=r'doc')

        def create_iter(paths):
            for p in paths:
                if self.filter_path(p):
                    yield p, False

        self.handle_commit(commit, create_iter(walker.walk()))

    def handle_commit(self, commit, paths):
        package_dir = os.path.join(self.repo.working_dir, self.base_path)

        for path, deleted in paths:
            module = parser.Module(path, package_dir)

            if deleted:
                dependencies = set()
            else:
                dependencies = self.get_dependent_modules(commit, module)

            try:
                old_dependencies = self.graph.get_dependencies(module)
                removed = old_dependencies - dependencies
                added = dependencies - old_dependencies
            except ModuleNotFound:
                #assert not deleted
                self.log.debug('Created {!r}'.format(module))
                self.graph.add_module(commit, module)
                added = dependencies
                removed = set()

            self.graph.add_modification(commit, module)

            if deleted:
                self.log.debug('Deleted {!r}'.format(module))

            self.graph.remove_dependencies(commit, module, removed)
            self.graph.add_dependencies(commit, module, added)

            if deleted:
                self.graph.remove_module(commit, module)

        if not paths:
            self.log.debug('No source files modified, skipping commit {}'
                           .format(commit.hexsha[:6]))
