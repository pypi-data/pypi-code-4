
SETUP_INFO = dict(
    name = 'infi.pypi_manager',
    version = '0.4.8',
    author = 'wiggin15',
    author_email = 'wiggin15@yahoo.com',

    url = 'https://github.com/Infinidat/infi.pypi_manager',
    license = 'PSF',
    description = """A small tool we use to migrate/mirror distributions from pypi.python.org to our local djangopypi server""",
    long_description = """A small tool we use to migrate/mirror distributions from pypi.python.org to our local djangopypi server""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['infi.pyutils', 'infi.execute', 'distribute', 'docopt', 'PrettyTable'],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = ['mirror_package = infi.pypi_manager.scripts.mirror_package:mirror_package', 'hard_install = infi.pypi_manager.scripts.hard_install:main', 'compare_pypi_repos = infi.pypi_manager.scripts.compare_pypi_repos:main'],
        gui_scripts = [],
        ),
)

if SETUP_INFO['url'] is None:
    _ = SETUP_INFO.pop('url')

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

