
import ConfigParser
import os
import argparse

        
def parse():
    """Create argparse structure and parse arguments"""

    parser = argparse.ArgumentParser( \
        description="A command line tool to create issues in Atlassian JIRA via REST API.",
        formatter_class=argparse.RawDescriptionHelpFormatter, \
        epilog="Project home page: <https://bitbucket.org/oktopuz/jira-bulk-loader>",
        )

    parser.add_argument('template_file', help='a file containing issues definition')
    parser.add_argument('--dry', dest='dry_run', action='store_true', \
        help='make a dry run. It checks everything but does not create issues', default=False)

    required = parser.add_argument_group('required arguments')
    required.add_argument('-H', '--host',  required=True, help='JIRA hostname with http:// or https://')
    required.add_argument('-U', '--user', required=True, help='your username')
    required.add_argument('-P', dest='password', help='your password. You\'ll be prompted for it if not specified')

    issue_attr = parser.add_argument_group('JIRA attributes')
    issue_attr.add_argument('-W', '--project', help='project key')
    issue_attr.add_argument('-R', '--priority', help="default issue priority. 'Medium' if not specified", default="Medium")
    issue_attr.add_argument('-D', '--duedate', help='default issue dueDate (YYYY-mm-DD)')


    return parser.parse_args()

parse()


'''
    def __read_config_file(path_to_executable):
        """
        Read configuration file and return dict of options.

        The config file (jira-bulk-loader.cfg) must be located either 
        in the same directory as 'path_to_executable' or in ~/.config/jira-bulk-loader/.
        The only possible section is 'connection'.

        Example:
        [connection]
        hostname = https://jira.atlassian.com
        username = my_jira_user
        """

        r = {}
        config = ConfigParser.RawConfigParser()

        project_name = 'jira-bulk-loader'
        default_cfg_filename = project_name + '.cfg'

        config.read([ \
            os.path.join(os.path.dirname(path_to_executable), default_cfg_filename), \
            os.path.join(os.path.expanduser('~/.config/' + project_name), default_cfg_filename)
            ])

        try:
            for item in config.items('connection'):
                r[item[0]] = item[1]
        except ConfigParser.NoSectionError:
            pass

        return r

'''
