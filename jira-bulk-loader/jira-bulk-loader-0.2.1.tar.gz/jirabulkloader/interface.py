

def get_options( args_list = None ):
    """Create argparse structure and parse arguments"""

    import argparse

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
    required.add_argument('-P', dest='password', required=True, help='your password. You\'ll be prompted for it if not specified')

    issue_attr = parser.add_argument_group('JIRA attributes')
    issue_attr.add_argument('-W', '--project', help='project key')
    issue_attr.add_argument('-R', '--priority', help="default issue priority. 'Medium' if not specified", default="Medium")
    issue_attr.add_argument('-D', '--duedate', help='default issue dueDate (YYYY-mm-DD)')

    return parser.parse_args( args_list )


def get_template( template_filename ):
    """Read template file using uft-8 encoding.
    If there is no such file, IOError exception will be raised."""

    import io
    import codecs

    with io.open( template_filename, 'rt', encoding='utf-8' ) as f:
        tmpl = f.read()
        if tmpl[0] == unicode( codecs.BOM_UTF8, 'utf8' ):
            return tmpl[1:]
        else:
            return tmpl


