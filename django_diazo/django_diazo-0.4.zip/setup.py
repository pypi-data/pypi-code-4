from setuptools import setup, find_packages

VERSION = '0.4'

REQUIREMENTS = (
    'setuptools>=0.6c11',
    'django>=1.4.2',
    'south>=0.8.2',
    'diazo>=1.0',
    'webob==1.2.3',
    'repoze.xmliter>=0.3',
    'django-codemirror-widget>=0.3.0',
    'django-polymorphic>=0.5.1',
)
TEST_REQUIREMENTS = (
)


setup(
    name="django_diazo",
    version=VERSION,
    author="Douwe van der Meij, Job Ganzevoort",
    description="""Integrate Diazo in Django using WSGI middleware and
    add/change themes using the Django Admin interface.
    """,
    longdescription=open('README.md', 'rt').read(),
    url="https://github.com/Goldmund-Wyldebeast-Wunderliebe/django-diazo",
    packages=find_packages(),
    include_package_data=True,
    install_requires=REQUIREMENTS,
    tests_require=TEST_REQUIREMENTS,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
