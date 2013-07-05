import os
import ast
from collections import namedtuple


class Import(namedtuple('Import', ['module', 'name', 'alias', 'node'])):
    def is_submodule(self, parent):
        return self.module[0] == parent

    def code(self):
        if self.name:
            return 'from {} import {}'.format('.'.join(self.module), self.name)
        else:
            return 'import {}'.format('.'.join(self.module))

    def get_paths(self):
        """
        List of *possible* paths to which this import directive is referring
        to.
        """
        paths = []
        if self.name and self.name != '*':
            paths.append(os.path.join(*(self.module + [self.name + '.py'])))

        paths.append(os.path.join(*(self.module + ['__init__.py'])))
        paths.append(os.path.join(*(self.module[:-1] + [self.module[-1] + '.py'])))

        return paths


class Module(object):
    def __init__(self, path, base_path):
        self.base_path = base_path.rstrip('/')
        self.abspath = os.path.join(base_path, path)
        self.path = self.abspath[len(self.base_path) + 1:]

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, other):
        return isinstance(other, Module) and self.path == other.path

    def get_import_path(self):
        path, _ = os.path.splitext(self.path)
        path = path.split(os.sep)
        if path[-1] == '__init__':
            path.pop()
        path = '.'.join(path)
        return path

    def __repr__(self):
        return 'Module({!r})'.format(self.get_import_path())

    def get_imports(self):
        with open(self.abspath) as fh:
            root = ast.parse(fh.read(), self.path)

        for node in ast.iter_child_nodes(root):
            # TODO: This does not find imports nested in other directives
            # such as functions or try/excepts
            if isinstance(node, ast.Import):
                module = []
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split('.')
                else:
                    module = []
            else:
                continue

            for n in node.names:
                if not module:  # import
                    module = n.name.split('.')
                    name = None
                else:           # from ... import
                    name = n.name
                yield Import(module, name, n.asname, node)
