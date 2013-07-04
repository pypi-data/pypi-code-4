#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'livestatus-service',
          version = '0.3.1',
          description = 'Exposes MK livestatus to the outside world over HTTP',
          long_description = '''Livestatus-service is a WSGI application that exposes the functionality of a livestatus socket to the outside world over HTTP. 
Query results are formatted to be more machine readable and it is also possible to send commands over the livestatus socket or using the nagios/icinga command file.''',
          author = "Marcel Wolf, Maximilien Riehl",
          author_email = "marcel.wolf@immobilienscout24.de, maximilien.riehl@gmail.com",
          license = 'MIT',
          url = 'https://github.com/ImmobilienScout24/livestatus_service',
          scripts = [],
          packages = ['livestatus_service'],
          classifiers = ['Development Status :: 4 - Beta', 'Environment :: Web Environment', 'Intended Audience :: Developers', 'Intended Audience :: System Administrators', 'Programming Language :: Python', 'Natural Language :: English', 'Operating System :: POSIX :: Linux', 'Topic :: System :: Monitoring', 'Programming Language :: Python :: 2.6', 'Programming Language :: Python :: 2.7', 'Programming Language :: Python :: 3', 'License :: OSI Approved :: MIT License', 'Programming Language :: Python :: Implementation :: CPython', 'Programming Language :: Python :: Implementation :: Jython', 'Programming Language :: Python :: Implementation :: PyPy'],
          data_files = [('/var/www', ['livestatus_service/livestatus_service.wsgi']), ('/etc/httpd/conf.d/', ['livestatus_service/livestatus_service.conf'])],
          package_data = {'livestatus_service': ['templates/*.html']},
          install_requires = [ "flask" ],
          
          zip_safe=True
    )
