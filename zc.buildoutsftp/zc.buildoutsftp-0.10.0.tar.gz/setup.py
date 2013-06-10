from setuptools import setup, find_packages

name='zc.buildoutsftp'
setup(
    name=name,
    version = "0.10.0",
    author = "Jim Fulton",
    author_email = "jim@zope.com",
    description = "Specialized zc.buildout plugin to add sftp support.",
    long_description = open('README.txt').read(),
    license = "ZPL 2.1",
    keywords = "buildout",
    url='http://www.python.org/pypi/'+name,

    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['zc'],
    install_requires = ['paramiko', 'setuptools'],
    extras_require = dict(test=['zope.testing', 'mock']),
    zip_safe=False,
    entry_points = {
        'zc.buildout.extension': ['default = %s:install' % name],
        'zc.buildout.unloadextension': ['default = %s:unload' % name],
        },
    classifiers = [
       'Framework :: Buildout',
       'Development Status :: 3 - Alpha',
       'Intended Audience :: Developers',
       'License :: OSI Approved :: Zope Public License',
       'Topic :: Software Development :: Build Tools',
       'Topic :: Software Development :: Libraries :: Python Modules',
       ],
    )
