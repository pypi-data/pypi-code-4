from distutils.core import setup
import sys

py_version_t = sys.version_info[:2]
py_version_s = ".".join([str(x) for x in py_version_t])


if __name__ == '__main__':
    setup(
        name = 't3',
        version = '0.1',
        description = 'protoplasma of a system for functional testing',
        author = 'Kay Schluehr',
        author_email = 'kay@fiber-space.de',
        url = 'http://www.fiber-space.de/',
        download_url = 'http://pypi.python.org/pypi/t3/0.1',
        license = "BSD",
        packages = ['t3'],
    )

