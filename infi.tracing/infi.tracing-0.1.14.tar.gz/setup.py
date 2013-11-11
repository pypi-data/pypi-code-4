from setuptools.extension import Extension

import sys
if 'setuptools.extension' in sys.modules:
    m = sys.modules['setuptools.extension']
    m.Extension.__dict__ = m._Extension.__dict__


SETUP_INFO = dict(
    name = 'infi.tracing',
    version = '0.1.14',
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
    setup_requires = ['setuptools_cython'],
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


def find_boost_version():
    import subprocess
    code = r"""
#include <boost/version.hpp>
#include <stdio.h>

int main(int, char*[]) {
    printf("%d.%d.%d\n", BOOST_VERSION / 100000, BOOST_VERSION / 100 % 1000, BOOST_VERSION % 100);
    return 0;
}
"""
    with open("boost_version.cpp", "w") as f:
        f.write(code)

    subprocess.check_output("g++ boost_version.cpp -o boost_version", shell=True)
    boost_version_str = subprocess.check_output("./boost_version")

    return boost_version_str.strip()


def get_libraries():
    from platform import system
    from glob import glob
    if system() == "Linux":
        boost_version = find_boost_version()
        return [":libboost_chrono.so.{}".format(boost_version),
                ":libboost_thread.so.{}".format(boost_version)]
    if system() == "Darwin":
        return ["boost_chrono-mt", "boost_thread-mt"]
    raise NotImplementedError("unsupported operating system")


def build_ext_modules():
    from platform import platform
    extra_compile_args = ["-Wno-format-security"]
    extra_link_args = []
    if platform().startswith("Darwin-13"):
        extra_compile_args += ["-stdlib=libstdc++"]
        extra_link_args += ["-stdlib=libstdc++"]
    return [Extension("infi.tracing.ctracing",
               language="c++",
               sources=["src/infi/tracing/ctracing.pyx", "src/infi/tracing/thread_storage.cpp",
                        "src/infi/tracing/trace_dump.cpp"],
               include_dirs=["src/infi/tracing"],
               define_macros=[("_REENTRANT", 1)],
               libraries=get_libraries(),
               extra_compile_args=extra_compile_args,
               extra_link_args=extra_link_args)]


def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['ext_modules'] = build_ext_modules()
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()
