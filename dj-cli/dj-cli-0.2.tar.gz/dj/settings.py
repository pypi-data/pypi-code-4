import re


def add_packages(settings_file, packages):
    data = file(settings_file).read()

    installed_packages = []

    package_data = re.findall('INSTALLED_APPS = \(([^\(\)]+)\)', data)
    if len(package_data):
        installed_packages = re.findall("'([a-zA-Z0-9\.]+)'", package_data[0])

    packages = set(packages) - set(installed_packages)
    packages = ''.join(["    '%s',\n" % x for x in packages])

    data = re.sub('INSTALLED_APPS = \(([^\(\)]+)\)',
                  'INSTALLED_APPS = (\\1' + packages + ')', data, re.MULTILINE)

    file(settings_file, 'w').write(data)
