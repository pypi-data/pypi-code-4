from setuptools import setup, find_packages

setup(
    name='django-ci',
    version='0.0.4',
    author='John Leith',
    author_email='leith.john@gmail.com',
    packages=find_packages(),
    url='http://pypi.python.org/pypi/django-ci/',
    download_url='https://bitbucket.org/freakypie/django-ci',
    description='Django continuous integration and testing',
    long_description=open('README.rst').read(),
    install_requires=[
        "Django==1.4.5",
        "django-viewgroups>=0.0.4",
    	"socketio_server>=0.0.5",
    	"kombu",
    	"django-celery"
    ],
    package_data = {
        '': ['*.txt', '*.rst', '*.md', '*.html'],
    },
)
