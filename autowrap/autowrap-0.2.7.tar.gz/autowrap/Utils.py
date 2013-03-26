template = """

from distutils.core import setup, Extension

import sys
import pprint

from Cython.Distutils import build_ext

ext = Extension("%(name)s", sources = %(source_files)s, language="c++",
        include_dirs = %(include_dirs)r,
        extra_compile_args = [],
        extra_link_args = [],
        )

setup(cmdclass = {'build_ext' : build_ext},
      name="%(name)s",
      version="0.0.1",
      ext_modules = [ext]
     )

"""

def compile_and_import(name, source_files, include_dirs=None, **kws):

    if include_dirs is None:
        include_dirs = []

    debug = kws.get("debug")
    import os.path
    import shutil
    import tempfile
    import subprocess

    tempdir = tempfile.mkdtemp()
    if debug:
        print
        print "tempdir=", tempdir
        print
    for source_file in source_files:
        shutil.copy(source_file, tempdir)
    include_dirs = [os.path.abspath(d) for d in include_dirs]
    source_files = [os.path.basename(f) for f in source_files]
    setup_code = template % locals()
    if debug:
        print
        print "-"*70
        print setup_code
        print "-"*70
        print

    now = os.getcwd()
    os.chdir(tempdir)
    with open("setup.py", "w") as fp:
        fp.write(setup_code)


    import sys
    sys.path.insert(0, tempdir)
    if debug:
        print
        print "-"*70
        import pprint
        pprint.pprint(sys.path)
        print "-"*70
        print

    assert subprocess.Popen("python setup.py build_ext --force --inplace",
            shell=True).wait() == 0
    print "BUILT"
    #Popen("mycmd" + " myarg", shell=True).wait()
    result = __import__(name)
    print "imported"
    if debug:
        print "imported", result

    sys.path = sys.path[1:]
    os.chdir(now)
    print result
    return result


def remove_labels(graph):
    _remove_labels = lambda succ_list: [s for s, label in succ_list]
    pure_graph = dict((n0, _remove_labels(ni)) for n0, ni in graph.items())
    return pure_graph

def find_cycle(graph_as_dict):
    """ modified version of
    http://neopythonic.blogspot.de/2009/01/detecting-cycles-in-directed-graph.html
    """

    nodes = graph_as_dict.keys()
    for n in graph_as_dict.values():
        nodes.extend(n)
    todo = list(set(nodes))
    while todo:
        node = todo.pop()
        stack = [node]
        while stack:
            top = stack[-1]
            for node in graph_as_dict.get(top, []):
                if node in stack:
                    return stack[stack.index(node):]
                if node in todo:
                    stack.append(node)
                    todo.remove(node)
                    break
            else:
                node = stack.pop()
    return None


def _check_for_cycles_in_mapping(mapping):

    # detect cylces in typedefs
    graph = dict()
    for (alias, type_) in mapping.items():
        successors = type_.all_occuring_base_types()
        graph[alias] = successors

    cycle = find_cycle(graph)
    if cycle is not None:
        info = " -> ".join(map(str, cycle))
        raise Exception("mapping contains cycle: " + info)

def print_map(mapping):
    for k, v in mapping.items():
        print "%8s -> %s" % (k, v)


def flatten(mapping):
    """ resolves nested mappings, eg:
            A -> B
            B -> C[X,D]
            C -> Z
            D -> Y
        is resolved to:
            A -> Z[X,Y]
            B -> Z[X,Y]
            C -> Z
            D -> Y
    """
    _check_for_cycles_in_mapping(mapping)
    # this loop only terminates for cylce free mappings:
    while True:
        for name, type_ in mapping.items():
            transformed = type_.transformed(mapping)
            if transformed != type_:
                mapping[name] = transformed
                break
        else:
            break
