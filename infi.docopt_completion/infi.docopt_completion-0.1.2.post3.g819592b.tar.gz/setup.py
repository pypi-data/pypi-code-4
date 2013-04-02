
SETUP_INFO = dict(
    name = 'infi.docopt_completion',
    version = '0.1.2.post3.g819592b',
    author = 'wiggin15',
    author_email = 'wiggin15@yahoo.com',

    url = 'https://github.com/Infinidat/infi.docopt_completion',
    license = 'PSF',
    description = """docopt completion tool""",
    long_description = """a tool that creates ZSH completion for docopt scripts""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['distribute', 'docopt'],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = ['docopt-completion = infi.docopt_completion.docopt_completion:main'],
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

