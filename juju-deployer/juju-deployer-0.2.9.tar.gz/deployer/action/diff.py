import logging
import time

from .base import BaseAction
from ..relation import EndpointPair
from ..utils import _parse_constraints, yaml_dump


class Diff(BaseAction):

    log = logging.getLogger("deployer.diff")

    def __init__(self, env, deployment, options):
        self.options = options
        self.env = env
        self.deployment = deployment
        self.env_status = None
        self.env_state = {'services': {}, 'relations': []}

    def load_env(self):
        """
        """
        rels = set()
        for svc_name in self.env_status['services']:
            if not svc_name in self.env_status['services']:
                self.env_state['services'][svc_name] = 'missing'
            self.env_state['services'].setdefault(svc_name, {})[
                'options'] = self.env.get_config(svc_name)
            self.env_state['services'][svc_name][
                'constraints'] = self.env.get_constraints(svc_name)
            self.env_state['services'][svc_name][
                'unit_count'] = len(self.env_status[
                    'services'][svc_name]['units'])
            rels.update(self._load_rels(svc_name))
        self.env_state['relations'] = sorted(rels)

    def _load_rels(self, svc_name):
        rels = set()
        svc_rels = self.env_status['services'][svc_name].get(
            'relations', {})
        # There is ambiguity here for multiple rels between two
        # services without the relation id, which we need support
        # from core for.
        for r_name, r_svcs in svc_rels.items():
            for r_svc in r_svcs:
                # Skip peer relations
                if r_svc == svc_name:
                    continue
                rr_name = self._get_rel_name(svc_name, r_svc)
                rels.add(
                    tuple(sorted([
                        "%s:%s" % (svc_name, r_name),
                        "%s:%s" % (r_svc, rr_name)])))
        return rels

    def _get_rel_name(self, src, tgt):
        svc_rels = self.env_status['services'][tgt]['relations']
        found = None
        for r, eps in svc_rels.items():
            if src in eps:
                if found:
                    raise ValueError("Ambigious relations for service")
                found = r
        return found

    def get_delta(self):
        delta = {}
        rels_delta = self._get_relations_delta()
        if rels_delta:
            delta['relations'] = rels_delta
        svc_delta = self._get_services_delta()
        if svc_delta:
            delta['services'] = svc_delta
        return delta

    def _get_relations_delta(self):
        # Simple endpoint diff, no qualified endpoint checking.

        # Env relations are always qualified (at least in go).
        delta = {}
        env_rels = set(
            EndpointPair(*x) for x in self.env_state.get('relations', ()))
        dep_rels = set(
            [EndpointPair(*y) for y in self.deployment.get_relations()])

        for r in dep_rels.difference(env_rels):
            delta.setdefault('missing', []).append(r)

        for r in env_rels.difference(dep_rels):
            delta.setdefault('unknown', []).append(r)

        return delta

    def _get_services_delta(self):
        delta = {}
        env_svcs = set(self.env_status['services'].keys())
        dep_svcs = set([s.name for s in self.deployment.get_services()])

        missing = dep_svcs - env_svcs
        if missing:
            delta['missing'] = {}
        for a in missing:
            delta['missing'][a] = self.deployment.get_service(
                a).svc_data
        unknown = env_svcs - dep_svcs
        if unknown:
            delta['unknown'] = {}
        for r in unknown:
            delta['unknown'][r] = self.env_state.get(r)

        for cs in env_svcs.intersection(dep_svcs):
            d_s = self.deployment.get_service(cs).svc_data
            e_s = self.env_state['services'][cs]
            mod = self._diff_service(e_s, d_s)
            if not mod:
                continue
            if not 'modified' in delta:
                delta['modified'] = {}
            delta['modified'][cs] = mod
        return delta

    def _diff_service(self, e_s, d_s):
        mod = {}
        if 'constraints' in d_s:
            d_sc = _parse_constraints(d_s['constraints'])
            if d_sc != e_s['constraints']:
                mod['constraints'] = e_s['constraints']
        for k, v in d_s.get('options', {}).items():
            # Deploy options not known to the env may originate
            # from charm version delta or be an invalid config.
            if not k in e_s['options']:
                continue
            e_v = e_s['options'].get(k, {}).get('value')
            if e_v != v:
                mod['config'] = {k: e_v}
        if e_s['unit_count'] != d_s.get('num_units', 1):
            mod['num_units'] = e_s['unit_count'] - d_s['num_units']
        return mod

    def run(self):
        self.start_time = time.time()
        self.env.connect()
        self.env_status = self.env.status()
        self.load_env()
        delta = self.get_delta()
        if delta:
            print yaml_dump(delta)
