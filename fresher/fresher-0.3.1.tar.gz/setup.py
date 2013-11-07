try:
    import ez_setup
    ez_setup.use_setuptools()
except ImportError:
    pass

from setuptools import setup

setup(
    name = "fresher",
    version = "0.3.1",
    description = ("Clone of the Cucumber BDD framework for Python forked "
                   "from Freshen"),
    author = "Louis-Dominique Dubeau",
    author_email = "ldd@lddubeau.com",
    url = "http://github.com/lddubeau/fresher",
    license = "GPL",
    packages = ["fresher", "fresher.test"],
    package_data = {'fresher': ['languages.yml']},
    install_requires = [
        'pyparsing>=1.5.0',
        'PyYAML',
        'nose>=0.11.1',
        'six'
    ],
    entry_points = {
        'nose.plugins.0.10': [
            'fresher = fresher.noseplugin:FresherNosePlugin',
            'freshererr = fresher.noseplugin:FresherErrorPlugin'
        ],
        'console_scripts': [
            'fresher-list = fresher.commands:list_steps',
        ],
    },
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
    ]
)
