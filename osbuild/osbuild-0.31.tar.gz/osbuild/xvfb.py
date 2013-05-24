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

import os
import subprocess

from osbuild import utils


def start():
    xvfb_display = _find_free_display()
    xvfb_proc = subprocess.Popen(args=["Xvfb", xvfb_display],
                                 stdout=utils.devnull,
                                 stderr=subprocess.STDOUT)
    orig_display = os.environ.get("DISPLAY", None)
    os.environ["DISPLAY"] = xvfb_display

    return (xvfb_proc, orig_display)


def stop(xvfb_proc, orig_display):
    if orig_display is not None:
        os.environ["DISPLAY"] = orig_display

    xvfb_proc.terminate()


def _find_free_display():
    for i in range(100, 1000):
        display = ":%s" % i
        result = subprocess.call(args=["xdpyinfo", "--display", display],
                                 stdout=utils.devnull,
                                 stderr=subprocess.STDOUT)
        if result > 0:
            return display
