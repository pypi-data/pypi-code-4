#coding:utf-8
import argparse
import logging
import ConfigParser
import os
import pwd

import procname
import daemon
import lockfile.pidlockfile

from replmon import Replmon


logger = logging.getLogger()
logger.setLevel(logging.INFO)


DEFAULT_CNF_FILE = "/etc/replmon.ini"
DEFAULT_LOG_FILE = "/var/log/replmon.log"
DEFAULT_PID_FILE = "/var/run/replmon/replmon.pid"


def main():
    parser = argparse.ArgumentParser(description="Monitor your MySQL replication status")
    parser.add_argument("--config", help="Path to the replmon config file (default: {0})".format(DEFAULT_CNF_FILE),
                        default=DEFAULT_CNF_FILE)
    args = parser.parse_args()

    parser = ConfigParser.ConfigParser()
    parser.read(args.config)

    mysql_args = dict(parser.items("mysql"))
    mon = Replmon(mysql_args)

    try:
        user = parser.get("system", "user")
    except  (ConfigParser.NoSectionError, ConfigParser.NoSectionError):
        uid, gid = os.getuid(), os.getgid()
    else:
        user_entry = pwd.getpwnam(user)
        uid, gid = user_entry.pw_uid, user_entry.pw_gid


    # Ensure we can touch the status file
    mon.touch_status_file()
    os.chown(mon.status_file, uid, gid)

    # Ensure the pidfile folder exists and that we own it
    pid_dir = os.path.dirname(DEFAULT_PID_FILE)
    try:
        os.mkdir(pid_dir)
    except OSError:
        pass
    os.chown(pid_dir, uid, gid)

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