from .checkers import JenkinsChecker, URLChecker, SupervisorChecker


CHECK_INDEX = []

sdgf = [
    {
        'name': 'Site Front',
        'url': 'http://www.engage-sports.com/',
        'type': URLChecker
    },
]


OCHECK_INDEX = [
    {
        'name': 'Site Front',
        'url': 'http://www.engage-sports.com/',
        'type': URLChecker
    },
    {
        'name': 'Site Manage',
        'url': 'http://manage.engage-sports.com/',
        'type': URLChecker
    },
    {
        'name': 'Site Manage UI2',
        'url': 'http://ui2.manage.engage-sports.com/',
        'type': URLChecker
    },
    {
        'name': 'Site Admin',
        'url': 'http://admin.engage-sports.com/',
        'type': URLChecker
    },
    {
        'name': 'Site Ligue LMLR',
        'url': 'http://lmlr.org/',
        'type': URLChecker
    },
    {
        'name': 'Site Front pop',
        'url': 'http://pop.engage-sports.com/',
        'type': URLChecker
    },
    {
        'name': 'Site Motoball',
        'url': 'http://motoball.engage-sports.com/',
        'type': URLChecker
    },
    {
        'name': 'Site Velo',
        'url': 'http://velo.engage-sports.com/',
        'type': URLChecker
    },
    {
        'name': 'Site URL Shortener',
        'url': 'http://spor.tl/',
        'type': URLChecker
    },
    {
        'name': 'Site Monitoring',
        'url': 'http://monitoring.engage-sports.com/',
        'type': URLChecker
    },
    {
        'name': 'Site Static (CSS/JS ...)',
        'url': 'http://static.engage-sports.com/',
        'type': URLChecker
    },
    {
        'name': 'Supervisor',
        'url': 'http://processes.engage-sports.com/',
        'type': URLChecker,
        'kwargs': {
            'http_user': 'engage',
            'http_password': 'EngageMC2'
        }
    },
    {
        'name': 'Jenkins Engage (default)',
        'url': 'http://ci.engage-sports.com/',
        'type': JenkinsChecker,
        'kwargs': {
            'jenkins_url': "http://ci.engage-sports.com/job/Engage-Sports.com/lastCompletedBuild/api/json",
            'http_user': 'engagesports',
            'http_password': 'Eating Frogs'
        }
    },
    {
        'name': 'Jenkins Engage (pre_prod)',
        'url': 'http://ci.engage-sports.com/',
        'type': JenkinsChecker,
        'kwargs': {
            'jenkins_url': "http://ci.engage-sports.com/job/Engage-Sports-Pre-Prod/lastCompletedBuild/api/json",
            'http_user': 'engagesports',
            'http_password': 'Eating Frogs'
        }
    },
]

"""
    {
        'name': 'Process Front',
        'url': 'http://processes.engage-sports.com/',
        'type': SupervisorChecker,
        'kwargs': {
            'bind': "http://engage:EngageMC2@processes.engage-sports.com/",
            'process_name': "engageweb:institution"
        }
    }
"""
