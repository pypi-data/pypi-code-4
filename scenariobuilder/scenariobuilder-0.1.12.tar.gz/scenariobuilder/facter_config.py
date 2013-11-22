#!/usr/bin/env python
"""
    stack-builder.facter_config
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module will read metadata set during instance
    launch and override any yaml under the /etc/puppet/data
    directory (except data_mappings) that has a key matching
    the metadata
"""

import yaml
import os

# Child processes cannot set environment variables, so
# create a bash file to set some exports for facter
def create(metadata):
    facts = ""
    for key,value in metadata.items():
        # Things with spaces can't be exported
        if ' ' not in str(value):
            facts = facts + 'FACTER_' + str(key) + '=' + str(value) + '\n'
    return facts
