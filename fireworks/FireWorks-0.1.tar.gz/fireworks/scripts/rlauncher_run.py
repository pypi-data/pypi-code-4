#!/usr/bin/env python

"""
A runnable script to launch a single Rocket (a command-line interface to rocket_launcher.py)
"""
from argparse import ArgumentParser
import os
from fireworks.core.fw_config import FWConfig
from fireworks.core.launchpad import LaunchPad
from fireworks.core.fworker import FWorker
from fireworks.core.rocket_launcher import rapidfire, launch_rocket


__author__ = 'Anubhav Jain'
__copyright__ = 'Copyright 2013, The Materials Project'
__version__ = '0.1'
__maintainer__ = 'Anubhav Jain'
__email__ = 'ajain@lbl.gov'
__date__ = 'Feb 7, 2013'


def rlaunch():
    m_description = 'This program launches one or more Rockets. A Rocket grabs a job from the central database and ' \
                    'runs it. The "single-shot" option launches a single Rocket, ' \
                    'whereas the "rapidfire" option loops until all FireWorks are completed.'

    parser = ArgumentParser(description=m_description)
    subparsers = parser.add_subparsers(help='command', dest='command')
    single_parser = subparsers.add_parser('singleshot', help='launch a single Rocket')
    rapid_parser = subparsers.add_parser('rapidfire',
                                         help='launch multiple Rockets (loop until all FireWorks complete)')

    single_parser.add_argument('-f', '--fw_id', help='specific fw_id to run', default=None, type=int)

    rapid_parser.add_argument('--nlaunches', help='num_launches (int or "infinite")', default=0)
    rapid_parser.add_argument('--sleep', help='sleep time between loops (secs)', default=None, type=int)

    parser.add_argument('-l', '--launchpad_file', help='path to launchpad file', default=FWConfig().LAUNCHPAD_LOC)
    parser.add_argument('-w', '--fworker_file', help='path to fworker file', default=FWConfig().FWORKER_LOC)
    parser.add_argument('-c', '--config_dir', help='path to a directory containing the config file (used if -l, -w unspecified)',
                        default=FWConfig().CONFIG_FILE_DIR)

    parser.add_argument('--loglvl', help='level to print log messages', default='INFO')
    parser.add_argument('-s', '--silencer', help='shortcut to mute log messages', action='store_true')

    args = parser.parse_args()

    if not args.launchpad_file and os.path.exists(os.path.join(args.config_dir, 'my_launchpad.yaml')):
        args.launchpad_file = os.path.join(args.config_dir, 'my_launchpad.yaml')

    if not args.fworker_file and os.path.exists(os.path.join(args.config_dir, 'my_fworker.yaml')):
        args.fworker_file = os.path.join(args.config_dir, 'my_fworker.yaml')

    args.loglvl = 'CRITICAL' if args.silencer else args.loglvl

    if args.launchpad_file:
        launchpad = LaunchPad.from_file(args.launchpad_file)
    else:
        launchpad = LaunchPad(strm_lvl=args.loglvl)

    if args.fworker_file:
        fworker = FWorker.from_file(args.fworker_file)
    else:
        fworker = FWorker()

    if args.command == 'rapidfire':
        rapidfire(launchpad, fworker, None, args.nlaunches, -1, args.sleep, args.loglvl)

    else:
        launch_rocket(launchpad, fworker, args.fw_id, args.loglvl)

if __name__ == '__main__':
    rlaunch()