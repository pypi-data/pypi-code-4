from distutils.core import setup

setup(
    name='Pingokio',
    version='0.0.2',
    author='Yevgeniy Shchemelev',
    author_email='shchemelevev@gmail.com',
    packages=['pingokio'],
    url='https://github.com/shchemelevev/pingokio',
    license='LICENSE.txt',
    description='You site uptime statistic collector',
    long_description=open('README.md').read(),
    install_requires=[
        "Django >= 1.5.1",
        "celery >= 3.0.19",
        "django-celery >= 3.0.17",
        "django-kombu >= 0.9.4"
    ],
)
