import os

from ctypes import *

class SassOptions(Structure):
    _fields_ = [
        ("output_style", c_int),
        ("source_comments", c_int),
        ("include_paths", c_char_p),
        ("image_path", c_char_p),
    ]

class SassContext(Structure):
    _fields_ = [
        ("source_string", c_char_p),
        ("output_string", c_char_p),
        ("sass_options", SassOptions),
        ("error_status", c_int),
        ("error_message", c_char_p),
    ]

class SassFileContext(Structure):
    _fields_ = [
        ("input_path", c_char_p),
        ("output_string", c_char_p),
        ("sass_options", SassOptions),
        ("error_status", c_int),
        ("error_message", c_char_p),
    ]

class SassFolderContext(Structure):
    _fields_ = [
        ("search_path", c_char_p),
        ("output_path", c_char_p),
        ("sass_options", SassOptions),
        ("error_status", c_int),
        ("error_message", c_char_p),
    ]

class LibSass(object):
    """Wrapper class around libsass.

    The class provides methods that mimic the functions in sass_interface.h

    """

    def __init__(self):
        self.clib = None

    def _load(self):
        """Loads the libsass library if it isn't already loaded."""
        if self.clib is None:
            root_path = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__ )), '..'))
            path1 = os.path.join(root_path, 'sass.so')
            path2 = os.path.join(root_path, '..', 'sass.so')

            if os.path.exists(path1):
                self.clib = cdll.LoadLibrary(path1)
            elif os.path.exists(path1):
                self.clib = cdll.LoadLibrary(path2)
            else:
                raise Exception("Could not load library")

            self.clib.sass_new_context.restype = POINTER(SassContext)
            self.clib.sass_new_file_context.restype = POINTER(SassFileContext)
            self.clib.sass_new_folder_context.restype = POINTER(SassFolderContext)

            self.clib.sass_compile.restype = c_int
            self.clib.sass_compile.argtypes = [POINTER(SassContext)]

            self.clib.sass_compile_file.restype = c_int
            self.clib.sass_compile_file.argtypes = [POINTER(SassFileContext)]

            self.clib.sass_compile_folder.restype = c_int
            self.clib.sass_compile_folder.argtypes = [POINTER(SassFolderContext)]

    def __getattribute__(self, name):
        attr = object.__getattribute__(self, name)
        if hasattr(attr, '__call__') and name != "_load":
            def load_wrapper(*args, **kwargs):
                self._load()
                return attr(*args, **kwargs)
            return load_wrapper
        else:
            return attr

    def sass_new_context(self):
        """Gets a new sass context object.

        This calls the `sass_new_context()` function.

        """
        return self.clib.sass_new_context()

    def sass_new_file_context(self):
        """Gets a new sass file context object.

        This calls the `sass_new_file_context()` function.

        """
        return self.clib.sass_new_file_context()

    def sass_new_folder_context(self):
        """Gets a new sass folder context object.

        This calls the `sass_new_folder_context()` function.

        """
        return self.clib.sass_new_folder_context()

    def compile(self, ctx):
        """Compiles a string to CSS

        This calls the `sass_compile` function.

        :param :class:`pylibsass.sass.SassContext` ctx: The libsass context

        """
        return self.clib.sass_compile(ctx)

    def compile_file(self, ctx):
        """Compiles a file to CSS

        This calls the `sass_compile_file` function.

        :param :class:`pylibsass.sass.SassFileContext` ctx: The libsass context

        """
        return self.clib.sass_compile_file(ctx)

    def compile_folder(self, ctx):
        """Compiles a folder to CSS

        This calls the `sass_compile_folder` function.

        :param :class:`pylibsass.sass.SassFolderContext` ctx: The libsass context

        """
        return self.clib.sass_compile_folder(ctx)

SASS_CLIB = LibSass()

def compile_str(contents):
    """Compiles a SASS string

    :param str contents: The SASS contents to compile
    :returns: The compiled CSS

    """
    ctx = SASS_CLIB.sass_new_context()
    ctx.contents.source_string = c_char_p(contents)

    SASS_CLIB.compile(ctx)

    if ctx.contents.error_status:
        print(ctx.contents.error_message)

    return ctx.contents.output_string or ""
