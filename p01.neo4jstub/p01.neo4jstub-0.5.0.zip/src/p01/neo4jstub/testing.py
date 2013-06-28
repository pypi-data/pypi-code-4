###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################

__docformat__ = "reStructuredText"

import os
import os.path
import zipfile

import shutil
import fnmatch
import time
import tempfile
import urllib
import socket
import subprocess
import setuptools.archive_util

VERSION = '1.8.1'

SERVICE_NAME = "p01_neo4jstub_testing"


def doRemoveTree(src, sleep=5, retry=0):
    while retry <= 3:
        retry += 1
        try:
            if os.path.exists(src):
                shutil.rmtree(src)
        except Exception, e: # WindowsError, OSError?, just catch anything
            # this was to early just try again
            time.sleep(sleep)
            doRemoveTree(src, sleep, retry)
        # break while if everything is fine
        break


# helper for zip and unzip data for simpler sample data setup
def zipFolder(folderPath, zipPath, topLevel=False):
    """Zip a given folder to a zip file, topLevel stores top elvel folder too"""
    # remove existing zip file
    if os.path.exists(zipPath):
        os.remove(zipPath)
    zip = zipfile.ZipFile(zipPath, 'w', zipfile.ZIP_DEFLATED)
    path = os.path.normpath(folderPath)
    # os.walk visits every subdirectory, returning a 3-tuple of directory name,
    # subdirectories in it, and filenames in it
    for dirPath, dirNames, fileNames in os.walk(path):
        # walk over every filename
        for file in fileNames:
            # ignore hidden and lock files
            if not (file.startswith('.') or file.endswith('.lock')):
                if topLevel:
                    fPath = os.path.join(dirPath, file)
                    relPath = os.path.join(dirPath, file)[len(path)+len(os.sep):]
                    arcName = os.path.join(os.path.basename(path), relPath)
                    zip.write(fPath, arcName)
                else:
                    fPath = os.path.join(dirPath, file)
                    relPath = os.path.join(dirPath[len(path):], file)
                    zip.write(fPath, relPath) 
    zip.close()
    return None


def unZipFile(zipPath, target):
    # If the output location does not yet exist, create it
    if not os.path.isdir(target):
        os.makedirs(target)    
    zip = zipfile.ZipFile(zipPath, 'r')
    for each in zip.namelist():
        # check to see if the item was written to the zip file with an
        # archive name that includes a parent directory. If it does, create
        # the parent folder in the output workspace and then write the file,
        # otherwise, just write the file to the workspace.
        if not each.endswith('/'): 
            root, name = os.path.split(each)
            directory = os.path.normpath(os.path.join(target, root))
            if not os.path.isdir(directory):
                os.makedirs(directory)
            file(os.path.join(directory, name), 'wb').write(zip.read(each))
    zip.close()


# support missing ignore pattern in py25
def ignore_patterns(*patterns):
    """Function that can be used as copytree() ignore parameter"""
    def _ignore_patterns(path, names):
        ignored_names = []
        for pattern in patterns:
            ignored_names.extend(fnmatch.filter(names, pattern))
        return set(ignored_names)
    return _ignore_patterns


