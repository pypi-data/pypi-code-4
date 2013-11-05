
import argparse
from fileutils import File, YIELD, SKIP, RECURSE, create_temporary_folder
import importlib
import inspect
from singledispatch import singledispatch
import types
import pydoc
from collections import namedtuple
import sys
import subprocess

FILE = File(__file__)
MethodWrapper = namedtuple("MethodWrapper", ["function"])
PropertyWrapper = namedtuple("PropertyWrapper", ["name", "prop"])

def make_switch(parser, name, default):
    parser.add_argument("--" + name, action="store_const", dest=name, const=True, default=default)
    parser.add_argument("--no-" + name, action="store_const", dest=name, const=False, default=default)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--discover", nargs="+", default=[])
    parser.add_argument("--modules", nargs="+", default=[])
    parser.add_argument("--rst", default=None)
    parser.add_argument("--html", default=None)
    parser.add_argument("--skip-failed", action="store_true")
    parser.add_argument("--theme", default=None)
    parser.add_argument("--title", default=None)
    make_switch(parser, "inheritance", False)
    make_switch(parser, "mro", True)
    make_switch(parser, "overrides", True)
    args = parser.parse_args()
    #output_dir = File(args.output)
    #output_dir.create_folder(ignore_existing=True, recursive=True)
    
    if not (args.modules or args.discover):
        print "Error: need one of --modules or --discover."
        print "Use --help for more info."
        sys.exit(1)
    
    module_names = set()
    for folder_name in args.discover:
        folder = File(folder_name)
        # Add the folder to the path so we can import things from it
        sys.path.insert(0, folder.path)
        print "Discovering packages and modules in %r..." % folder.path
        for thing in folder.recurse(lambda f:
                YIELD if f.name.endswith(".py") and f.name != "__init__.py" and f != folder.child("setup.py") else 
                True if f.child("__init__.py").exists else
                RECURSE if f == folder else SKIP):
            name = thing.get_path(relative_to=folder, separator=".")
            # Strip off trailing ".py" for modules
            if thing.is_file:
                name = name[:-3]
            print "Discovered package/module %s" % name
            module_names.add(name)
    for name in args.modules:
        print "Including module %s on request" % name
        module_names.add(name)
    
    modules = set()
    for module_name in module_names:
        print "Importing %s" % module_name
        try:
            module = importlib.import_module(module_name)
        except:
            if args.skip_failed:
                print "IMPORT FAILED, ignoring."
            else:
                raise
        else:
            modules.add(module)
    
    modules = sorted(modules, key=lambda m: m.__name__)
    
    if args.rst:
        rst = File(args.rst)
        rst.delete(ignore_missing=True)
    else:
        rst = create_temporary_folder(delete_on_exit=True)
    rst.create_folder(ignore_existing=True, recursive=True)
    module_dir = rst.child("modules")
    module_dir.create_folder(True, True)
    
    # conf = "project = {0!r}\n".format("Test Project")
    with rst.child("conf.py").open("wb") as f:
        if args.title:
            f.write("project = {0!r}\n".format(args.title))
        if args.theme:
            f.write("html_theme = {0!r}\n".format(args.theme))
    
    with rst.child("contents.rst").open("wb") as contents:
        contents.write(".. toctree::\n")
        for module in modules:
            contents.write("   modules/{0}.rst\n".format(module.__name__))
    
    for module in modules:
        with module_dir.child(module.__name__ + ".rst").open("wb") as m:
            display_module(module, m, 0, args)
    
    if args.html:
        html = File(args.html)
        with rst.as_working:
            subprocess.check_output(["sphinx-build", "-b", "html",
                                     rst.path, html.path])


def title(stream, level, text):
    character = "=-^%#&"[level]
    stream.write("\n\n" + character * len(text) + "\n" + text + "\n" + character * len(text) + "\n\n")


class IndentStream(object):
    def __init__(self, stream, indent="", initial=True):
        self.stream = stream
        self.indent = indent
        self.need_indent = initial
    
    def write(self, text):
        for char in text:
            if self.need_indent and char != "\n":
                self.need_indent = False
                self.stream.write(self.indent)
            self.stream.write(char)
            if char == "\n":
                self.need_indent = True


@singledispatch
def display(thing, stream, level, args):
    print "SKIPPING {0!r}".format(thing)


def display_module(module, stream, level, args):
    synopsis, doc = pydoc.splitdoc(inspect.getdoc(module) or "")
    title(stream, level, ":mod:`" + module.__name__ + "` --- " + synopsis)
    stream.write(".. module:: " + module.__name__ + "\n   :synopsis: " + synopsis + "\n\n")
    stream.write(doc or "")
    # stream.write("\n\n.. contents:: Things\n   :depth: 1\n   :local:\n\n")
    for name in sorted(dir(module)):
        thing = getattr(module, name)
        if isinstance(thing, types.FunctionType):
            continue
        if should_document_module_member(name, thing, module):
            if isinstance(thing, type):
                display_class(thing, stream, level + 1, args)
            elif isinstance(thing, types.FunctionType):
                display_function(thing, stream, level + 1, args)
            else:
                print "Unknown type, skipping module member {0!r}".format(name)
    function_names = [n for n in sorted(dir(module)) if isinstance(getattr(module, n), types.FunctionType) and should_document_module_member(n, getattr(module, n), module)]
    if function_names:
        title(stream, level + 1, "Functions")
        for name in function_names:
            thing = getattr(module, name)
            display_function(thing, stream, level + 2, args)


