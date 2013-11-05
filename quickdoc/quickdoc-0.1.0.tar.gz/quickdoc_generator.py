
import argparse
from fileutils import File
import importlib
import inspect
from singledispatch import singledispatch
import types
import pydoc
from collections import namedtuple

FILE = File(__file__)
MethodWrapper = namedtuple("MethodWrapper", ["function"])
PropertyWrapper = namedtuple("PropertyWrapper", ["name", "prop"])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("modules", nargs="+")
    parser.add_argument("--rst", default=None)
    args = parser.parse_args()
    #output_dir = File(args.output)
    #output_dir.create_folder(ignore_existing=True, recursive=True)
    modules = set()
    for module_name in args.modules:
        module = importlib.import_module(module_name)
        modules.add(module)
    modules = sorted(modules, key=lambda m: m.__name__)
    
    rst = File(args.rst)
    rst.create_folder(ignore_existing=True, recursive=True)
    module_dir = rst.child("modules")
    module_dir.create_folder(True, True)
    
    conf = "project = {0!r}\n".format("Test Project")
    rst.child("conf.py").write(conf)
    
    with rst.child("contents.rst").open("wb") as contents:
        contents.write(".. toctree::\n")
        for module in modules:
            contents.write("   modules/{0}.rst\n".format(module.__name__))
    
    for module in modules:
        with module_dir.child(module.__name__ + ".rst").open("wb") as m:
            display(module, m, 0)


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
def display(thing, stream, level):
    print "SKIPPING %r" % thing


@display.register(types.ModuleType)
def _(module, stream, level):
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
            display(thing, stream, level + 1)
    function_names = [n for n in sorted(dir(module)) if isinstance(getattr(module, n), types.FunctionType) and should_document_module_member(n, getattr(module, n), module)]
    if function_names:
        title(stream, level + 1, "Functions")
        for name in function_names:
            thing = getattr(module, name)
            display(thing, stream, level + 2)


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


@display.register(type)
def _(cls, stream, level): #@DuplicatedSignature
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
    stream.write("\n\n.. class:: " + cls.__name__ + spec + "\n\n")
    class_stream = IndentStream(stream, "   ")
    class_stream.write(inspect.getdoc(cls.__init__) or "")
    for name in sorted(dir(cls)):
        print "Class member {}".format(name)
        thing = getattr(cls, name)
        if not name.startswith("__") and pydoc.visiblename(name, None, thing):
            if callable(thing):
                try:
                    inspect.getargspec(thing)
                except:
                    print "Skipping"
                else:
                    display(MethodWrapper(thing), class_stream, level + 1)
            elif isinstance(thing, property):
                display(PropertyWrapper(name, thing), class_stream, level + 1)
            else:
                display(thing, class_stream, level + 1)


@display.register(MethodWrapper)
def _(wrapper, stream, level): #@DuplicatedSignature
    function = wrapper.function
    stream.write("\n\n.. method:: " + function.__name__ + inspect.formatargspec(*inspect.getargspec(function)) + "\n\n")
    method_stream = IndentStream(stream, "   ")
    method_stream.write(inspect.getdoc(function) or "")


@display.register(PropertyWrapper)
def _(prop, stream, level): #@DuplicatedSignature
    stream.write("\n\n.. attribute:: " + prop.name + "\n\n")
    prop_stream = IndentStream(stream, "   ")
    prop_stream.write(inspect.getdoc(prop.prop) or "")


@display.register(types.FunctionType)
def _(function, stream, level): #@DuplicatedSignature
    stream.write("\n\n.. function:: " + function.__name__ + inspect.formatargspec(*inspect.getargspec(function)) + "\n\n")
    function_stream = IndentStream(stream, "   ")
    function_stream.write(inspect.getdoc(function) or "")


if __name__ == "__main__":
    main()



















