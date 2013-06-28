#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyrax
import pyrax.utils as utils

pyrax.set_environment("gluecon")
pyrax.keyring_auth()
cs = pyrax.cloudservers
clb = pyrax.cloud_loadbalancers
cdb = pyrax.cloud_databases
cnw = pyrax.cloud_networks
dns = pyrax.cloud_dns

iso_network_name = "GlueconNetwork"
iso_network_cidr = "192.168.0.0/24"

# Create the new network
iso_net = cnw.create(iso_network_name, cidr=iso_network_cidr)

networks = new_net.get_server_networks(public=False, private=False)
isolated = cs.servers.create("isolated", img_id, flavor_id,
        nics=networks)
print "Isolated server:", isolated.name, isolated.id



iso_net.delete()
