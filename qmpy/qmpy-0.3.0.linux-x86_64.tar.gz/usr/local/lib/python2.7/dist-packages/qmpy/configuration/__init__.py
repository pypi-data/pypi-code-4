import ConfigParser
import json
from qmpy import INSTALL_PATH
from qmpy.computing.resources import Host, Account, Project, Allocation
from django.contrib.auth.models import User
from qmpy.configuration.resources import *

config = ConfigParser.ConfigParser()
config.read(INSTALL_PATH+'/configuration/site.cfg')

VASP_POTENTIALS = config.get('VASP', 'potential_path')

def sync_resources():
    for host, data in hosts.items():
        h = Host.objects.get_or_create(name=host)[0]
        h.__dict__.update({'check_queue':data['check_queue'],
            'ip_address':data['ip_address'],
            'binaries':data['binaries'],
            'ppn':data['ppn'],
            'nodes':data['nodes'],
            'walltime':data['walltime'],
            'sub_script':data['sub_script'],
            'sub_text':data['sub_text']})

        h.save()

    for user, data in users.items():
        u = User.objects.get_or_create(username=user)[0]
        u.save()
        for host, adata in data.items():
            host = Host.objects.get_or_create(name=host)[0]
            host.save()
            acc = Account.objects.get_or_create(user=u, host=host)[0]
            acc.__dict__.update(**adata)
            acc.save()

    for allocation, data in allocations.items():
        host = Host.objects.get_or_create(name=data['host'])[0]
        host.save()
        alloc = Allocation.objects.get_or_create(name=allocation)[0]
        alloc.host = host
        alloc.key = data.get('key', '')
        alloc.save()
        for user in data['users']:
            user = User.objects.get_or_create(username=user)[0]
            user.save()
            alloc.users.add(user)

    for project, data in projects.items():
        proj = Project.objects.get_or_create(name=project)[0]
        proj.save()

        for user in data['users']:
            user = User.objects.get_or_create(username=user)[0]
            user.save()
            proj.users.add(user)

        for allocation in data['allocations']:
            alloc = Allocation.objects.get_or_create(name=allocation)[0]
            alloc.save()
            proj.allocations.add(alloc)
