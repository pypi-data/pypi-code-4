TASKER_HOST = 'taskworkshop.com'
TASKER_PORT = 443
TASKER_PROTO = 'https'
TASKER_API = 'api/v1'
TASKER_URL = '{0}://{1}:{2}/{3}/{{0}}.json'.format(
    TASKER_PROTO, TASKER_HOST, TASKER_PORT, TASKER_API)

TASKER_ENV = ''

HELP = """Task Workshop CLI thin client.

Usage:
{0}

Options:
  -i --interactive     Take arguments for command after starting application
                       (default if you give wrong number of arguments or no
                       arguments)
  -h --help            Show this screen
  -p --project_id      Use specified project id (currently active project
                       is default)
  -t --token           Use specified token for this action (by default token
                       is stored in settings)

"""

HELP_USAGE = "  {0} {1:<25} {2:<30}"
