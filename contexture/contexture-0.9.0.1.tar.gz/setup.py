import os
from setuptools import setup, find_packages


def find_package_data(package, files=()):
    package_data = {}
    for dirpath, _, filenames in os.walk(package):
        for f in files:
            if f in filenames:
                package_path = dirpath.replace('/', '.')
                package_data.setdefault(package_path, []).append(f)
    return package_data


def local_file(fn):
    return open(os.path.join(os.path.dirname(__file__), fn))


with local_file('requirements.txt') as f:
    requirements = map(str.strip, f)


setup(name='contexture',
      description='Magic Automatic Logging Context',
      # version=os.environ.get('GIT_BRANCH'),
      version='0.9.0.1',
      author='Alex Kouznetsov',
      author_email='alex@eat-up.org',
      packages=find_packages(),
      license='Apache 2',
      url='https://github.com/unthingable/contexture',
      include_package_data=True,
      install_requires=requirements,
      package_data=find_package_data('contexture',
                                     files=('config.conf',)),
      entry_points="""
        [console_scripts]
        lcmon=contexture.monitor:monitor_cmd
        lcdump=contexture.utils.db:main
    """
)
