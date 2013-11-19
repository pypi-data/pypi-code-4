#!/home/zyxue/.virtualenvs/env1_md/bin/python

import os
import sys
import argparse
import StringIO
import subprocess

def get_cpt_time(infile):
    if not os.path.exists(infile):
        raise IOError("{0} does not exist".format(infile))

    proc = subprocess.Popen(['gmxcheck', '-f', infile],
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()

    if proc.returncode != 0:
        raise IOError("{0}\n{1}\n{2} is corrupted, see the above error\n\n".format(
            stderr, '#' * 79, infile))

    # It's strange that gromacs-4.[05].5 will direct out useful content as
    # stderr
    for line in StringIO.StringIO(stderr):
        if 'Last frame' in line:
            sl = [i.strip() for i in line.split()]
            ret = float(sl[-1]) / 1000 # unit: ns
            return ret

def get_tpr_time(tprfile):
    if not os.path.exists(tprfile):
        raise IOError("{0} does not exist".format(tprfile))

    proc = subprocess.Popen(['gmxdump', '-s', tprfile],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()

    if proc.returncode != 0:
        raise IOError("{0}\n{1}\n{2} is corrupted, see the above error\n\n".format(
            stderr, '#' * 79, tprfile))

    # Different from get_cpt_time, we use stdout this time
    nsteps_found_flag = False
    dt_found_flag = False
    for line in StringIO.StringIO(stdout):
        if 'nsteps' in line:
            nsteps = float(line.split('=')[1].strip())  # number of steps
            nsteps_found_flag = True
        elif "delta_t" in line:
            dt = float(line.split('=')[1].strip())      # unit: ps
            dt_found_flag = True

        if nsteps_found_flag and dt_found_flag:
            break
    ret = nsteps * dt / 1000       # unit: ns
    return ret

def cpt_less_than_tpr(cpt_f, tpr_f):
    cpt_t = get_cpt_time(cpt_f)
    tpr_t = get_tpr_time(tpr_f)
    return cpt_t < tpr_t

def parse_cmd_args(cmd_args=None):
    parser = argparse.ArgumentParser(
        prog='specify the gmxcheck version, and cpt file as input')
    parser.add_argument('-f', type=str, dest='inputfile',
                        help='specify the inputfile')
    parser.add_argument('--comp', nargs=2, dest='comp_fs',
                        help='for comparison, evaluate "cpt < tpr"')
    args = parser.parse_args(cmd_args)
    return args

def main(cmd_args):
    """
    If both -f and --comp are speicified, only -f will be considered
    """
    args = parse_cmd_args(cmd_args)
    if args.inputfile:
        file_type = args.inputfile[-3:]
        if file_type == "cpt":
            cpt_t = get_cpt_time(args.inputfile)
            sys.stdout.write('{0:.0f}'.format(cpt_t)) # unit: ns
        elif file_type == "tpr":
            tpr_t = get_tpr_time(args.inputfile)
            sys.stdout.write('{0:.0f}'.format(tpr_t))
        else:
            raise ValueError("Unrecoganized file type: {0}\n".format(args.inputfile))
    elif args.comp_fs:
        cpt_f, tpr_f = args.comp_fs
        sys.stdout.write(str(cpt_less_than_tpr(cpt_f, tpr_f)))

if __name__ == "__main__":
    # Surprise!! This won't produce exception even if sys.argv is of length 1.
    main(sys.argv[1:])
