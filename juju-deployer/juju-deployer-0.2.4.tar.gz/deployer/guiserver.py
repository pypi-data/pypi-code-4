"""Juju GUI server bundles deployment support.

The following functions are used by the Juju GUI server to validate and start
bundle deployments. The validate and import_bundle operations represents the
public API: they are directly called in the GUI server bundles support code,
which also takes care of handling any exception they can raise.
Those functions are blocking, and therefore the GUI server executes them in
separate processes.
See <https://code.launchpad.net/~juju-gui/charms/precise/juju-gui/trunk>.
"""

import os

from deployer.action.importer import Importer
from deployer.deployment import Deployment
from deployer.env.gui import GUIEnvironment
from deployer.utils import mkdir


# This value is used by the juju-deployer Importer object to store charms.
# This directory is usually created in the machine where the Juju GUI charm is
# deployed the first time a bundle deployment is requested.
JUJU_HOME = '/var/lib/juju-gui/juju-home'


def _validate(env, bundle):
    """Bundle validation logic, used by both validate and import_bundle.

    This function receives a connected environment and the bundle as a YAML
    decoded object.
    """
    # Retrieve the services deployed in the Juju environment.
    env_status = env.status()
    env_services = set(env_status['services'].keys())
    # Retrieve the services in the bundle.
    bundle_services = set(bundle.get('services', {}).keys())
    # Calculate overlapping services.
    overlapping = env_services.intersection(bundle_services)
    if overlapping:
        services = ', '.join(overlapping)
        error = 'service(s) already in the environment: {}'.format(services)
        raise ValueError(error)


def validate(apiurl, password, bundle):
    """Validate a bundle."""
    env = GUIEnvironment(apiurl, password)
    env.connect()
    try:
        _validate(env, bundle)
    finally:
        env.close()


def import_bundle(apiurl, password, name, bundle, options):
    """Import a bundle."""
    env = GUIEnvironment(apiurl, password)
    deployment = Deployment(name, bundle, [])
    importer = Importer(env, deployment, options)
    env.connect()
    # The Importer tries to retrieve the Juju home from the JUJU_HOME
    # environment variable: create a customized directory (if required) and
    # set up the environment context for the Importer.
    mkdir(JUJU_HOME)
    os.environ['JUJU_HOME'] = JUJU_HOME
    try:
        _validate(env, bundle)
        importer.run()
    finally:
        env.close()
