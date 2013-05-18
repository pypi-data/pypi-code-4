# Copyright 2013 Daniel Narvaez
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess
import time

from osbuild import config


def run(args, test=False, interactive=False, retry=0):
    if test:
        print(" ".join(args))
        return

    log_file = None
    subprocess_args = {"args": args}

    if config.log_path and not interactive:
        log_file = open(config.log_path, "a")
        subprocess_args["stdout"] = log_file
        subprocess_args["stderr"] = subprocess.STDOUT

    tries = 0
    while tries < retry + 1:
        try:
            tries = tries + 1
            subprocess.check_call(**subprocess_args)
            break
        except subprocess.CalledProcessError as e:
            print("\nCommand failed, tail of %s\n" % config.log_path)
            if config.log_path:
                subprocess.call(["tail", config.log_path])

            if tries < retry + 1:
                print("Retrying (attempt %d) in 1 minute" % tries)
                time.sleep(60)
            else:
                raise e

    if log_file:
        log_file.close()


def run_with_sudo(args, test=False, interactive=False, retry=0):
    args_with_sudo = ["sudo"]
    args_with_sudo.extend(args)

    print(" ".join(args_with_sudo))

    run(args_with_sudo, test=test, retry=retry, interactive=interactive)