def copytree(src, dst, ignore=None):
    """Recursively copy a directory tree using copy2()"""
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    os.makedirs(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                copytree(srcname, dstname, ignore)
            else:
                shutil.copy2(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except (IOError, os.error), why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error, err:
            errors.extend(err.args[0])
    try:
        shutil.copystat(src, dst)
    except OSError, why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise shutil.Error, errors


def startNeo4jServer(sandBoxDir, neo4jSource=None, dataDir=None, confSource=None,
    dataSource=None, sleep=10, sleepService=6, sleepCopy=3, downloadURL=None,
    version=VERSION,
    confSourceCopyTreeIgnorePatterns='*.svn',
    dataSourceCopyTreeIgnorePatterns='*.svn'):
    """Start the ne04j test server."""

    # stop neo4j service (if running)
    cmd = 'sc stop %s' % SERVICE_NAME
    try:
        subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE,
            shell=False).wait()
    except Exception, e:
        pass
    time.sleep(sleepService)

    if not os.path.exists(sandBoxDir):
        # create server location
        os.mkdir(sandBoxDir)

    # setup data dir
    if dataDir is None:
        data = os.path.join(sandBoxDir, 'data')
    else:
        data = dataDir

    # download and install a server
    names = os.listdir(sandBoxDir)
    if not 'lib' in names and not 'bin' in names:
        if neo4jSource is not None:
            # install neo4j based on given source folder or file
            if os.path.isdir(neo4jSource):
                if os.name == 'nt':
                    # windows
                    fName = 'neo4j-community-%s-windows.zip' % version
                else:
                    # non windows
                    fName = 'neo4j-community-%s-unix.tar.gz' % version
                neo4jSourceFile = os.path.join(neo4jSource, fName)
            else:
                neo4jSourceFile = neo4jSource

        else:
            # download neo4j resource if a downloadURL is given
            if downloadURL is None:
                # windows
                base = 'http://dist.neo4j.org/neo4j-community-%s' % version
                if os.name == 'nt':
                    url = '%s-windows.zip' % base
                # non windows
                else:
                    url = '%s-unix.tar.gz' % base
            else:
                url = downloadURL
    
            handle, neo4jSourceFile = tempfile.mkstemp(prefix='p01-neo4j-download')
            urllib.urlretrieve(url, neo4jSourceFile)

        if not os.path.exists(neo4jSourceFile):
            raise Exception("Missing neo4j source files at: %s" % neo4jSourceFile)

        # install a server based on neo4j source file
        tmpDir = tempfile.mkdtemp('p01-ne4jstub-tmp')
        setuptools.archive_util.unpack_archive(neo4jSourceFile, tmpDir)
        topLevelDir = os.path.join(tmpDir, os.listdir(tmpDir)[0])
        for fName in os.listdir(topLevelDir):
            source = os.path.join(topLevelDir, fName)
            dest = os.path.join(sandBoxDir, fName)
            shutil.move(source, dest)

    # first remove the original data folder, we need an empty setup
    if os.path.exists(data):
        doRemoveTree(data)

    # re-use predefined neo4j data for simpler testing
    if dataSource is not None and os.path.exists(dataSource):
        if dataSource.endswith('.zip'):
            # extract zip file to dataDir
            try:
                unZipFile(dataSource, data)
            except Exception, e: # WindowsError?, just catch anything
                # this was to early just try again
                time.sleep(sleepCopy)
                if os.path.exists(data):
                    doRemoveTree(data)
                time.sleep(sleepCopy)
                unZipFile(dataSource, data)
        else:
            ignore = None
            if dataSourceCopyTreeIgnorePatterns is not None:
                ignore = ignore_patterns(dataSourceCopyTreeIgnorePatterns)
            try:
                copytree(dataSource, data, ignore=ignore)
            except: # WindowsError?, just catch anything
                # this was to early just try again
                time.sleep(sleepCopy)
                if os.path.exists(data):
                    doRemoveTree(data)
                time.sleep(sleepCopy)
                copytree(dataSource, data, ignore=ignore)

    # setup conf dir path
    conf = os.path.join(sandBoxDir, 'conf')

    # move the given conf source to our config location
    if confSource is not None and os.path.exists(confSource):
        if os.path.exists(conf):
            doRemoveTree(conf)
        ignore = None
        if confSourceCopyTreeIgnorePatterns is not None:
            ignore = ignore_patterns(confSourceCopyTreeIgnorePatterns)
        copytree(confSource, conf, ignore=ignore)

    # on windows, we will install a serivce and use them for start neo4j
    if os.name == 'nt':
        # setup java options and friends
        JAVA_HOME = os.environ['JAVA_HOME']
        JAVA_BIN = os.path.join(JAVA_HOME, 'bin', 'java')
        if os.name == 'nt':
            sep = ';'
        else:
            sep = ':' #linux does not like ;
    
        CLASSPATH = "-DserverClasspath=lib/*.jar;system/lib/*.jar;plugins/*.jar;system/coordinator/lib/*.jar"
        wrapperJarFilename = os.path.join(sandBoxDir, 'bin', 'windows-service-wrapper-4.jar')
    
        # service start command (aka binPath)
        cmd = [
            JAVA_BIN,
            "-DworkingDir=%s" % sandBoxDir,
            "-DconfigFile=conf/neo4j-wrapper.conf",
            "-Djava.util.logging.config.file=conf/windows-wrapper-logging.properties",
            CLASSPATH,
            "-DserverMainClass=org.neo4j.server.Bootstrapper",
            "-jar", wrapperJarFilename,
            SERVICE_NAME
            ]
        binPath = ' '.join(cmd)
    
        # install service
        cmd = 'sc create %s binpath= "%s" start= demand' % (SERVICE_NAME, binPath)
        try:
            subprocess.Popen(cmd, stderr=subprocess.STDOUT,
                stdout=subprocess.PIPE, shell=False).wait()
        except Exception, e:
            pass
            # ignore installed service
    
        time.sleep(sleepService)
    
        # start service
        cmd = [
            "sc",
            "start",
            SERVICE_NAME,
            ]
        # and start the neo4j stub server
        try:
            subprocess.Popen("sc start %s" % SERVICE_NAME,
                stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=False).wait()
        except Exception, e:
            raise Exception("Subprocess error: %s" % e)

    else:
        # unix is not tested yet
        binPath = os.path.join(sandBoxDir, 'bin', 'neo4j')
        try:
            subprocess.Popen("%s start" % binPath, shell=False)
        except Exception, e:
            raise Exception("Subprocess error: %s" % e)

    # give it the extra wait time
    time.sleep(sleep)


def stopNeo4jServer(sandBoxDir, sleep=3):
    """Stop neo4j server"""
    # give it the extra wait time
    time.sleep(sleep)
    if os.name == 'nt':
        # stop neo4j service
        cmd = 'sc stop %s' % SERVICE_NAME
        try:
            subprocess.Popen(cmd, stderr=subprocess.STDOUT,
                stdout=subprocess.PIPE, shell=False).wait()
        except Exception, e:
            pass
    
        time.sleep(sleep)
    
        # remove neo4j service
        cmd = 'sc delete %s' % SERVICE_NAME
        try:
            subprocess.Popen(cmd, stderr=subprocess.STDOUT,
                stdout=subprocess.PIPE, shell=False).wait()
        except Exception, e:
            raise Exception("Subprocess error: %s" % e)
    
    else:
        # unix is not tested yet
        binPath = os.path.join(sandBoxDir, 'bin', 'neo4j')
        try:
            subprocess.Popen("%s stop" % binPath, stderr=subprocess.STDOUT,
                stdout=subprocess.PIPE, shell=False).wait()
        except Exception, e:
            raise Exception("Subprocess error: %s" % e)

    # give it the extra wait time
    time.sleep(sleep)


###############################################################################
#
# Doctest setup
#
###############################################################################

def doctestSetUp(test):
    # setup neo4j server
    here = os.path.dirname(__file__)
    sandbox = os.path.join(here, 'sandbox')
    confSource = os.path.join(here, 'conf')
    startNeo4jServer(sandbox, confSource=confSource)


def doctestTearDown(test):
    # tear down neo4j server
    here = os.path.dirname(__file__)
    sandbox = os.path.join(here, 'sandbox')
    stopNeo4jServer(sandbox)
