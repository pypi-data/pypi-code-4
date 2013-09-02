# -*- coding: utf-8 -*-
import pkg_resources

from trac.util.translation import domain_functions


_, tag_, N_, add_tracpor_domain = \
            domain_functions('penelope.trac', ('_', 'tag_', 'N_', 'add_domain'))


def add_domains(env_path):
    locale_dir = pkg_resources.resource_filename(__name__, 'locale')
    add_tracpor_domain(env_path, locale_dir)
