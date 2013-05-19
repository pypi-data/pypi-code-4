from distutils.core import setup
import os
SETUP_PATH = os.path.abspath(os.path.dirname(__file__))


def is_package(path):
    return (os.path.isdir(path) and os.path.isfile(os.path.join(path, '__init__.py')))


def find_packages(path, base=""):
    """ Find all packages in path """
    packages = {}
    for item in os.listdir(path):
        dir = os.path.join(path, item)
        if is_package(dir):
            if base:
                module_name = "%(base)s.%(item)s" % vars()
            else:
                module_name = item
            packages[module_name] = dir
            packages.update(find_packages(dir, module_name))
    return packages


setup(
    name='Pingokio',
    version='0.0.8',
    author='Yevgeniy Shchemelev',
    author_email='shchemelevev@gmail.com',
    package_dir={'': 'src'},
    packages=find_packages("src"),
    url='https://github.com/shchemelevev/pingokio',
    license='MIT',
    description='You site uptime statistic collector',
    long_description=open(os.path.join(SETUP_PATH, 'README.md')).read(),
    install_requires=[
        "Django >= 1.5.1",
        "celery >= 3.0.19",
        "django-celery >= 3.0.17",
        "django-kombu >= 0.9.4",
        "logan >= 0.5.6"
        "gunicorn >= 0.17.4",
    ],
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
    ],
    entry_points={
        'console_scripts': [
            'pingokio = pingokio.server.logan_runner:main',
        ],
    },
)
