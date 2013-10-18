from datetime import datetime
import subprocess
import logging
import tempfile


__author__ = 'alexey.grachev'
import os
import sys

searchIn = {'sjc':
                (
                    'iad01-c01-utl03.c01.ringcentral.com',
                    ['/mnt/rclogbackup-sjc01-tmp', '/mnt/rclogbackup'],
                    'ssh-rsa 2048 1f:c1:b9:dc:d8:cb:8f:73:bb:cd:f9:a2:c4:6f:40:c8'
                ),
            'iad':
                (
                    'sjc01-c01-utl03.c01.ringcentral.com',
                    ['/mnt/rclogbackup-iad01-tmp', '/mnt/rclogbackup'],
                    'ssh-rsa 2048 5a:04:83:08:57:12:84:7b:2a:24:d9:df:8a:18:1f:34'
                )}

winscpCmdLine = r'{path}\WinSCP.com /script={script}'

def whereSearch(machine):
    return searchIn.get(machine[:3].lower())

def getFile(host, key, srcFile, dstFile, user, password):
    winCmdPath = os.path.dirname(__file__)
    fullTmpFileName = os.path.join(os.path.dirname(dstFile), datetime.today().strftime("%Y%m%d%H%M%S"))
    with open(fullTmpFileName, 'w') as tmpFile:
        tmpFile.write("option batch abort\n")
        tmpFile.write("open {0}:{1}@{2} -hostkey=\"{3}\"\n".format(user, password, host, key))
        tmpFile.write("get {0} {1}\n".format(srcFile, dstFile))
        tmpFile.write("exit\n")

    cmd = winscpCmdLine.format(path=winCmdPath, script=fullTmpFileName)
    logging.debug(cmd)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(process.stdout.readline, ''):
        logging.debug('WinSCP: ' + line.strip('\n\r'))
    result = process.wait()
    os.remove(fullTmpFileName)
    if result is not 0:
        raise Exception('WinSCP returned {0}'.format(result))

def download(issue, outputDir, user, password):
    try:
        logging.info("------------------------------Downloading")
        issue.setStatus("Downloading")
        if issue.machine() is None or issue.date() is None:
            raise Exception('issue.machine or issue.date is not set')

        machine = issue.machine().upper()
        eventDate = issue.date().replace('.', '-')
        (host, paths, key) = whereSearch(machine)

        for path in paths:
            srcPath = path + '/' + eventDate
            srcFileName = 'logs_{0}_{1}.zip'.format(eventDate, machine)
            dstFullFileName = os.path.join(outputDir, issue.dest(), srcFileName)
            getFile(host,
                    key,
                    srcPath + '/' + srcFileName,
                    dstFullFileName,
                    user,
                    password)

            issue.setArchive(dstFullFileName)
            issue.setStatus("Downloaded")
            return
    except Exception as e:
        logging.error(str(e))
        logging.debug('Traceback', exc_info=sys.exc_info())
        raise Exception('Failed to download')

