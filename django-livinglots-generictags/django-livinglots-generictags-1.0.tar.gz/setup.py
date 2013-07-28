from setuptools import setup, find_packages
import os

import livinglots_generictags


CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
]

setup(
    author="Eric Brelsford",
    author_email="eric@596acres.org",
    name='django-livinglots-generictags',
    version=livinglots_generictags.__version__,
    description=('A set of helpers for creating Django template tags for '
                 'models with generic relations.'),
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    url='https://github.com/596acres/django-livinglots-generictags/',
    license='GNU Lesser General Public License v3 (LGPLv3)',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=[
        'Django>=1.3.1',
        'django-classy-tags==0.4',
    ],
    packages=find_packages(),
    include_package_data=True,
)
