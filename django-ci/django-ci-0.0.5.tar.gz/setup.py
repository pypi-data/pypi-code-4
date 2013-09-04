from setuptools import setup, find_packages  # @UnresolvedImport
import os

desc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name='django-ci',
    version='0.0.5',
    author='John Leith',
    author_email='leith.john@gmail.com',
    packages=find_packages(),
    url='http://pypi.python.org/pypi/django-ci/',
    download_url='https://bitbucket.org/freakypie/django-ci',
    description='Django continuous integration and testing',
    long_description=desc,
    install_requires=[
        "Django>=1.4.5,<1.5",
        "django-viewgroups>=0.0.8",
        "socketio_server>=0.0.7",
        "kombu",
        "django-celery",
        "GitPython",
        "SocketIO_client",
        "django_test_exclude",
    ],
    include_package_data=True,
)
