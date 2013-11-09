"""
flask-bundle-system
-------------------



Links
`````

* `documentation <http://packages.python.org/flask-bundle-system>`_
* `development version
  <http://github.com/yograterol/flask-bundle-system/zipball/master>`_

"""
from setuptools import setup


setup(
    name='flask-bundle-system',
    version='0.1',
    url='https://github.com/yograterol/flask-bundle-system',
    license='BSD',
    author='yograterol',
    author_email='yograterol@fedoraproject.org',
    description='Flask extension for work with blueprints as bundles',
    long_description=__doc__,
    packages=['flask_bundlesystem'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
