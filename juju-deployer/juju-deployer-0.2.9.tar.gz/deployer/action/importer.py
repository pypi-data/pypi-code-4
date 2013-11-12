import logging
import time

from .base import BaseAction
from ..errors import UnitErrors
from ..utils import ErrorExit


class Importer(BaseAction):

    log = logging.getLogger("deployer.import")

    def __init__(self, env, deployment, options):
        self.options = options
        self.env = env
        self.deployment = deployment

    def add_units(self):
        self.log.debug("Adding units...")
        # Add units to existing services that don't match count.
        env_status = self.env.status()
        reloaded = False

        for svc in self.deployment.get_services():
            cur_units = len(env_status['services'][svc.name].get('units', ()))
            delta = (svc.num_units - cur_units)

            if delta <= 0:
                self.log.debug(
                    " Service %r does not need any more units added.",
                    svc.name)
                continue

            charm = self.deployment.get_charm_for(svc.name)
            if charm.is_subordinate():
                self.log.warning(
                    "Config specifies num units for subordinate: %s",
                    svc.name)
                continue

            self.log.info(
                "Adding %d more units to %s" % (abs(delta), svc.name))
            if svc.unit_placement:
                # Reload status once after non placed services units are done.
                if reloaded is False:
                    # Crappy workaround juju-core api inconsistency
                    time.sleep(5.1)
                    env_status = self.env.status()
                    reloaded = True

                for mid in range(cur_units, svc.num_units):
                    mspec = self.deployment.get_unit_placement(
                        svc, mid, env_status)
                    self.env.add_unit(svc.name, mspec)
            else:
                self.env.add_units(svc.name, abs(delta))

    def get_charms(self):
        # Get Charms
        self.log.debug("Getting charms...")
        self.deployment.fetch_charms(
            update=self.options.update_charms,
            no_local_mods=self.options.no_local_mods)

        # Load config overrides/includes and verify rels after we can
        # validate them.
        self.deployment.resolve(self.options.overrides or ())

    def deploy_services(self):
        self.log.info("Deploying services...")
        env_status = self.env.status()
        reloaded = False

        for svc in self.deployment.get_services():
            if svc.name in env_status['services']:
                self.log.debug(
                    " Service %r already deployed. Skipping" % svc.name)
                continue

            charm = self.deployment.get_charm_for(svc.name)
            self.log.info(
                " Deploying service %s using %s", svc.name, charm.charm_url)

            if svc.unit_placement:
                # We sorted all the non placed services first, so we only
                # need to update status once after we're done with them.
                if not reloaded:
                    self.log.debug(
                        " Refetching status for placement deploys")
                    time.sleep(5.1)
                    env_status = self.env.status()
                    reloaded = True
                num_units = 1
            else:
                num_units = svc.num_units

            self.env.deploy(
                svc.name,
                charm.charm_url,
                self.deployment.repo_path,
                svc.config,
                svc.constraints,
                num_units,
                self.deployment.get_unit_placement(svc, 0, env_status))

            if svc.annotations:
                self.log.debug(" Setting annotations")
                self.env.set_annotation(svc.name, svc.annotations)

            if svc.expose:
                self.log.info(" Exposing service %r" % svc.name)
                self.env.expose(svc.name)

            if self.options.deploy_delay:
                self.log.debug(" Waiting for deploy delay")
                time.sleep(self.options.deploy_delay)

    def add_relations(self):
        self.log.info("Adding relations...")

        # Relations
        status = self.env.status()
        created = False

        for end_a, end_b in self.deployment.get_relations():
            if self._rel_exists(status, end_a, end_b):
                continue
            self.log.info(" Adding relation %s <-> %s", end_a, end_b)
            self.env.add_relation(end_a, end_b)
            created = True
            # per the original, not sure the use case.
            #self.log.debug(" Waiting 5s before next relation")
            #time.sleep(5)
        return created

    def _rel_exists(self, status, end_a, end_b):
        # Checks for a named relation on one side that matches the local
        # endpoint and remote service.
        (name_a, name_b, rem_a, rem_b) = (end_a, end_b, None, None)

        if ":" in end_a:
            name_a, rem_a = end_a.split(":", 1)
        if ":" in end_b:
            name_b, rem_b = end_b.split(":", 1)

        rels_svc_a = status['services'][name_a].get('relations', {})

        found = False
        for r, related in rels_svc_a.items():
            if name_b in related:
                if rem_a and not r in rem_a:
                    continue
                found = True
                break
        if found:
            return True
        return False

    def wait_for_units(self, ignore_error=False):
        timeout = self.options.timeout - (time.time() - self.start_time)
        if timeout < 0:
            self.log.error("Reached deployment timeout.. exiting")
            raise ErrorExit()
        try:
            self.env.wait_for_units(
                int(timeout), watch=self.options.watch, no_exit=ignore_error)
        except UnitErrors:
            if not ignore_error:
                raise

    def run(self):
        self.start_time = time.time()
        if self.options.bootstrap:
            self.env.bootstrap()
        self.env.connect()

        # Get charms
        self.get_charms()
        if self.options.branch_only:
            return

        self.deploy_services()

        # Workaround api issue in juju-core, where any action takes 5s
        # to be consistent to subsequent watch api interactions, see
        # http://pad.lv/1203105 which will obviate this wait.
        time.sleep(5.1)
        self.add_units()

        self.log.debug("Waiting for units before adding relations")
        self.wait_for_units()

        rels_created = self.add_relations()

        # Wait for the units to be up before waiting for rel stability.
        if rels_created:
            self.log.debug(
                "Waiting for relation convergence %ds", self.options.rel_wait)
            time.sleep(self.options.rel_wait)
            self.wait_for_units(self.options.retry_count)

        if self.options.retry_count:
            self.log.info("Looking for errors to auto-retry")
            self.env.resolve_errors(
                self.options.retry_count,
                self.options.timeout - time.time() - self.start_time)
