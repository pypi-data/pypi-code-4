from setuptools import setup, find_packages

DATA_FILES = [
    ('pylocalsmtp', ["LICENSE", "README.md"])
]

LONG_DESCRIPTION = "%s\n\n%s" % (open('README.md').read(), open('CHANGES.md').read())

setup(
    name='pylocalsmtp',
    version='0.4.1',
    description='Ouvre un mini serveur SMTP en local avec inbox dans une interface web.',
    long_description=LONG_DESCRIPTION,
    url='https://bitbucket.org/m_clement/pylocalsmtp/',
    license='MIT',
    author='Martyn CLEMENT',
    author_email='martyn.clement@gmail.com',
    packages=find_packages(),
    data_files=DATA_FILES,
    include_package_data=True,
    install_requires=[
        'peewee',
        'tornado==3.0.1',
        'wsgiref==0.1.2',
        'sockjs-tornado'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Natural Language :: French',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    entry_points={
        'console_scripts': [
            'pylocalsmtpd=pylocalsmtp.cmd:run',
        ],
    }
)
