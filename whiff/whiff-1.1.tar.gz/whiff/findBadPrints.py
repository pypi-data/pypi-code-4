"""
Look for files that have non-verbose prints in them.
Stop looking at the first line which has a print which also mentions test
"""

import os
def scan():
    files = os.listdir(".")
    for fn in files:
        if not fn.endswith(".py"):
            continue
        lines = open(fn).readlines()
        for line in lines:
            lowerline = line.lower()
            if lowerline.find("print")>=0:
                if lowerline.find("test")>=0: # verbose
                    break
                if lowerline.find("verbose")>=0:
                    continue
                print repr(fn), repr(line) # verbose

if __name__=="__main__":
    scan()
