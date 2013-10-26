from fabric.api import task
# from fabric import operations
# import fabric.api
# fabric.api.sudo = fabric.api.run

# from fabric.api import *

# from fabtools.vagrant import vagrant
from fabtools.vagrant import vagrant
# import fabtools
# from fabtools import require


# env.hosts = [
#     'root@127.0.0.1:2200'
# ]
# env.key_filename = '/Users/ronan/.vagrant.d/insecure_private_key'
# env.disable_known_hosts = True

# @task
# def python_from_source():
#     """
#     Check Python installation
#     """
#     fabtools.deb.update_index()
#     require.python.from_source(version='2.7.3', prefix='/usr/local')
#     assert fabtools.files.is_file('/usr/local/bin/python')
#     version = fabtools.python.version(prefix='/usr/local')
#     assert version == '2.7.3', version


# @task
# def toto():
#     # require.postgres.server()
#     # assert not fabtools.postgres.user_exists('alice')
#     # fabtools.postgres.create_user('alice', password='secret')
#     # assert fabtools.postgres.user_exists('alice')

#     require.postgres.server()

#     # Test low-level operations
#     assert not fabtools.postgres.user_exists('alice')
#     assert not fabtools.postgres.user_exists('bob')
#     fabtools.postgres.create_user('alice', password='1234')
#     assert fabtools.postgres.user_exists('alice')
#     assert not fabtools.postgres.user_exists('bob')
#     fabtools.postgres.create_user('bob', password='5678')
#     assert fabtools.postgres.user_exists('alice')
#     assert fabtools.postgres.user_exists('bob')

#     # Test high-level operations
#     require.postgres.user('pguser', 'foo')
#     assert fabtools.postgres.user_exists('pguser')

#     require.postgres.database('pgdb', 'pguser')
#     assert fabtools.postgres.database_exists('pgdb')


# @task
# def tutu():
#     print fabtools.user.exists('bob')
#     run('whoami')
#     sudo('whoami')


# @task
# def lolo():
#     # print fabtools.system.supported_locales()
#     require.system.locale('en_US.UTF-8')
#     require.system.locale('fr_FR.UTF-8')


# @task
# def postgresql():
#     """
#     Install the latest stable PostgreSQL version on Debian/Ubuntu
#     from the PostgreSQL Global Development Group APT repository

#     See: https://wiki.postgresql.org/wiki/Apt
#     """

#     import fabtools
#     from fabtools import require

#     # Get the distrib codename
#     #
#     # Note that with fabtools >= 0.14.0 this will be:
#     #
#     #   distrib = fabtools.system.distrib_codename()
#     #
#     distrib = fabtools.deb.distrib_codename()

#     # Add the PGDG key
#     require.file(url='http://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc')
#     fabtools.deb.add_apt_key('ACCC4CF8.asc', update=False)

#     # Add the PGDG repository
#     require.deb.source(
#         'PGDG',
#         'http://apt.postgresql.org/pub/repos/apt/',
#         '%s-pgdg' % distrib,
#         'main'
#     )

#     # Install PostgreSQL
#     require.postgres.server()

#     # fabtools.service.restart('postgresql')

#     # # Test low-level operations
#     # assert not fabtools.postgres.user_exists('alice')
#     # assert not fabtools.postgres.user_exists('bob')
#     # fabtools.postgres.create_user('alice', password='1234')
#     # assert fabtools.postgres.user_exists('alice')
#     # assert not fabtools.postgres.user_exists('bob')
#     # fabtools.postgres.create_user('bob', password='5678')
#     # assert fabtools.postgres.user_exists('alice')
#     # assert fabtools.postgres.user_exists('bob')

#     # Test high-level operations
#     require.postgres.user('pguser', 'foo')
#     assert fabtools.postgres.user_exists('pguser')

#     require.postgres.database('pgdb', 'pguser')
#     assert fabtools.postgres.database_exists('pgdb')

#     #run('cp /etc/locale.gen /tmp/loc1')
#     #run('md5sum /etc/locale.gen')

