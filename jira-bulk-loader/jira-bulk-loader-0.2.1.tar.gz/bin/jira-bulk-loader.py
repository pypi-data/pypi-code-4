#!/usr/bin/python
#-*- coding: UTF-8 -*-

from jirabulkloader.task_extractor import TaskExtractor
import jirabulkloader.interface as iface

args = iface.get_options()

try:
    input_text = iface.get_template( args.template_file )
except IOError as e:
    print "Template file error: %s" % e
    exit(1)

options = {}
if args.duedate is not None: options['duedate'] = args.duedate
if args.priority is not None: options['priority'] = {'name':args.priority}
if args.project is not None: options['project'] = {'key':args.project}

task_ext = TaskExtractor(args.host, args.user, args.password, options, dry_run = args.dry_run)

from jirabulkloader.task_extractor_exceptions import TaskExtractorTemplateErrorProject, TaskExtractorJiraValidationError, TaskExtractorTemplateErrorJson, TaskExtractorJiraCreationError, TaskExtractorJiraHostProblem
from jirabulkloader.jiraConnect import JiraConnectConnectionError

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

print '===  The following structure will be created ===\n\n'

import sys
print breakdown.encode(sys.stdout.encoding, 'ignore')

print "\nDone."

