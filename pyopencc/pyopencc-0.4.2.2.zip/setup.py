from distutils.core import setup, Extension

include_dirs = ['/usr/include/opencc', '/usr/local/include/opencc']
library_dirs = ['/usr/local/lib']
libraries = ['opencc']
runtime_library_dirs = []
extra_objects = []
define_macros = []

setup(name = "pyopencc",
      version = "0.4.2.2",
      author = "Guangming Li",
      author_email = "leeful@gmail.com",
      license = "Apache License",
      url = "http://code.google.com/p/opencc/",
      packages = ["pyopencc"],
      ext_package = "pyopencc",
      ext_modules = [Extension( name = "opencc",
                                sources = ["src/opencc.c"],
                                include_dirs = include_dirs,
                                library_dirs = library_dirs,
                                runtime_library_dirs = runtime_library_dirs,
                                libraries = libraries,
                                extra_objects = extra_objects,
                                define_macros = define_macros
                              )],
      )

