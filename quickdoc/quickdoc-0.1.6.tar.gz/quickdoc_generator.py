
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
    parser.add_argument("--" + name, action="store_const", dest=name.replace("-", "_"), const=True, default=default)
    parser.add_argument("--no-" + name, action="store_const", dest=name.replace("-", "_"), const=False, default=default)


def flatten(list):
    return [v for l in list for v in l]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--discover", action="append", nargs="+", default=[])
    parser.add_argument("--modules", action="append", nargs="+", default=[])
    parser.add_argument("--exclude", action="append", nargs="+", default=[])
    parser.add_argument("--interlink", action="append", default=[])
    parser.add_argument("--rst", default=None)
    parser.add_argument("--html", default=None)
    parser.add_argument("--skip-failed", action="store_true")
    parser.add_argument("--theme", default=None)
    parser.add_argument("--title", default=None)
    make_switch(parser, "inheritance", False)
    make_switch(parser, "mro", True)
    make_switch(parser, "overrides", True)
    args = parser.parse_args()
    args.discover = flatten(args.discover)
    args.modules = flatten(args.modules)
    args.exclude = flatten(args.exclude)
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
                YIELD if f.name.endswith(".py") and not f.name.startswith("__") and f != folder.child("setup.py") else 
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
    
    exclude = set(args.exclude)
    for name in set(module_names):
        current = name
        # See if the module or any of its parent packages are in the exclude
        # list
        while current:
            if current in exclude:
                print "Excluding %s on request" % name
                module_names.discard(name)
                break
            current, _, _ = current.rpartition(".")
    
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
    print "Final list of modules to document: %s" % ", ".join(m.__name__ for m in modules)
    
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
        extensions = []
        
        if args.title:
            f.write("project = {0!r}\n".format(args.title))
        if args.theme:
            f.write("html_theme = {0!r}\n".format(args.theme))
        
        if args.interlink:
            extensions.append("sphinx.ext.intersphinx")
            intersphinx_mapping = {}
            for url in args.interlink:
                # We're not supporting explicit keys for now, so just use the
                # URL to make sure we've got a unique one. Perhaps in the
                # future I'll add something like --named-interlink <name> <url>
                # to support qualified interlinking.
                intersphinx_mapping[url] = (url, None)
            f.write("intersphinx_mapping = {0!r}\n".format(intersphinx_mapping))
            f.write("intersphinx_cache_limit = 0\n")
        
        f.write("extensions = {0!r}\n".format(extensions))
    
    with rst.child("contents.rst").open("wb") as contents:
        contents.write(".. toctree::\n")
        for module in modules:
            contents.write("   modules/{0}.rst\n".format(module.__name__))
    
    for module in modules:
        with module_dir.child(module.__name__ + ".rst").open("wb") as m:
            display_module(module, m, 0, args)
    
    if args.html:
        html = File(args.html)
        html.delete(ignore_missing=True)
        html.create_folder(recursive=True)
        with rst.as_working:
            subprocess.check_output(["sphinx-build", "-b", "html",
                                     rst.path, html.path])
        # Include a simple index.html that redirects to py-modindex.html. I'll
        # likely make the index page's content configurable at some point.
        html.child("index.html").write("""
        <html>
            <head>
                <meta http-equiv="refresh" content="0; url=py-modindex.html"/>
            </head>
            <body>
                <a href="py-modindex.html">py-modindex.html</a>
            </body>
        </html>""")


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
    print "module " + module.__name__
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
                print "  Unknown type, skipping {}".format(name)
    function_names = [n for n in sorted(dir(module)) if isinstance(getattr(module, n), types.FunctionType) and should_document_module_member(n, getattr(module, n), module)]
    if function_names:
        title(stream, level + 1, "Functions")
        for name in function_names:
            thing = getattr(module, name)
            display_function(thing, stream, level + 2, args, name)


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
    print "  class {}".format(cls.__name__)
    title(stream, level, "Class " + cls.__name__)
    stream.write(inspect.getdoc(cls) or "")
    if cls.__init__ is object.__init__:
        spec = ""
    else:
        try:
            inspect.getargspec(cls.__init__)
        except:
            print "    Skipping class spec"
            spec = ""
        else:
            spec = inspect.formatargspec(*inspect.getargspec(cls.__init__))
    
    if args.mro:
        mro = inspect.getmro(cls)[1:-1]
        if mro:
            stream.write("\n\n")
            stream.write("*Method resolution order:* ")
            stream.write(", ".join(":obj:`~{0}.{1}`".format(c.__module__, c.__name__) for c in mro))

    stream.write("\n\n.. class:: " + cls.__name__ + spec + "\n\n")
    class_stream = IndentStream(stream, "   ")
    class_stream.write(inspect.getdoc(cls.__init__) or "")
    
    # Sort out aliases. thing_dict maps names (the names we're going to
    # document things under) to 2-tuples (thing, names), where thing is the
    # thing itself and names is a list of names under which it can be found
    # (including the key under which the tuple is registered in thing_dict)
    thing_dict = {}
    for name, kind, definer, thing in sorted(inspect.classify_class_attrs(cls)):
        if definer is cls and pydoc.visiblename(name, None, thing) and name != "__init__":
            # See if we've already seen this thing before
            for k, (v, names) in thing_dict.iteritems():
                # We have to use == here instead of "is" as the bound method
                # object returned for each attribute of a class is generated on
                # the fly, so it's different each time we request it. They
                # compare equal, though, if they wrap the same underlying
                # function, so using == works as expected.
                if v == thing:
                    # We have, under the name k. Add an alias for it under our
                    # current name.
                    names.append(name)
                    break
            else:
                # We haven't seen it before, so add a new entry for it.
                thing_dict[name] = (thing, [name])
    
    for _, (thing, names) in sorted(thing_dict.iteritems()):
        # TODO: Handle nested classes here
        if should_document_as_method(thing):
            try:
                inspect.getargspec(thing)
            except:
                print "    Couldn't get argspec, skipping {}".format(names)
            else:
                display_method(thing, class_stream, level + 1, args, cls, names)
        elif should_document_as_property(thing):
            display_property(thing, class_stream, level + 1, args, cls, names)
        else:
            print "    Not a method or property, skipping {}".format(names)
    
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
                class_stream.write("\n\n*Members inherited from class* :obj:`~{0}.{1}`\\ *:* ".format(base_class.__module__, base_class.__name__))
                class_stream.write(", ".join(":obj:`~{0}.{1}.{2}`".format(base_class.__module__, base_class.__name__, n) for n in inheritance_dict[base_class]))


