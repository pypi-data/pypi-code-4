from setuptools import setup, find_packages
import pwr as module

setup(
    name='pwr',
    version = module.__version__,
    author = module.__author__,
    author_email = module.__email__,
    description = module.__description__,
    license = module.__license__,
    keywords = module.__keywords__,
    url = module.__url__,
    install_requires = ['PySide','Pygments'],
    package_data = {
        # If any package contains *.txt or *.rst or *.md files, include them:
        '': ['*.txt', '*.rst', '*.md'],
        # And include any *.msg files found in the package, too:
        'pwr' : ['images/*', '*.*'],
    },
    packages=find_packages(),
    long_description='Simple python wysiwyg redactor based on Qt, QtWebkit and html',
    include_package_data=True,
#    test_suite='tests',
    entry_points={
        'console_scripts':
            ['pwr = pwr.wysiwyg:main',],
        'gui_scripts':
            ['pwr = pwr.wysiwyg:main',],
        }
)