from __future__ import print_function

import json
import urlparse
import argparse
import requests
import ConfigParser

API_ROOT = '/rest/api/2'

class JIRAException(Exception):
    
    def __init__(self, message, code):
        super(JIRAException, self).__init__(message)
        self.code = code

class JIRA(object):
    """Helper class for executing JIRA operations
    """

    def __init__(self, username, password, base_url):
        self.username = username
        self.password = password
        self.base_url = base_url

    def get(self, rest_url, params={}):
        """Make a GET web service call to rest_url and return the results as JSON.
        """
        url = urlparse.urljoin(self.base_url, API_ROOT) + rest_url
        r = requests.get(url, params=params, auth=(self.username, self.password))

        if r.status_code == 200:
            return r.json()
        elif r.status_code > 200 and r.status_code < 300:
            return None
        else:
            raise JIRAException("Error %d in GET request from %s" % (r.status_code, r.url), r.status_code)

    def post(self, rest_url, data={}):
        """Make a POST web service call to rest_url and return the results as JSON.
        """
        url = urlparse.urljoin(self.base_url, API_ROOT) + rest_url
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(data), headers=headers, auth=(self.username, self.password))

        if r.status_code == 200:
            return r.json()
        elif r.status_code > 200 and r.status_code < 300:
            return None
        else:
            raise JIRAException("Error %d in POST request to %s with body %s" % (r.status_code, r.url, r.request.body), r.status_code)

    # Higher order operations

    def fetch_issue(self, issue_key):
        return self.get('/issue/' + issue_key)

    def fetch_issue_transitions(self, issue_key):
        return self.get('/issue/%s/transitions' % issue_key)

    def transition_issue(self, issue_key, transition_id, comment):
        return self.post('/issue/%s/transitions' % issue_key, data={
            'update': {
                'comment': [{
                    'add': {
                        'body': comment
                    }
                }]
            },
            'transition': {
                'id': transition_id
            }
        })


class Configuration(object):
    """Load and store the configuration
    """

    columns_section = 'columns'

    def __init__(self, filename):
        self.parser = ConfigParser.SafeConfigParser()
        self.parser.read(filename)

    def get_status(self, column_number):
        try:
            return self.parser.get(self.columns_section, str(column_number))
        except ConfigParser.NoOptionError:
            return None


class Klopfer(object):
    """Load and store the Klopfer output
    """

    tickets = {} # Map ticket id -> column number

    def __init__(self, filename):
        self.tickets = {}
        data = {}
        with open(filename, 'r') as f:
            data = json.loads(f.read())

        for info in data['board']['informations'].values():
            self.tickets[info['data']] = info['column']


def map_jira_statuses(jira, config, klopfer):
    """Run the mapping of tickets in the Klopfer file to JIRA using the
    column configuration
    """

    for ticket_id, column_number in klopfer.tickets.items():
        try:
            issue_data = jira.fetch_issue(ticket_id)
        except JIRAException as e:
            if e.code == 404:
                print("Could not find ticket with id %s in JIRA" % ticket_id)
                continue
            else:
                raise

        current_status = issue_data['fields']['status']['name']
        wall_status = config.get_status(column_number)

        if wall_status and wall_status != current_status:
            transitions = jira.fetch_issue_transitions(ticket_id)

            # Look for a transition that gets us to the target state
            moved = False
            for transition_info in transitions['transitions']:
                if transition_info['to']['name'] == wall_status:
                    jira.transition_issue(ticket_id, transition_info['id'], "Moved on physical card wall")
                    print("Moved from %s to %s" % (current_status, wall_status,))
                    moved = True
                    break

            if not moved:
                print("Could not find transition to move from %s to %s" % (current_status, wall_status,))

# Console script

def run():
    parser = argparse.ArgumentParser(description='Update JIRA to reflect a JimFlow Kanban wall')
    parser.add_argument('--url', dest='url', help='JIRA instance URL')
    parser.add_argument('--username', dest='username', help='JIRA user name')
    parser.add_argument('--password', dest='password', help='JIRA password')
    parser.add_argument('--config', dest='config', help='Configuration file')
    parser.add_argument(metavar='klopfer-output.json', dest='file', help='JimFlowKlopfer output file')

    args = parser.parse_args()

    if not args.url or not args.username or not args.password or not args.config or not args.file:
        parser.print_usage()
        return 1

    jira = JIRA(args.username, args.password, args.url)
    config = Configuration(args.config)
    klopfer = Klopfer(args.file)

    map_jira_statuses(jira, config, klopfer)
    print("Done")

    return 0
