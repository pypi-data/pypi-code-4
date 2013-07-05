from setuptools import setup
import os


def read(filename):
    """Open a file and return its contents."""
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


setup(
    name='pyramid_settings',
    version='0.1.2',
    description="Pyramid settings module that lets you use settings.py",
    long_description=read('README.md'),
    url='http://github.com/niktto/pyramid_settings/',
    license=read('LICENSE'),
    author=u'Marek Szwalkiewicz',
    author_email='marek@szwalkiewicz.waw.pl',
    packages=['pyramid_settings'],
    keywords='web pyramid pylons',
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
)
