import xmlrpclib
from celery.task import task
from django.db import IntegrityError
from pypi.models import Package, Version, Release


@task()
def update_releases(pk):
    client = xmlrpclib.ServerProxy('http://pypi.python.org/pypi',
                                   use_datetime=True)
    version = Version.objects.get(pk=pk)
    for release in client.release_urls(version.package.name, version.version):
        try:
            Release.objects.create(**dict(release, version=version))
        except IntegrityError:
            pass


@task()
def update_versions(pk):
    client = xmlrpclib.ServerProxy('http://pypi.python.org/pypi',
                                   use_datetime=True)
    package = Package.objects.get(pk=pk)
    for pypi_version in client.package_releases(package.name, True):
        version, created = Version.objects.get_or_create(package=package,
                                                         version=pypi_version)

        update_releases.apply_async((version.pk,))


@task()
def update_packages():
    client = xmlrpclib.ServerProxy('http://pypi.python.org/pypi',
                                   use_datetime=True)
    for package_name in client.list_packages():
        package, created = Package.objects.get_or_create(name=package_name)
        update_versions.apply_async((package.pk,))