# -*- coding: utf-8 -*-
#!/usr/bin/env python
from distutils.core import setup

setup(
    name='Caliope_Iliada',
    version='0.1dev',
    package_dir={'': 'src'},
    packages=['iliada'],
    license='GNU AFFERO GENERAL PUBLIC LICENSE',
    long_description=open('README.md').read(),
    author='Andrés F. Calderón',
    author_email='andres.calderon@correlibre.org',
    url='https://proyectos.correlibre.org/caliope/caliope_storage_la_iliada',
    install_requires=['psycopg2']
)