#     #require.postgres.database('pgdb4', 'pguser', locale='es_EC.UTF-8')
#     #assert fabtools.postgres.database_exists('pgdb4')

#     #run('md5sum /etc/locale.gen')
#     #run('diff -u /tmp/loc1 /etc/locale.gen || true')


# @task
# def locales():
#     # from fabric.api import sudo
#     import fabtools

#     # sudo('mv /usr/share/i18n/SUPPORTED /usr/share/i18n/SUPPORTED.bak')
#     # fabtools.require.file('/usr/share/i18n/SUPPORTED', contents='', use_sudo=True)

#     print(repr(fabtools.system.supported_locales()))

#     # sudo('rm /usr/share/i18n/SUPPORTED')
#     # sudo('mv /usr/share/i18n/SUPPORTED.bak /usr/share/i18n/SUPPORTED')


@task
def test_append():

    from fabric.api import run
    from fabric.contrib.files import append

    filename = '/tmp/testfile'

    TEST_LINES = [
        r'foo',
        r'foo\bar',
        # r'foo\\bar',
        r'foo/bar',
        r'foo//bar',
        r'foo"bar',
        r"foo'bar",
        r"foo.bar",
        r"foo_bar",
        r'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAgQCysMENTuVeMJ2jTP8UnkgxAWRWKhWWnSVXLw3frkDLuKcB6q2GN21jcnQfdGbeivPLlYvJ7UYyBq4zz6B8H6tFv/burtAk2IuMZytgXCLWXIUStjE851/nH9Y/BX9XzE8dgy1ZZZujzUwcgnXG75HlurDHy5NV0jBOY6yQ/UifzQ== test@fabtools',
    ]

    for line in TEST_LINES:
        run('rm -f %s' % filename)
        run('touch %s' % filename)

        # File should be empty
        assert run('cat %s' % filename).splitlines() == []

        # File should have one line
        append(filename, line)
        assert run('cat %s' % filename).splitlines() == [line], line

        # File should still have one line
        append(filename, line)
        assert run('cat %s' % filename).splitlines() == [line], line


import os
from fabric.api import sudo

@task
def require_ssh_public_keys():
    """
    Check addition of SSH public key
    """

    from fabtools.user import authorized_keys
    from fabtools import require

    tests_dir = os.path.dirname(__file__)
    public_key_file = os.path.join(tests_dir, 'id_test.pub')

    with open(public_key_file) as f:
        public_key = f.read().strip()

    require.user('req4', home='/tmp/req4', ssh_public_keys=public_key_file)

    assert authorized_keys('req4') == [public_key]

    # let's try add same keys second time
    require.user('req4', home='/tmp/req4', ssh_public_keys=public_key_file)

    assert authorized_keys('req4') == [public_key]

# @task
# def require_ssh_public_keys():
#     """
#     Check addition of SSH public key
#     """

#     import os
#     from fabric.api import sudo
#     # from fabric.contrib.files import contains
#     from fabtools import require

#     tests_dir = os.path.dirname(__file__)
#     public_key_file = os.path.join(tests_dir, 'id_test.pub')

#     with open(public_key_file) as f:
#         public_key = f.read().strip()

#     sudo('rm -rf /tmp/req4/.ssh')

#     require.user('req4', home='/tmp/req4', ssh_public_keys=public_key_file)

#     # assert not contains('/tmp/req4/.ssh/authorized_keys', public_key)

#     # with hide('running', 'stdout'):
#     res = sudo('cat /tmp/req4/.ssh/authorized_keys')
#     # assert contains('/tmp/req4/.ssh/authorized_keys', public_key)
#     assert res.splitlines() == [public_key], (res.splitlines(), public_key)

#     # let's try add same keys second time
#     require.user('req4', home='/tmp/req4', ssh_public_keys=public_key_file)

#     # with hide('running', 'stdout'):
#     res = sudo('cat /tmp/req4/.ssh/authorized_keys')
#     assert res.splitlines() == [public_key], (res.splitlines(), public_key)
