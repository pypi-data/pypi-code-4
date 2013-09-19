from setuptools import setup, find_packages


setup(
    name='logbag',
    version='0.0.8',
    description='Cloud logging.',
    long_description=open('README.rst').read(),
    author='Mikko Hellsing',
    author_email='mikko@aino.se',
    license='BSD',
    url='https://github.com/aino/logbagpy',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=['supervisor>=3.0'],
    test_suite='tests.test',
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: System :: Logging',
    ],
)
