"""pcli installation script."""

from setuptools import find_packages, setup

if __name__ == "__main__":
    with open("README") as readme:
        setup(
            name = "pcli",
            version = "0.2",

            description = readme.readline().strip(),
            long_description = readme.read().strip() or None,
            url = "http://github.com/KonishchevDmitry/pcli",

            license = "GPL3",
            author = "Dmitry Konishchev",
            author_email = "konishchev@gmail.com",

            classifiers = [
                "Development Status :: 4 - Beta",
                "Intended Audience :: Developers",
                "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                "Operating System :: MacOS :: MacOS X",
                "Operating System :: POSIX",
                "Operating System :: Unix",
                "Programming Language :: Python :: 3",
                "Topic :: Software Development :: Libraries :: Python Modules",
            ],
            platforms = [ "unix", "linux", "osx" ],

            packages = find_packages(),
        )
