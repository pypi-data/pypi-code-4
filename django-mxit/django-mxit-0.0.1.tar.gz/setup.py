from setuptools import setup


def listify(filename):
    return filter(None, open(filename, 'r').read().split('\n'))


setup(
    name="django-mxit",
    version="0.0.1",
    url='http://github.com/praekelt/django-mxit',
    license='BSD',
    description="Simple helpers for writing Mxit apps with Django",
    long_description=open('README.rst', 'r').read(),
    author='Praekelt Foundation',
    author_email='dev@praekeltfoundation.org',
    packages=['mxit'],
    include_package_data=True,
    install_requires=listify('requirements.pip'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
        'Framework :: Django',
    ],
)
