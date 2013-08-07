from setuptools import setup, find_packages


setup(
    name='django-weblog',
    version='0.2.0',
    author='Stefan Scherfke',
    author_email='stefan at sofa-rockers.org',
    description='A Django weblog app with hierarchic categories.',
    long_description=(open('README.txt').read() + '\n\n' +
                      open('CHANGES.txt').read() + '\n\n' +
                      open('AUTHORS.txt').read()),
    url='https://bitbucket.org/ssc/django-weblog',
    license='MIT',
    install_requires=[
        'Django>=1.4',
        'django-haystack>=2.1',
    ],
    packages=find_packages(exclude=['*.tests', '*.tests.*', 'tests.*']),
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)
