#!/usr/bin/env python
"""
Juju Deployer

Deployment automation for juju.

"""


import argparse
import logging
import os
import sys
import time

from deployer.config import ConfigStack
from deployer.env import select_runtime
from deployer.action import diff, importer
from deployer.utils import ErrorExit, setup_logging


def setup_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--config',
        help=('File containing deployment(s) json config. This '
              'option can be repeated, with later files overriding '
              'values in earlier ones.'),
        dest='configs', action='append')
    parser.add_argument(
        '-d', '--debug', help='Enable debugging to stdout',
        dest="debug",
        action="store_true", default=False)
    parser.add_argument(
        '-L', '--local-mods',
        help='Disallow deployment of locally-modified charms',
        dest="no_local_mods", default=True, action='store_false')
    parser.add_argument(
        '-u', '--update-charms',
        help='Update existing charm branches',
        dest="update_charms", default=False, action="store_true")
    parser.add_argument(
        '-l', '--ls', help='List available deployments',
        dest="list_deploys", action="store_true", default=False)
    parser.add_argument(
        '-D', '--destroy-services',
        help='Destroy all services (do not terminate machines)',
        dest="destroy_services", action="store_true",
        default=False)
    parser.add_argument(
        '-T', '--terminate-machines',
        help=('Terminate all machines but the bootstrap node.  '
              'Destroy any services that exist on each'),
        dest="terminate_machines", action="store_true",
        default=False)
    parser.add_argument(
        '-t', '--timeout',
        help='Timeout (sec) for entire deployment (45min default)',
        dest='timeout', action='store', type=int, default=2700)
    parser.add_argument(
        "-f", '--find-service', action="store", type=str,
        help='Find hostname from first unit of a specific service.',
        dest="find_service")
    parser.add_argument(
        "-b", '--branch-only', action="store_true",
        help='Update vcs branches and exit.',
        dest="branch_only")
    parser.add_argument(
        '-B', '--bootstrap',
        help=('Bootstrap specified environment, blocks until ready'),
        dest="bootstrap", action="store_true",
        default=False)
    parser.add_argument(
        '-s', '--deploy-delay', action='store', type=float,
        help=("Time in seconds to sleep between 'deploy' commands, "
              "to allow machine provider to process requests. On "
              "terminate machines this also signals waiting for "
              "machine removal."),
        dest="deploy_delay", default=0)
    parser.add_argument(
        '-e', '--environment', action='store', dest='juju_env',
        help='Deploy to a specific Juju environment.',
        default=os.getenv('JUJU_ENV'))
    parser.add_argument(
        '-o', '--override', action='append', type=str,
        help=('Override *all* config options of the same name '
              'across all services.  Input as key=value.'),
        dest='overrides', default=None)
    parser.add_argument(
        '-v', '--verbose', action='store_true', default=False,
        dest="verbose", help='Verbose output')
    parser.add_argument(
        '-W', '--watch', help='Watch environment changes on console',
        dest="watch", action="store_true", default=False)
    parser.add_argument(
        '-r', "--retry", default=0, type=int, dest="retry_count",
        help=("Resolve CLI and unit errors via number of retries (default: 0)."
              " Either standalone or in a deployment"))
    parser.add_argument(
        "--diff", action="store_true", default=False,
        help=("Generate a delta between a configured deployment and a running"
             " environment."))
    parser.add_argument(
        '-w', '--relation-wait', action='store', dest='rel_wait',
        default=60, type=int,
        help=('Number of seconds to wait before checking for '
              'relation errors after all relations have been added '
              'and subordinates started. (default: 60)'))
    parser.add_argument("--description", help=argparse.SUPPRESS,
                        action="store_true")
    parser.add_argument("deployment", nargs="?")
    return parser


def main():
    stime = time.time()
    try:
        run()
    except ErrorExit:
        logging.getLogger('deployer.cli').info(
            "Deployment stopped. run time: %0.2f", time.time() - stime)
        sys.exit(1)


def run():
    parser = setup_parser()
    options = parser.parse_args()

    if options.description:
        print "Tool for declarative management of complex deployments."
        sys.exit(0)

    # Debug implies watching and verbose
    if options.debug:
        options.watch = options.verbose = True
    setup_logging(options.verbose, options.debug)

    log = logging.getLogger("deployer.cli")
    start_time = time.time()

    env = select_runtime(options.juju_env, options)
    log.debug('Using runtime %s', env.__class__.__name__)

    config = ConfigStack(options.configs or [])

    # Destroy services and exit
    if options.destroy_services or options.terminate_machines:
        log.info("Resetting environment...")
        env.connect()
        env.reset(terminate_machines=options.terminate_machines,
                  terminate_delay=options.deploy_delay,
                  watch=options.watch)
        log.info("Environment reset in %0.2f", time.time() - start_time)
        sys.exit(0)

    # Display service info and exit
    if options.find_service:
        address = env.get_service_address(options.find_service)
        if address is None:
            log.error("Service not found %r", options.find_service)
            sys.exit(1)
        elif not address:
            log.warning("Service: %s has no address for first unit",
                        options.find_service)
        else:
            log.info("Service: %s address: %s", options.find_service, address)
            print address
        sys.exit(0)

    # Just resolve/retry hooks in the environment
    if not options.deployment and options.retry_count:
        log.info("Retrying hooks for error resolution")
        env.connect()
        env.resolve_errors(
            options.retry_count, watch=options.watch, timeout=options.timeout)

    # Arg check on config files and deployment name.
    if not options.configs:
        log.error("Config files must be specified")
        sys.exit(1)

    config.load()

    # Just list the available deployments
    if options.list_deploys:
        print "\n".join(sorted(config.keys()))
        sys.exit(0)

    # Do something to a deployment
    if not options.deployment:
        # If there's only one option then use it.
        if len(config.keys()) == 1:
            options.deployment = config.keys()[0]
            log.info("Using deployment %s", options.deployment)
        else:
            log.error(
                "Deployment name must be specified. available: %s",
                tuple(sorted(config.keys())))
            sys.exit(1)

    deployment = config.get(options.deployment)

    if options.diff:
        diff.Diff(env, deployment, options).run()
        return

    # Import it
    log.info("Starting deployment of %s", options.deployment)
    importer.Importer(env, deployment, options).run()

    # Deploy complete
    log.info("Deployment complete in %0.2f seconds" % (
        time.time() - start_time))


if __name__ == '__main__':
    main()
