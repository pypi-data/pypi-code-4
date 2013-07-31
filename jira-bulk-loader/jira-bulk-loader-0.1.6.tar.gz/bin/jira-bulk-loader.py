#!/usr/bin/python
#-*- coding: UTF-8 -*-

import argparse
from jirabulkloader.task_extractor import TaskExtractor
from jirabulkloader.task_extractor_exceptions import TaskExtractorTemplateErrorProject, TaskExtractorJiraValidationError, TaskExtractorTemplateErrorJson, TaskExtractorJiraCreationError, TaskExtractorJiraHostProblem
from jirabulkloader.jiraConnect import JiraConnectConnectionError

prg_description="Uses template file to create many tasks in Jira at once"

prg_epilog="""Report bugs to: <https://bitbucket.org/oktopuz/jira-bulk-loader/issues>
Project home page: <https://bitbucket.org/oktopuz/jira-bulk-loader>"""

parser = argparse.ArgumentParser(description=prg_description, formatter_class=argparse.RawDescriptionHelpFormatter, epilog=prg_epilog)

parser.add_argument('template_file', help='file containing tasks definition')
parser.add_argument('-W', dest='project', help='Project key')
parser.add_argument('-R', dest='priority', help='Task priority. "Medium" by default', default="Medium")
parser.add_argument('-D', dest='dueDate', help='dueDate  (YYYY-mm-DD). For example: 2012-05-31')
parser.add_argument('--dry', dest='dry_run', action='store_true', help='Make a dry run. It checks everything but does not create tasks', default=False)

mandatory = parser.add_argument_group('mandatory arguments')
mandatory.add_argument('-H', dest='hostname', required=True, help='Jira hostname with http:// or https://')
mandatory.add_argument('-U', dest='username', required=True, help='your Jira username')
mandatory.add_argument('-P', dest='password', required=True, help='your Jira password')

args = parser.parse_args()


##############################################################
# open input file, parse and create tasks

import codecs
try:
    f = codecs.open(args.template_file, encoding='utf-8')
    input_text = f.read()
except IOError as e:
    print "Template file error: %s" % e
    exit(1)
else:
    f.close()

options = {}
if args.dueDate: options['duedate'] = args.dueDate
if args.priority: options['priority'] = {'name':args.priority}
if args.project: options['project'] = {'key':args.project}

task_ext = TaskExtractor(args.hostname, args.username, args.password, options, dry_run = args.dry_run)

try:
    print "Parsing task list.."
    tasks =  task_ext.load(input_text)

    print "Validating tasks.."
    task_ext.validate_load(tasks)

    print "Creating tasks.."
    breakdown = task_ext.create_tasks(tasks)

except (TaskExtractorTemplateErrorProject, TaskExtractorJiraValidationError, TaskExtractorJiraCreationError, TaskExtractorJiraHostProblem, JiraConnectConnectionError) as e:
    print e.message
    exit(1)
except TaskExtractorTemplateErrorJson, e:
    print "ERROR: The following line in template is not valid:", e.error_element
    print "A correct JSON structure expected."
    exit(1)

print '===  The following structure will be created ===' + '\n\n' + breakdown

print "\nDone."

