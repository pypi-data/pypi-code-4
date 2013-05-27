import os
from shutil import rmtree
from cubicweb import UnknownEid

cacheroot = session.repo.config['local-repo-cache-root']
for eid in os.listdir(cacheroot):
    try:
        repo = session.entity_from_eid(int(eid))
    except ValueError:
        print eid, 'is not a valid eid'
    except UnknownEid:
        print 'removing unknown', eid
        rmtree(os.path.join(cacheroot, eid))
    else:
        if not repo.__regid__ == 'Repository':
            print 'removing not-a-repository', eid
            rmtree(os.path.join(cacheroot, eid))

