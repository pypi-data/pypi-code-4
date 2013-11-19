import base64
from issue import Issue, Issues
__author__ = 'alexey.grachev'
import requests
import re
import logging
import os.path
import sys


baseUrl = r'http://jira.ringcentral.com/rest/api/2/search?fields=summary,key,description&maxResults=200&'
openIssesUrl = baseUrl + r'jql=status = Open AND text ~ "TAS crash" AND assignee in (telcoduty) ORDER BY created ASC'
specificIssesUrl = baseUrl + r'jql=Key in ({0})'

machineMask = r'(\w\w\w\d\d-\w\d\d-\w\w\w\d\d)'
serviceMask = r'(TAM|TGS)'
dateMask = r'(\d\d\d\d[\.\-]\d\d[\.\-]\d\d)'
timeMask = r'(\d\d:\d\d:\d\d)'


def tryStore(issue, results):
    if issue.machine() or issue.archive() or issue.unpacked():
        logging.debug("New issue: " + str(issue))
        results.append(issue)
        issue = Issue()
    return issue


#sjc01-p05-tas02 2013.09.18 19:37:55
#d:\log\pro\2013.09.27\logs_2013-09-21_SJC01-P06-TAS12.zip 19:37:55
#d:\log\pro\2013.09.27\ 19:37:55
#sjc01-p05-tas02/mnt/rclogbackup-iad01-tmp/2013-09-17/logs_2013-09-17_IAD01-P09-TAS05.zip 19:37:55 not implemented
def parseIssues(input):
    logging.debug("parseIssues " + str(input))
    results = list()
    issue = Issue()
    for item in input:
        if re.match(machineMask, item):
            issue = tryStore(issue, results)
            issue.setMachine(item)
        elif re.match(dateMask, item):
            issue.setDate(item)
        elif re.match(timeMask, item):
            issue.setTime(item)
        else:
            if os.path.splitext(item)[1].lower() == '.zip':
                issue = tryStore(issue, results)
                issue.setArchive(item)
            else:
                issue = tryStore(issue, results)
                issue.setUnpacked(item)
    issue = tryStore(issue, results)
    return results

def getGroupSafe(matchObject):
    return matchObject.group(0) if matchObject else None

def getIssues(issues, userName, password, onIssue):
    logging.info("------------------------------Gettting issues: " + (str(issues) if issues else "all opened"))

    if issues:
        request = specificIssesUrl.format(','.join(issues))
    else:
        request = openIssesUrl

    try:
        response = requests.get(request, auth=(userName, password))
        response.raise_for_status()
        jsonIssues = response.json()['issues']
    except Exception as e:
        logging.error(str(e))
        logging.debug('Traceback', exc_info=sys.exc_info())
        raise Exception("Failed to get issues")

    for jsonIssue in jsonIssues:
        try:
            desc = jsonIssue['fields']['description']
            onIssue(jsonIssue['key'],
                    machine=getGroupSafe(re.search(machineMask, desc)),
                    service=getGroupSafe(re.search(serviceMask, desc)),
                    eventDate=getGroupSafe(re.search(dateMask, desc)),
                    eventTime=getGroupSafe(re.search(timeMask, desc)))

        except Exception as e:
            logging.error(str(e))
            logging.debug('Traceback', exc_info=sys.exc_info())
