
SETUP_INFO = dict(
    name = 'infi.jira_cli',
    version = '0.1.1',
    author = 'Arnon Yaari',
    author_email = 'arnony@infinidat.com',

    url = 'https://infinigit.infinidat.com/host/infi-jira-cli',
    license = 'PSF',
    description = """JIRA command-line tools""",
    long_description = """JIRA command-line tools""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['bunch==1.0.0', 'git-py>=1.0.0', 'infi.execute>=0.0.12', 'docopt>=0.6.1', 'infi.pyutils>=0.0.30', 'infi.docopt-completion>=0.1.4', 'jira-python>=0.13', 'infi.recipe.console-scripts>=0.3.4', 'distribute>=0.6.45', 'schematics>=0.5'],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': ['jish.zsh']},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = ['setup-jish = infi.jira_cli.setup:main', 'jissue = infi.jira_cli:main'],
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

