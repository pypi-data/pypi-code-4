import os
from pyprotobuf.parser import ProtoParser, ParseError
from pyprotobuf.codegenerator import Frame
from pyprotobuf.nameresolver import NameResolver
from pyprotobuf.commentresolver import CommentResolver
from pyprotobuf.namecollector import NameCollector
from pyprotobuf.dependencysorter import DependencySorter
import pyprotobuf.nodes as nodes
import logging
import copy


logger = logging.getLogger('pyprotobuf.Compiler')


class Compiler(object):
    def __init__(self, generator_class):
        self.parser = ProtoParser()
        self.generator_class = generator_class
        self.import_paths = [os.getcwd()]

    def set_import_paths(self, paths):
        self.import_paths = paths

    def compile(self, filename):
        with open(filename, 'r') as f:
            return self.compile_string(filename, f.read())

    def compile_string(self, filename, string):
        try:
            rootnode = self.precompile_string(filename, string)
        except ParseError as e:
            print str(e)
            raise

        generator = self.generator_class()
        # only compile the last package for now
        return generator.generate_file(rootnode.children[-1].children[0])

    def precompile_string(self, filename, string):
        self.packages = nodes.RootNode()
        self.traversal_path = []

        package = self.parser.parse_string(string)
        # so the generators know the path 
        package.children[0].filename = filename


        # resolve an add other packages before adding ours
        self.resolve_imports(package.children[0])

        self.packages.add_child(package)

        frame = Frame()




        name_collector = NameCollector(frame)
        name_collector.visit(self.packages, )

        logger.debug('Resolving names')
        # resolve name references between messages/etc
        name_resolver = NameResolver(frame)
        name_resolver.visit(self.packages)

        logger.debug('Resolved names')


        dependency_sorter = DependencySorter(frame)
        dependency_sorter.visit(self.packages)

        logger.debug('FINISHED DEP SORT %r', self.packages)

        # associate comments with suceeding nodes
        comment_resolver = CommentResolver(frame)
        comment_resolver.visit(self.packages)






        return self.packages


    def resolve_import_path(self, path, file_node=None):
        if path.startswith('/'):
            return path

        # search through each of the paths
        # if specified, starting relative to the directory of the package
        import_paths = copy.copy(self.import_paths)
        if file_node is not None:
            assert isinstance(file_node, nodes.FileNode)
            import_paths.insert(0, os.path.dirname(file_node.filename))

        split_path = path.split(os.pathsep)
        for import_path in import_paths:
            test_path = os.path.join(import_path, *split_path)
            if os.path.exists(test_path):
                return test_path

        raise Exception("Could not find import %s in paths %s" % (path, import_paths))


    def resolve_imports(self, file_node):
        assert isinstance(file_node, nodes.FileNode)
        # find any import nodes
        for child in file_node.get_imports():
            path = self.resolve_import_path(child.value, file_node)

            importnode = self.import_package(path)

            if importnode.name in self.traversal_path:
                self.traversal_path.append(importnode.name)
                raise Exception("Circular import %s" % self.traversal_path)

            # visit other imports before we add ours
            self.traversal_path.append(importnode.name)
            self.resolve_imports(importnode.children[0])
            self.traversal_path.pop()
            self.packages.add_child(importnode)

    def import_package(self, filename):
        """ Return the package node at path. 
        """
        if filename in self.traversal_path:
            raise Exception("Circular import %s from %s" % (filename, self.traversal_path))

        self.traversal_path.append(filename)

        with open(filename, 'r') as f:
            string = f.read()

        package = self.parser.parse_string(string)
        package.children[0].filename = filename

        self.resolve_imports(package.children[0])

        self.traversal_path.pop()

        return package
            
            