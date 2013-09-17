#coding:utf-8
import argparse
import logging
import ConfigParser
import os
import pwd
import stat

import daemon
import procname
import lockfile.pidlockfile

from replmon import Replmon


logger = logging.getLogger()
logger.setLevel(logging.INFO)


DEFAULT_CNF_FILE = "/etc/replmon.ini"
DEFAULT_LOG_FILE = "/var/log/replmon.log"

DEFAULT_PID_FILE = "/var/run/replmon/replmon.pid"
DEFAULT_STATUS_FILE = "/var/run/replmon/replmon.status"

DEFAULT_CHECK_INTERVAL = 10


def ensure_writable(dir, uid, gid):
    try:
        os.mkdir(dir)
    except OSError:
        pass
    os.chown(dir, uid, gid)
    os.chmod(dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)



def main():
    parser = argparse.ArgumentParser(description="Monitor your MySQL replication status")
    parser.add_argument("--config", help="Path to the replmon config file (default: {0})".format(DEFAULT_CNF_FILE),
                        default=DEFAULT_CNF_FILE)
    args = parser.parse_args()

    parser = ConfigParser.ConfigParser()
    parser.read(args.config)

    mysql_args = dict(parser.items("mysql"))
    mon = Replmon(mysql_args, DEFAULT_STATUS_FILE, DEFAULT_CHECK_INTERVAL)

    try:
        user = parser.get("system", "user")
    except  (ConfigParser.NoSectionError, ConfigParser.NoSectionError):
        uid, gid = os.getuid(), os.getgid()
    else:
        user_entry = pwd.getpwnam(user)
        uid, gid = user_entry.pw_uid, user_entry.pw_gid

    # Ensure we can touch the status file
    for dir in map(os.path.dirname, [DEFAULT_PID_FILE, DEFAULT_STATUS_FILE]):
        ensure_writable(dir, uid, gid)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler(DEFAULT_LOG_FILE)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


    with daemon.DaemonContext(pidfile=lockfile.pidlockfile.PIDLockFile(DEFAULT_PID_FILE),
                              files_preserve=[file_handler.stream], uid=uid, gid=gid):
        procname.setprocname("replmon")
        # noinspection PyBroadException
        try:
            mon.run()
        except Exception:
            logger.exception("An error occurred")


if __name__ == "__main__":
    main()