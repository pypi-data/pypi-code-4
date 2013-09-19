import base64
from pyrate.services import github

h = github.GithubPyrate('Chive', 'bighit.24')
p = 1

while p < 5:
    repos = h.do('orgs/divio/repos?type=source&per_page=100&page=' + str(p))
    f = open('log.txt', 'a')
    for repo in repos:
        found = False
        write = []
        if 'project' in repo['name']:
            print(repo['name'])
            for u in ['/requirements.txt', '/hard-requirements.txt', '/versions.cfg', '/versions-locked.cfg', '/versions-auto.cfg']:
                r = h.do('repos/divio/' + repo['name'] + '/contents' + u)
                try:
                    reqs = base64.b64decode(r['content'])
                    lines = reqs.split('\n')
                    for line in lines:
                        if 'django=' in line or 'Django=' in line\
                            or 'django =' in line or 'Django =' in line:
                            found = True
                            write.append(u + ': ' + line + '\n')
                except:
                    pass

            if found:
                f.write(repo['name'] + ' (' + repo['url'] + ')\n')
                for l in write:
                    f.write(l)
                f.write('\n')

    p += 1