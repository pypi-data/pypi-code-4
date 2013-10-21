#!/usr/bin/env python
# Copyright 2013 Donald Stufft
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import absolute_import, division, print_function

import argparse
import ConfigParser
import smtplib
import subprocess
import sys

from email.mime.text import MIMEText


def main():
    parser = argparse.ArgumentParser(prog="zdup")
    parser.add_argument("-c", "--config", default="/etc/zdup.cfg")
    parser.add_argument("command")

    args = parser.parse_args()

    config = ConfigParser.ConfigParser()
    config.read(args.config)

    archive_dir = config.get("zdup", "archive-dir")
    key_id = config.get("zdup", "key-id")
    source = config.get("zdup", "source")
    dest = config.get("zdup", "dest")
    email = config.get("zdup", "email")
    from_email = config.get("zdup", "from_email")
    email_server = config.get("zdup", "email_server")
    email_port = config.get("zdup", "email_port")
    email_user = config.get("zdup", "email_user")
    email_password = config.get("zdup", "email_password")

    env = {
        "AWS_ACCESS_KEY_ID": config.get("zdup", "aws_access_key_id"),
        "AWS_SECRET_ACCESS_KEY": config.get("zdup", "aws_secret_access_key"),
        "PASSPHRASE": config.get("zdup", "key-passphrase"),
        "SIGN_PASSPHRASE": config.get("zdup", "key-passphrase"),
    }

    cmd = [
        "duplicity",
        "--archive-dir", archive_dir,
        "--encrypt-sign-key", key_id,
        "--s3-use-new-style",
        "--volsize", "512",
        "--asynchronous-upload",
    ]

    if args.command == "backup":
        cmd += [source, dest]
    elif args.command == "verify":
        cmd += ["verify", dest, source]
    else:
        raise RuntimeError("Invalid Command")

    p = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    p.wait()

    msg = MIMEText("-- stdout --\n%s\n-- stderr --\n%s" % (
        p.stdout.read(),
        p.stderr.read()
    ))

    if p.returncode == 0:
        msg["Subject"] = "Backup Complete"
    else:
        msg["Subject"] = "Backup Failed"

    msg["To"] = email
    msg["From"] = from_email

    s = smtplib.SMTP_SSL(email_server, email_port)
    s.login(email_user, email_password)
    s.sendmail(from_email, [email], msg.as_string())
    s.quit()

    return p.returncode

if __name__ == "__main__":
    sys.exit(main())
