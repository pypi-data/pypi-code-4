from setuptools import setup, find_packages
from rdcelery_email import __version__


setup(
    name='rd-celery-email',
    version=__version__,
    description="rd-celery-email",
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "Environment :: Web Environment",
    ],
    keywords='django,celery,email',
    author='andychiang',
    author_email='rdandy@gmail.com',
    url='https://bitbucket.org/andychiang/dj-celery-email',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
