from setuptools import setup, find_packages
import os

setup(
    name = "chssh",
    version = "0.2",
    packages = find_packages(),
    install_requires = ['pychef>=0.2'],

    author = 'Kris Wehner',
    author_email = 'kris@further.com',
    description = 'ssh wrappers to transparently use chef node names instead of hostnames',
    long_description = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    license = 'BSD',
    keywords = '',
    url = 'http://github.com/kriswehner/chssh',
    classifiers = [
        #'Development Status :: 1 - Planning',
        #'Development Status :: 2 - Pre-Alpha',
        #'Development Status :: 3 - Alpha',
        #'Development Status :: 4 - Beta',
        'Development Status :: 5 - Production/Stable',
        #'Development Status :: 6 - Mature',
        #'Development Status :: 7 - Inactive',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],

    entry_points = {
        'console_scripts': [
            'chssh = chssh.cmd:ssh',
            'chscp = chssh.cmd:scp',
        ]
    }
)