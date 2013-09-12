
SETUP_INFO = dict(
    name = 'infi.jira_cli',
    version = '0.1.3.post6.g2e44345',
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

    install_requires = ['infi.execute', 'schematics', 'infi.recipe.console-scripts', 'jira-python', 'infi.docopt-completion', 'distribute', 'bunch==1.0.0', 'infi.pyutils', 'git-py', 'docopt', 'PrettyTable'],
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

