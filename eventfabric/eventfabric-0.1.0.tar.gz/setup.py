'''setup.py for eventfabric'''
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


try:
    with open('README.rest') as f:
        README = f.read()
except IOError:
    README = None

setup(
    name='eventfabric',
    version='0.1.0',
    py_modules=['eventfabric'],
    package_dir={'': 'src'},
    data_files=[
        ('', ['README.rest'])
    ],
    zip_safe=False,
    description='Event Fabric API client library',
    long_description=README,
    license='MIT License',
    author='Mariano Guerra',
    author_email='mariano' '@' 'marianoguerra.org',
    url='https://github.com/EventFabric/python-api',
    install_requires=['requests'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Environment :: No Input/Output (Daemon)',
        'Environment :: Other Environment',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: OS Independent',
        'Operating System :: Other OS',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: BSD',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX :: Other',
        'Operating System :: POSIX :: SunOS/Solaris',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Communications',
        'Topic :: Internet',
        'Topic :: Internet :: Log Analysis',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Networking',
        'Topic :: System :: Networking :: Monitoring'
    ]
)
