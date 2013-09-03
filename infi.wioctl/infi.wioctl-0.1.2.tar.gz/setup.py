
SETUP_INFO = dict(
    name = 'infi.wioctl',
    version = '0.1.2',
    author = 'Arnon Yaari',
    author_email = 'arnony@infinidat.com',

    url = 'http://www.infinidat.com',
    license = 'PSF',
    description = """Windows ioctl wrapper""",
    long_description = """wrapper for sending DevieIoControl commands to Windows devices""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['distribute', 'infi.instruct', 'infi.cwrap', 'infi.exceptools'],
    namespace_packages = ['infi'],

    # packages = find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = [],
        gui_scripts = []),
    )

platform_install_requires = {
    'windows' : [],
    'linux' : [],
    'macosx' : [],
}

def _get_os_name():
    import platform
    system = platform.system().lower().replace('-', '').replace('_', '')
    if system == 'darwin':
        return 'macosx'
    return system


def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    SETUP_INFO['install_requires'] += platform_install_requires[_get_os_name()]
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

