from distutils.core import setup
setup(
    name          = 'phpydaemon',
    packages      = ['phpydaemon'],
    version       = '0.1',
    description   = 'Webservice for calling long-running PHP functions as subprocesses',
    author        = 'Stian Strandem',
    author_email  = 'stian@strandem.no',
    url           = 'https://github.com/stianstr/phpydaemon',
    download_url  = 'https://github.com/stianstr/phpydaemon/tarball/0.1',
    keywords      = ['php', 'daemon', 'subprocess'],
    classifiers   = [
        'Intended Audience :: Developers',
        'Operating System :: POSIX'
    ],
    license       = 'MIT',
    requires      = ['daemon (>=1.6)', 'bottle (>=0.10.6)'],
    scripts       = ['scripts/phpydaemon'],
    package_data  = {'phpydaemon': ['templates/*']},
    data_files    = [
        ('/etc',                      ['etc/phpydaemon.json-dist']),
        ('/etc/init.d',               ['etc/init.d/phpydaemon']),
        ('/usr/share/php/phpydaemon', [
            'php/Callback.php',
            'php/Client.php',
            'php/PhpyDaemonException.php',
            'php/callback-example.php'
        ])
    ]
)

