from distutils.core import setup
import os
SETUP_PATH = os.path.abspath(os.path.dirname(__file__))

setup(
    name='Pingokio',
    version='0.0.3',
    author='Yevgeniy Shchemelev',
    author_email='shchemelevev@gmail.com',
    packages=['pingokio'],
    url='https://github.com/shchemelevev/pingokio',
    license='LICENSE.txt',
    description='You site uptime statistic collector',
    long_description=open(os.path.join(SETUP_PATH, 'README.md')).read(),
    install_requires=[
        "Django >= 1.5.1",
        "celery >= 3.0.19",
        "django-celery >= 3.0.17",
        "django-kombu >= 0.9.4"
    ],
)
