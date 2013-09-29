from setuptools import (setup, find_packages)
import script

requirements = [
    'docopt',
    'htpasswd',
]

setup(
    name='htpasswd-cli',
    version=script.__version__,
    download_url='https://bitbucket.org/toenobu/htpasswd-cli',
    author=script.__author__,
    author_email =script.__author_email__,
    license=script.__licence__,
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'htpasswd-cli = script.htpasswdcli:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2.7',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Topic :: Terminals',
        'Topic :: Utilities',
    ]
)
