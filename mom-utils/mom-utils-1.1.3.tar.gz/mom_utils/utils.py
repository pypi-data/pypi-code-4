import time
import sys
import math
import os
import re


def spin(times, interval=1):
    SPIN = '|\\-/'
    i = 0
    while i <= times:
        sys.stdout.write("\r%s" % SPIN[i % len(SPIN)])
        sys.stdout.flush()
        time.sleep(interval)
        i += 1


def layout(n, factor=1):

    def divisors(num):
        result = []
        step = 1
        while step <= math.ceil(num / 2):
            if num % step == 0:
                result.append(step)
            step += 1
        result.append(num)
        return result

    possibilities = [(n / d, d) for d in divisors(n) if n / d >= d]
    possibilities.sort(key=lambda x: abs(float(n / x[1] ** 2) - factor))
    return possibilities[0]


def get_output_files(cfg):
    """

        Example
        cfg = {'data_path': '/Tupa/simulations/exp048/dataout',
               'filename_pattern': 'cgcm2.2_currents_.*\.nc'}
    """
    # Create files list
    filenames = [f for f in os.listdir(cfg['data_path']) if re.match(cfg['filename_pattern'],f)]
    filenames.sort()
    # Include the path to the files
    ncfpaths = [os.path.join(cfg['data_path'],f) for f in filenames]
    return ncfpaths
