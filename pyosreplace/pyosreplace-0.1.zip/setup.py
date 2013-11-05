#!/usr/bin/env python
import sys
import os
import subprocess
from distutils.core import setup, Command
from distutils.extension import Extension


class TestCommand(Command):
    """Hack for setup.py with implicit build_ext -i
    """
    user_options = []

    def initialize_options(self):
        self.rootdir = os.getcwd()

    def finalize_options(self):
        pass

    def remove_ext(self):
        """Remove extensions
        """
        for fname in os.listdir(self.rootdir):
            if fname.endswith("pyd"):
                os.unlink(os.path.join(self.rootdir, fname))

    def get_lib_dirs(self):
        """Get version, platform and configuration dependend lib dirs

        Distutils caches the build command object on the distribution object.
        We can retrieve the object to retrieve the paths to the directories
        inside the build directory.
        """
        build = self.distribution.command_obj["build"]
        builddirs = set()
        for attrname in 'build_platlib', 'build_lib', 'build_purelib':
            builddir = getattr(build, attrname, None)
            if not builddir:
                continue
            builddir = os.path.abspath(os.path.join(self.rootdir, builddir))
            if not os.path.isdir(builddir):
                continue
            builddirs.add(builddir)
        return builddirs

    def run(self):
        self.remove_ext()
        # force a build with build_ext
        self.run_command("build")
        # get lib dirs from build object
        libdirs = self.get_lib_dirs()
        # add lib dirs to Python's search path
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join(libdirs)
        # and finally run the test command
        errno = subprocess.check_call([sys.executable, "tests.py"], env=env)
        raise SystemExit(errno)

long_description = []
with open("README.txt") as f:
    long_description.append(f.read())
with open("CHANGES.txt") as f:
    long_description.append(f.read())

setup(
    name="pyosreplace",
    version="0.1",
    ext_modules=[Extension("osreplace", ["osreplace.c"])],
    py_modules=[],
    cmdclass={"test": TestCommand},
    author="Christian Heimes",
    author_email="christian@python.org",
    maintainer="Christian Heimes",
    maintainer_email="christian@python.org",
    url="https://bitbucket.org/tiran/pyosreplace",
    keywords="rename replace atomic movefileex",
    platforms="Windows",
    license="PSFL",
    description="os.replace() backport for Python 2.x",
    long_description="\n".join(long_description),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Python Software Foundation License",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: C",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
    ],
)
