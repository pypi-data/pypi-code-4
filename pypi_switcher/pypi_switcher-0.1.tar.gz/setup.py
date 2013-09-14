
SETUP_INFO = dict(
    name = 'pypi_switcher',
    version = '0.1',
    author = 'Guy Rozendorn',
    author_email = 'guy@rzn.co.il',

    url = 'http://github.com/grzn/pypi_switcher',
    license = 'PSF',
    description = """a script for switching between pypi servers""",
    long_description = """a script for switching between pypi servers""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['infi.pyutils', 'setuptools'],
    namespace_packages = [],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = ['set_index_url = pypi_switcher:set_index_url'],
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