def should_document_module_member(name, thing, module):
    if not pydoc.visiblename(name, getattr(module, "__all__", None), thing):
        return False
    if hasattr(module, "__all__"):
        return True
    if isinstance(thing, types.ModuleType):
        return False
    if hasattr(thing, "__module__") and thing.__module__ != module.__name__:
        return False
    # Skip aliases for now. Might want to document aliases specially in the
    # future.
    if hasattr(thing, "__name__") and thing.__name__ != name:
        return False
    return True


def display_class(cls, stream, level, args): #@DuplicatedSignature
    print "Class {}".format(cls.__name__)
    title(stream, level, "Class " + cls.__name__)
    stream.write(inspect.getdoc(cls) or "")
    if cls.__init__ is object.__init__:
        spec = ""
    else:
        try:
            inspect.getargspec(cls.__init__)
        except:
            print "Skipping"
            spec = ""
        else:
            spec = inspect.formatargspec(*inspect.getargspec(cls.__init__))
    
    if args.mro:
        mro = inspect.getmro(cls)[1:-1]
        if mro:
            stream.write("\n\n")
            stream.write("*Method resolution order:* ")
            stream.write(", ".join(":class:`~{0}.{1}`".format(c.__module__, c.__name__) for c in mro))

    stream.write("\n\n.. class:: " + cls.__name__ + spec + "\n\n")
    class_stream = IndentStream(stream, "   ")
    class_stream.write(inspect.getdoc(cls.__init__) or "")
    
    
    for name, kind, definer, thing in sorted(inspect.classify_class_attrs(cls)):
        print "Class member {}".format(name)
        if definer is cls and pydoc.visiblename(name, None, thing) and name != "__init__":
            # TODO: Handle nested classes here
            if should_document_as_method(thing):
                try:
                    inspect.getargspec(thing)
                except:
                    print "Couldn't get argspec, skipping"
                else:
                    display_method(thing, class_stream, level + 1, args, cls, name)
            elif should_document_as_property(thing):
                display_property(thing, class_stream, level + 1, args, cls, name)
            else:
                print "Not a method or property, skipping"
    
    if args.inheritance:
        inheritance_dict = {}
        for name, kind, definer, thing in sorted(inspect.classify_class_attrs(cls)):
            if (
                    definer is not cls and
                    definer is not object and
                    pydoc.visiblename(name, None, thing) and
                    name not in ["__dict__", "__weakref__"] and
                    (should_document_as_method(thing) or should_document_as_property(thing))):
                inheritance_dict.setdefault(definer, []).append(name)
        for base_class in inspect.getmro(cls):
            if base_class in inheritance_dict:
                class_stream.write("\n\n*Members inherited from class* :class:`~{0}.{1}`\\ *:* ".format(base_class.__module__, base_class.__name__))
                class_stream.write(", ".join(":obj:`~{0}.{1}.{2}`".format(base_class.__module__, base_class.__name__, n) for n in inheritance_dict[base_class]))


def display_method(function, stream, level, args, cls, name):
    stream.write("\n\n.. method:: " + function.__name__ + inspect.formatargspec(*inspect.getargspec(function)) + "\n\n")
    method_stream = IndentStream(stream, "   ")
    method_stream.write(inspect.getdoc(function) or "")
    display_override_info(function, method_stream, level, args, cls, name)


def display_property(prop, stream, level, args, cls, name): #@DuplicatedSignature
    stream.write("\n\n.. attribute:: " + name + "\n\n")
    prop_stream = IndentStream(stream, "   ")
    prop_stream.write(inspect.getdoc(prop) or "")
    display_override_info(prop, prop_stream, level, args, cls, name)


def display_override_info(thing, stream, level, args, cls, name):
    if args.overrides:
        for base_class in inspect.getmro(cls)[1:]:
            # Special-case: ignore overrides from object as these tend to be overly
            # verbose (we don't need a note on every __init__, for example, telling
            # us that it overrides object.__init__)
            if name in base_class.__dict__ and base_class is not object:
                stream.write("\n\n")
                stream.write("*Overrides* :obj:`~{0}.{1}.{2}` *in class* :class:`~{0}.{1}`".format(base_class.__module__, base_class.__name__, name))
                break


def display_function(function, stream, level, args): #@DuplicatedSignature
    stream.write("\n\n.. function:: " + function.__name__ + inspect.formatargspec(*inspect.getargspec(function)) + "\n\n")
    function_stream = IndentStream(stream, "   ")
    function_stream.write(inspect.getdoc(function) or "")


def should_document_as_method(thing):
    return callable(thing)


def should_document_as_property(thing):
    return isinstance(thing, property)


if __name__ == "__main__":
    main()



















