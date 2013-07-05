import subprocess
import re

from i3pystatus import IntervalModule

class XRandr(IntervalModule):
    """
    Do Not Publish, private hack of it's own
    """

    interval = 1
    settings = ()
    required = ()

    def run(self):
        text = subprocess.check_output(["xrandr", "--nograb"], universal_newlines=True)

        lvds1 = re.search(r"LVDS1 connected( primary)? 1280x800", text)
        if not lvds1 and "DP2 disconnected" in text:
            print("!!ACTRION!!!")
            subprocess.call(["xrandr", "--output", "LVDS1", "--auto", "--primary"])
            subprocess.call(["xrandr", "--output", "DP2", "--off"])
        elif lvds1 and "DP2 connected" in text:
            print("!!ACTRION!!!")
            subprocess.call(["xrandr", "--output", "LVDS1", "--off"])
            subprocess.call(["xrandr", "--output", "DP2", "--auto", "--primary"])
