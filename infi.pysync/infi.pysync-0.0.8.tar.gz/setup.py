
SETUP_INFO = dict(
    name = 'infi.pysync',
    version = '0.0.8',
    author = 'Tal Yalon',
    author_email = 'tal.yalon@gmail.com',

    url = 'https://infinigit.infinidat.com/host/infi-pysync',
    license = 'PSF',
    description = """rsync-like utility to help sync dev files to a machine""",
    long_description = """rsync-like utility to help sync dev files to a machine""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['infi.recipe.console_scripts', 'distribute', 'infi.watchdog', 'paramiko', 'docopt'],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = ['pysync = infi.pysync:main'],
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

