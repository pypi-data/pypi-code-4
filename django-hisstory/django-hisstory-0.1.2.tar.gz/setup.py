from setuptools import setup, find_packages
setup(
    name = 'django-hisstory',
    version = '0.1.2',
    description = 'Lightweight read-only django model history app.',
    keywords = 'django apps',
    license = 'New BSD License',
    author = 'Andrey Mozgunov',
    author_email = 'andrey.mozgunov@softline.ru',
    url = 'https://bitbucket.org/medsafe/django-hisstory',
    install_requires = [
        'jsonfield',
        'django_globals==0.2.1',
    ],
    dependency_links = [
        'git+https://github.com/ashvetsov/django-globals.git#egg=django_globals-0.2.1',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Plugins',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=[
        'hisstory',
    ],
    include_package_data = True,
)


