import argparse
from ConfigParser import SafeConfigParser
import config
from .app import runserver
from .checkers import JenkinsChecker, URLChecker, SupervisorChecker


CONF_TO_CHERCKER = {
    'url': URLChecker,
    'jenkins': JenkinsChecker,
    'supervisor': SupervisorChecker
}


class VuConfig(object):
    def __init__(self, config_file):
        self.checker_conf_keyword = "checker"
        self.parser = SafeConfigParser()
        self.parser.read(config_file)
        for section in self.parser.sections():
            self.parse_section(section)

    def parse_section(self, section):
        if section.startswith('%s:' % self.checker_conf_keyword):
            self.create_checker(section=section)

    def create_checker(self, section):
        try:
            name = section.split(':')[1]
            section_name = "%s:%s" % (self.checker_conf_keyword, name)
            clss = CONF_TO_CHERCKER[self.parser.get(section_name, 'type')]
            url = self.parser.get(section_name, 'url')
            kwargs = {}
            for k, v in dict(self.parser.items(section_name)).items():
                if k not in ['type', 'url']:
                    kwargs[k] = v
            config.CHECK_INDEX.append({
                'name': name,
                'url': url,
                'type': clss,
                'kwargs': kwargs
            })
        except KeyError:
            print "The section \"%s\" cannot be created. Wrong type" % section


def run():
    parser = argparse.ArgumentParser(description='Runs VU over the web on local network.')
    parser.add_argument('-p', '--port', dest='port', default=8888, help="default HTTP port", type=int),
    parser.add_argument('-c', '--conf', dest='conf',  help="VU Configuration file"),
    args = parser.parse_args()
    VuConfig(args.conf)
    runserver(port=args.port)


if __name__ == "__main__":
    run()
