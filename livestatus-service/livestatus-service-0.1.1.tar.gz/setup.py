#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'livestatus-service',
          version = '0.1.1',
          description = 'Exposes MK livestatus to the outside world over HTTP',
          long_description = '''Exposes MK livestatus to the outside world over HTTP''',
          author = "Marcel Wolf, Maximilien Riehl",
          author_email = "marcel.wolf@immobilienscout24.de, maximilien.riehl@gmail.com",
          license = 'WTFPL',
          url = 'https://github.com/mriehl/livestatus-service',
          scripts = [],
          packages = ['livestatus_service'],
          classifiers = ['Development Status :: 4 - Beta', 'Environment :: Web Environment', 'Intended Audience :: Developers', 'Intended Audience :: System Administrators', 'Programming Language :: Python', 'Natural Language :: English', 'Operating System :: POSIX :: Linux', 'Topic :: System :: Monitoring'],
          data_files = [('/var/www', ['livestatus_service/livestatus_service.wsgi']), ('/etc/httpd/conf.d/', ['livestatus_service/livestatus_service.conf'])],
          package_data = {'livestatus_service': ['templates/*.html']},
          install_requires = [ "flask" ],
          
          zip_safe=True
    )
