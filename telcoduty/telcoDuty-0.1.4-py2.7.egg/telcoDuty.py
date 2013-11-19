__author__ = 'alexey.grachev'
from MaskingFormatter import MaskingFormatter
import traceback
import analyzer
import archive
import downloader
from issue import Issues
from issueGetter import getIssues
import sys
import logging
import argparse
import issueGetter
from datetime import datetime, time, date
import os

# default parameters
jiraUser = '<default>'
jiraPassword = '<default>'

domainUser = '<default>'
domainPassword = '<default>'

logFilesFilter = ['TGS*.log', 'TAM*.log']
outputDir = r'.'


class Arguments:
    pass

def initLogger(Arguments):
    logging.getLogger().setLevel(logging.DEBUG)

    fh = logging.FileHandler(os.path.join(Arguments.outputDir, datetime.today().strftime('%Y_%m_%d-%H_%M_%S.log')))
    fh.setFormatter(MaskingFormatter(
        logging.Formatter('%(asctime)s:%(levelname)s:%(filename)s:\t%(message)s', '%H:%M:%S'),
        [Arguments.jiraPassword, Arguments.domainPassword]))
    logging.getLogger().addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG if Arguments.verbose else logging.INFO)
    ch.setFormatter(MaskingFormatter(
        logging.Formatter('%(asctime)s:%(levelname)s:\t%(message)s', '%H:%M:%S'),
        [Arguments.jiraPassword, Arguments.domainPassword]))
    logging.getLogger().addHandler(ch)

def prepareOutputDir(outputDir):
    todayDateStr = datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    outputDir = os.path.join(outputDir, todayDateStr)
    os.makedirs(outputDir)
    return outputDir

def prepareArguments():
    parser = argparse.ArgumentParser(description='Telco duty logs helper')
    parser.add_argument('-i', '--issues', nargs='*', help='issues list')
    parser.add_argument('-d', '--downloads', nargs='*', help='filename or [machine date [time]]')
    parser.add_argument('-a', '--analyze', nargs='*', help='zip file name or path')
    parser.add_argument('-ju', '--jiraUser', help='jira username', default=jiraUser)
    parser.add_argument('-jp', '--jiraPassword', help='jira password', default=jiraPassword)
    parser.add_argument('-du', '--domainUser', help='Domain username', default=domainUser)
    parser.add_argument('-dp', '--domainPassword', help='Domain password', default=domainPassword)
    parser.add_argument('-o', '--outputDir', help='where to output', default=outputDir)
    parser.add_argument('-s', '--logFilesFilter', help='Log types to process', default=logFilesFilter)
    parser.add_argument('-v', '--verbose', help='Be verbose to console', action='store_true', default=False)
    parser.parse_args(namespace=Arguments)
    return Arguments

def main():
    issues = Issues()
    try:
        Arguments = prepareArguments()
        Arguments.outputDir = prepareOutputDir(Arguments.outputDir)
        initLogger(Arguments)
        logging.info('Outputting to {0}'.format(Arguments.outputDir))
        if Arguments.issues is not None:
            getIssues(Arguments.issues, Arguments.jiraUser, Arguments.jiraPassword, issues.appender())

        if Arguments.downloads is not None:
            issues.extend(issueGetter.parseIssues(Arguments.downloads))
            issues.setDownloader(lambda issue: downloader.download(issue, Arguments.outputDir, Arguments.domainUser, Arguments.domainPassword))

        if Arguments.analyze is not None:
            issues.extend(issueGetter.parseIssues(Arguments.analyze))
            issues.setUnpacker(lambda issue: archive.unpack(issue, Arguments))
            issues.setAnalyser(lambda issue: analyzer.Analyzer().analyze(issue, Arguments))

        issues.process(Arguments)

        #self.packResults(outputDir)
    except Exception as e:
        logging.error("Fatal error: " + str(e))
        logging.debug('Traceback', exc_info=sys.exc_info())
    except (KeyboardInterrupt):
        logging.error("Program terminataion was requested")
        logging.debug('Traceback', exc_info=sys.exc_info())
    finally:
        logging.info(issues.report())

if __name__ == '__main__':
    main()