def display_method(function, stream, level, args, cls, names):
    print "    method {!r}".format(names)
    signature = inspect.formatargspec(*inspect.getargspec(function))
    stream.write("\n\n.. method:: " + names[0] + signature + "\n")
    for name in names[1:]:
        stream.write("            " + name + signature + "\n")
    stream.write("\n")
    method_stream = IndentStream(stream, "   ")
    method_stream.write(inspect.getdoc(function) or "")
    display_override_info(function, method_stream, level, args, cls, names)


def display_property(prop, stream, level, args, cls, names): #@DuplicatedSignature
    print "    property {!r}".format(names)
    stream.write("\n\n.. attribute:: " + names[0] + "\n")
    for name in names[1:]:
        stream.write("               " + name + "\n")
    stream.write("\n")
    prop_stream = IndentStream(stream, "   ")
    prop_stream.write(inspect.getdoc(prop) or "")
    display_override_info(prop, prop_stream, level, args, cls, names)


def display_override_info(thing, stream, level, args, cls, names):
    found_override = False
    for name in names:
        if args.overrides:
            for base_class in inspect.getmro(cls)[1:]:
                # Special-case: ignore overrides from object as these tend to be overly
                # verbose (we don't need a note on every __init__, for example, telling
                # us that it overrides object.__init__)
                if name in base_class.__dict__ and base_class is not object:
                    if not found_override:
                        found_override = True
                        stream.write("\n")
                    stream.write("\n|  *Overrides* :obj:`~{0}.{1}.{2}` *in class* :obj:`~{0}.{1}`".format(base_class.__module__, base_class.__name__, name))
                    break


def display_function(function, stream, level, args, name): #@DuplicatedSignature
    print "  Function " + name
    stream.write("\n\n.. function:: " + name + inspect.formatargspec(*inspect.getargspec(function)) + "\n\n")
    function_stream = IndentStream(stream, "   ")
    function_stream.write(inspect.getdoc(function) or "")


def should_document_as_method(thing):
    return callable(thing)


def should_document_as_property(thing):
    return isinstance(thing, property)


if __name__ == "__main__":
    main()



















