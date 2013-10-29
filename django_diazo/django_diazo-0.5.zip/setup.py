from setuptools import setup, find_packages

VERSION = '0.5'

REQUIREMENTS = (
    'setuptools>=0.6c11',
    'django>=1.4.2',
    'south>=0.8.2',
    'diazo>=1.0',
    'webob==1.2.3',
    'repoze.xmliter>=0.3',
)
TEST_REQUIREMENTS = (
)


setup(
    name="django_diazo",
    version=VERSION,
    author="Douwe van der Meij, Job Ganzevoort",
    author_email="vandermeij@gw20e.com",
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
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
