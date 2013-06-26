#!/usr/bin/env python
"""PPlus Slipguru installation script.

This script is used by our reseach group to quickly add new machine
in the our PPlus environment.

The script was tested on different *ubuntu workstation ad is release
without any warranty as an example of PPlus configuration.

"""

# Author: Salvatore Masecchia <salvatore.masecchia@disi.unige.it>,
#         Grzegorz Zycinski <grzegorz.zycinski@disi.unige.it>
# License: BSD Style.

import os
import socket
import optparse
import subprocess
import shlex
import ConfigParser

try:
    from pplus import __version__ as version
    from pplus.jobutils import detect_ncpus
except ImportError:
    print 'error: pplus not installed!'
    exit()

# Utility ---------------------------------------------------------------------
def check_nfs(addr):
    if not ':' in addr:
        raise optparse.BadOptionError(
            '%s is not a valid NFS mount point' % addr)
    return addr.split(':')


def cmd(command, silent=False):
    if silent:
        with open('/dev/null', 'w') as null_out:
            subprocess.check_call(shlex.split(command), stdout=null_out,
                                  stderr=null_out)
    else:
        subprocess.check_call(shlex.split(command))


def pipe_out(cmd1, cmd2):
    p1 = subprocess.Popen(shlex.split(cmd1), stdout=subprocess.PIPE)
    p2 = subprocess.Popen(shlex.split(cmd2), stdin=p1.stdout,
                          stdout=subprocess.PIPE)
    p1.stdout.close()
    return p2.communicate()[0]


# Operations ------------------------------------------------------------------
def nfs_configuration(args):
    print '* NFS configuration... '
    print '\t* Given NFS remote mount point: %s' % ':'.join(args.nfs_mount)

    # dpkg -l | grep nfs-common
    if not pipe_out('dpkg -l', 'grep nfs-common'):
        print '\t* NFS driver not found, installing...'

        try:
            # apt-get install nfs-common
            cmd('apt-get install nfs-common')
            print '\t* NFS driver installation done!'
        except subprocess.CalledProcessError:
            print '\t* NFS driver installation aborted!'
    else:
        print '\t* NFS driver already installed'


def user_configuration(args):
    print '* User configuration... '
    print '\t* Given user name: %s' % args.user

    exp_path = '~%s' % args.user
    user_home = os.path.expanduser(exp_path)
    if exp_path == user_home:
        print '\t* User %s not found...' % args.user
        cmd('useradd -m -U -c "pplus user" -s /bin/bash %s' % args.user)
        cmd('passwd -l %s' % args.user)

        user_home = os.path.expanduser(exp_path)
        print '\t* User %s created (home is %s)' % (args.user, user_home)
    else:
        print '\t* User %s found (home is %s)' % (args.user, user_home)


def pplus_directories(args):
    print '* PPlus directories creation... '

    user_home = os.path.expanduser('~%s' % args.user)
    disk_path = os.path.join(user_home, 'disk')
    if os.path.exists(os.path.join(user_home, 'disk')):
        print ('\t* Shared disk directory already exists (%s)! '
               '\t **Please check if it is empty and if NFS-mountable**' % disk_path)
    else:
        cmd('su %s -c "mkdir %s"' % (args.user, disk_path))
        print '\t* Shared disk directory created (%s)' % disk_path

    cache_path = os.path.join(user_home, 'cache')
    if os.path.exists(os.path.join(user_home, 'cache')):
        print ('\t* Local cache directory already exists (%s)!'
               '\t **Please check if it is accesible by PPlus users**'% cache_path)
    else:
        cmd('su %s -c "mkdir -m 777 %s"' % (args.user, cache_path))
        print '\t* Local cache directory created (%s)' % cache_path


def config_update(args):
    print '* Global configuration file update... '

    config_path = os.path.normpath('/etc/pplus/pplus.cfg')
    if not os.path.exists(config_path):
        print ('\t* Configuration file does not exists (%s)!'
               '\t **Please create and configure manually a configuration file**' % config_path)
    else:
        cp = ConfigParser.SafeConfigParser()
        cp.read(config_path)

        user_home = os.path.expanduser('~%s' % args.user)
        cp.set('io', 'disk_path', os.path.join(user_home, 'disk'))
        cp.set('io', 'cache_path', os.path.join(user_home, 'cache'))

        with open(config_path, 'wb') as out_config:
            cp.write(out_config)

        print '\t* Configuration file updated (%s)' % config_path


def pplus_services(args):
    print '* PPlus services installation... '
    print '\t* Given number of workers to manage: %d' % args.workers

    defult_service = open('pplus_services', 'r').read()
    cmd('touch /etc/init.d/pplus_services')

    user_home = os.path.expanduser('~%s' % args.user)
    disk_path = os.path.join(user_home, 'disk')

    with open('/etc/init.d/pplus_services', 'w') as out_service:
        out_service.write(defult_service % {'DISK_NODE_IP': args.nfs_mount[0],
                                            'DISK_NODE_PATH': args.nfs_mount[1],
                                            'DISK_PATH': disk_path,
                                            'USER': args.user,
                                            'WORKERS': args.workers})
    cmd('chmod +x /etc/init.d/pplus_services')
    cmd('update-rc.d pplus_services defaults 90 10', silent=True)
    cmd('/etc/init.d/pplus_services start', silent=True)

    print ('\t* Services installed and started. '
           '\t\t\t\t **Please check with /etc/init.d/pplus_services status')


# Main script -----------------------------------------------------------------
if __name__ == '__main__':

    usage = """Usage: pplusserver.py [options] nfs_mount.

    NFS mount point must be in remote_host:remote_dir format.
    If not found, NFS driver will be automatically installed.
    """
    parser = optparse.OptionParser(usage=usage, version='%prog ' + version)
    parser.add_option('-u', '--user', dest='user', action='store',
                      default='pplus',
                      help='workers owner user (*default pplus*). '
                           'If the specified user does not exist, '
                           'it will be created (login disabled)')
    parser.add_option('-w', '--workers', dest='workers', action='store',
                      type='choice', default=str(detect_ncpus()),
                      choices=[str(x) for x in xrange(1, detect_ncpus()+1)],
                      help='number of workers to manage, default %d' % (detect_ncpus()))

    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")
    options.nfs_mount = check_nfs(args[0])
    options.workers = int(options.workers)
    print

    # -------------------------------------------------------------------------
    commands = [ # Comment item to disable an operation
        nfs_configuration,
        user_configuration,
        pplus_directories,
        config_update,
        pplus_services
    ]

    # Execution ---------------------------------------------------------------
    for command in commands:
        command(options)

    # TODO: add rollback operations


# We do not provide any uninstallation script, in order to rollback some
# of the operation done by this script you can use this commands

# sudo /etc/init.d/pplus_services stop
# sudo rm -f /etc/init.d/pplus_services
# sudo update-rc.d -f pplus_services remove
# sudo apt-get remove --purge nfs-common
# sudo apt-get autoremove --purge
# sudo userdel -f -r pplus
# sudo rm -rf /etc/pplus
