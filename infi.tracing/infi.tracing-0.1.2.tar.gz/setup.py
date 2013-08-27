from setuptools.extension import Extension

import sys
if 'setuptools.extension' in sys.modules:
    m = sys.modules['setuptools.extension']
    m.Extension.__dict__ = m._Extension.__dict__


SETUP_INFO = dict(
    name = 'infi.tracing',
    version = '0.1.2',
    author = 'Tal Yalon',
    author_email = 'tal.yalon@gmail.com',

    url = 'https://infinigit.infinidat.com/host/tracing',
    license = 'PSF',
    description = """short description here""",
    long_description = """long description here""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['distribute', 'greenlet', 'cython', 'infi.pyutils'],
    setup_requires = ['Cython'],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': ['*.pxd', '*.h', 'greenlet.h', '*.hpp', '*.pyx']},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = [],
        gui_scripts = [],
        ),

)

if SETUP_INFO['url'] is None:
    _ = SETUP_INFO.pop('url')

def build_ext_modules():
    return [Extension("infi.tracing.ctracing",
               language="c++",
               sources=["src/infi/tracing/ctracing.pyx", "src/infi/tracing/thread_storage.cpp", 
                        "src/infi/tracing/trace_dump.cpp"],
               include_dirs=["src/infi/tracing"],
               define_macros=[("_REENTRANT", 1)],
               libraries=["stdc++"],
               extra_compile_args=["-std=c++11", "-Wno-format-security"],
               extra_link_args=["-std=c++11"])]

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['ext_modules'] = build_ext_modules()
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)
 
if __name__ == '__main__':
    setup()
