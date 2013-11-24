#Robot Framework FTP Library
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This library provides functionality of FTP client.

Version 1.2 released on 24th of November 2013.

What's new in release 1.2:
- updated naming for puprpose of pypi.

FTP communication provided by ftplib.py. While developing, following versions
were used:
- robotframework-2.8.1
- robotframework-ride-1.2.1
- python-2.7.5

Tested on:
- Windows 7
- Debian 6
- ProFTPD

Author: Marcin Kowalczyk

Website: http://sourceforge.net/projects/rf-ftp-py/

Installation:
- run command: pip install robotframework-ftplibrary

OR
- download, unzip and run command: python setup.py install

OR
- download, unzip and copy FtpLibrary.py file to a directory pointed by
    PYTHONPATH (for example ...\Python27\lib\site-packages).

The simplest example (connect, change working dir, print working dir, close):
 | ftp connect | 192.168.1.10 | mylogin | mypassword |
 | cwd | /home/myname/tmp/testdir |
 | pwd |
 | ftp close |
"""

import ftplib
import os
import socket
rfftp = None

def ftp_connect(host,user='anonymous',password='anonymous@',port=21,timeout=30):
    """
    Constructs FTP object, opens a connection and login.
    Call this function before any other (otherwise raises exception).
    Returns server output.
    Parameters:
        - host - server host address
        - user(optional) - FTP user name. If not given, 'anonymous' is used.
        - password(optional) - FTP password. If not given, 'anonymous@' is used.
        - port(optional) - TCP port. By default 21.
        - timeout(optional) - timeout in seconds. By default 30.
    Examples:
    | ftp connect | 192.168.1.10 | mylogin | mypassword |  |  |
    | ftp connect | 192.168.1.10 |  |  |  |  |
    | ftp connect | 192.168.1.10 | mylogin | mypassword | 29 | 20 |
    | ftp connect | 192.168.1.10 | mylogin | mypassword | 29 |  |
    | ftp connect | 192.168.1.10 | mylogin | mypassword | timeout=20 |  |
    | ftp connect | 192.168.1.10 | port=29 | timeout=20 |  |  |
    """
    global rfftp
    outputMsg = ""
    if __checkFtpStatus(True):
        rfftp = RF_Ftp()
        outputMsg = rfftp.connectAndLogin(host=host,user=user,password=password,port=port,timeout=timeout)
        print("Response: " + outputMsg)
        return outputMsg

def get_welcome():
    """
    Returns wlecome message of FTP server.
    """
    global rfftp
    outputMsg = ""
    if __checkFtpStatus():
        outputMsg = rfftp.getWelcome()
        print("Response: " + outputMsg)
        return outputMsg

def pwd():
    """
    Returns the pathname of the current directory on the server.
    """
    global rfftp
    outputMsg = ""
    if __checkFtpStatus():
        outputMsg = rfftp.pwd()
        print("Response: " + outputMsg)
        return outputMsg

def cwd(directory):
    """
    Changes working directory and returns server output. Parameters:
        - directory - a path to which working dir should be changed.
    Example:
    | cwd | /home/myname/tmp/testdir |
    """
    global rfftp
    outputMsg = ""
    if __checkFtpStatus():
        outputMsg = rfftp.cwd(directory)
        print("Response: " + outputMsg)
        return outputMsg

def dir():
    """
    Returns list of contents of current directory.
    """
    global rfftp
    outputMsg = ""
    if __checkFtpStatus():
        dirList = rfftp.dir()
        for d in dirList:
            outputMsg += d + "\n"
        print(outputMsg)
        return dirList

def mkd(newDirName):
    """
    Creates new directory on FTP server. Returns new directory path.
    Parameters:
    - newDirName - name of a new directory
    """
    global rfftp
    outputMsg = ""
    if __checkFtpStatus():
        outputMsg = rfftp.mkd(newDirName)
        print("Response: " + outputMsg)
        return outputMsg

def rmd(directory):
    """
    Deletes directory from FTP server. Returns server output.
    Parameters:
    - directory - path to a directory to be deleted
    """
    global rfftp
    outputMsg = ""
    if __checkFtpStatus():
        outputMsg = rfftp.rmd(directory)
        print("Response: " + outputMsg)
        return outputMsg

def upload_file(localFileName,remoteFileName=None):
    """
    Sends file from local drive to current directory on FTP server in binary mode.
    Returns server output.
    Parameters:
    - localFileName - file name or path to a file on a local drive.
    - remoteFileName (optional) - a name or path containing name under which file should be saved.
    If remoteFileName agument is not given, local name will be used.
    Examples:
    | upload file | x.txt |  |
    | upload file | D:/rfftppy/y.txt |  |
    | upload file | u.txt | uu.txt |
    | upload file | D:/rfftppy/z.txt | zz.txt |
    | upload file | D:\\rfftppy\\v.txt |  |
    """
    global rfftp
    outputMsg = ""
    if __checkFtpStatus():
        outputMsg = rfftp.storbinary(localFileName,remoteFileName)
        print("Response: " + outputMsg)
        return outputMsg

def download_file(remoteFilename,localFilePath=None):
    """
    Downloads file from current directory on FTP server in binary mode. If
    localFilePath is not given, file is saved in current local directory (by
    default folder containing robot framework project file) with the same name
    as source file. Returns server output
    Parameters:
    - remoteFileName - file name on FTP server
    - localFilePath (optional) - local file name or path where remote file should be saved.
    localFilePath variable can have following meanings:
    1. file name (will be saved in current default directory);
    2. full path (dir + file name)
    3. dir path (original file name will be added)
    Examples:
    | download file | a.txt |  |
    | download file | a.txt | b.txt |
    | download file | a.txt | D:/rfftppy/tmp |
    | download file | a.txt | D:/rfftppy/tmp/b.txt |
    | download file | a.txt | D:\\rfftppy\\tmp\\c.txt |
    """
    global rfftp
    outputMsg = ""
    if __checkFtpStatus():
        outputMsg = rfftp.retrbinary(remoteFilename,localFilePath)
        print("Response: " + outputMsg)
        return outputMsg

def size(fileToCheck):
    """
    Checks size of a file on FTP server. Returns size of a file in bytes (integer).
    Parameters:
    - fileToCheck - file name or path to a file on FTP server
    Example:
    | ${file1size} = | size | /home/myname/tmp/uu.txt |
    | Should Be Equal As Numbers | ${file1size} | 31 |
    """
    global rfftp
    sizeOfFile = 0
    outputMsg = ""
    if __checkFtpStatus():
        sizeOfFile = rfftp.size(fileToCheck)
        print("Response: " + str(sizeOfFile))
        return sizeOfFile

def rename(targetFile,newName):
    """
    Renames (actually moves) file on FTP server. Returns server output.
    Parameters:
    - targetFile - name of a file or path to a file to be renamed
    - newName - new name or new path
    Example:
    | rename | tmp/z.txt | /home/myname/tmp/testdir/z.txt |
    """
    global rfftp
    outputMsg = ""
    if __checkFtpStatus():
        outputMsg = rfftp.rename(targetFile,newName)
        print("Response: " + outputMsg)
        return outputMsg

def delete(targetFile):
    """
    Deletes file on FTP server. Returns server output.
    Parameters:
    - targetFile - file path to be deleted
    """
    global rfftp
    outputMsg = ""
    if __checkFtpStatus():
        outputMsg = rfftp.delete(targetFile)
        print("Response: " + outputMsg)
        return outputMsg

def send_cmd(command):
    """
    Sends any command to FTP server. Returns server output.
    Parameters:
    - command - any valid command to be sent (invalid will result in exception).
    Example:
    | send cmd | HELP |
    """
    global rfftp
    outputMsg = ""
    if __checkFtpStatus():
        outputMsg = rfftp.sendCmd(command)
        print("Response: " + outputMsg)
        return outputMsg

def ftp_close():
    """
    Closes FTP connection. Returns None.
    Parameters: None
    """
    global rfftp
    if __checkFtpStatus():
        rfftp.close()
    rfftp = None

def __checkFtpStatus(inverted=False):
    global rfftp
    if inverted:
        if not isinstance(rfftp,RF_Ftp):
            return True
        else:
            raise FtpLibraryError("Active FTP connection already exists.")
    else:
        if isinstance(rfftp,RF_Ftp):
            if(rfftp.checkConnectionStatus()):
                return True
            else:
                errorMsg = "FTP connection was not established properly."
                rfftp = None
                raise FtpLibraryError(errorMsg)
        else:
            errorMsg = "No active FTP connection exists."
            errorMsg += " One must be created before calling this method."
            raise FtpLibraryError(errorMsg)

class RF_Ftp(object):
    def __init__(self):
        self.f = ftplib.FTP()

    def connectAndLogin(self, **kwargs):
        outputMsg = ""
        host = ""
        port = -1
        timeout = -1
        user = ""
        password = ""
        if 'host' in kwargs:
            host = kwargs['host']
        if 'port' in kwargs:
            port = kwargs['port']
        if 'timeout' in kwargs:
            timeout = kwargs['timeout']
        if 'user' in kwargs:
            user = kwargs['user']
        if 'password' in kwargs:
            password = kwargs['password']
        self.connectionStatus = False
        try:
            timeout = int(timeout)
            port = int(port)
            if host!= "" and port>0 and timeout>0:
                outputMsg += self.f.connect(host,port,timeout)
            elif host!= "" and port>0:
                outputMsg += self.f.connect(host,port)
            elif host!= "" and timeout>0:
                outputMsg += self.f.connect(host,21,timeout)
            else:
                outputMsg += self.f.connect(host)
            outputMsg += self.f.login(user,password)
        except socket.error as se:
            raise FtpLibraryError('Socket error exception occured.')
        except ftplib.all_errors as e:
            raise FtpLibraryError(str(e))
        self.connectionStatus = True
        return outputMsg

    def checkConnectionStatus(self):
        return self.connectionStatus

    def getWelcome(self):
        outputMsg = ""
        try:
            outputMsg += self.f.getwelcome()
        except ftplib.all_errors as e:
            raise FtpLibraryError(str(e))
        return outputMsg

    def pwd(self):
        outputMsg = ""
        try:
            outputMsg += self.f.pwd()
        except ftplib.all_errors as e:
            raise FtpLibraryError(str(e))
        return outputMsg

    def dir(self):
        dirList = []
        try:
            self.f.dir(dirList.append)
        except ftplib.all_errors as e:
            raise FtpLibraryError(str(e))
        return dirList

    def cwd(self,directory):
        outputMsg = ""
        try:
            outputMsg += self.f.cwd(directory)
        except ftplib.all_errors as e:
            raise FtpLibraryError(str(e))
        return outputMsg

    def mkd(self,newDirName):
        outputMsg = ""
        try:
            outputMsg += self.f.mkd(newDirName)
        except ftplib.all_errors as e:
            raise FtpLibraryError(str(e))
        return outputMsg

    def rmd(self,directory):
        outputMsg = ""
        try:
            outputMsg += self.f.rmd(directory)
        except ftplib.all_errors as e:
            raise FtpLibraryError(str(e))
        return outputMsg

    def retrbinary(self,ftpFileName,localFileName=None):
        outputMsg = ""
        localPath = ""
        if localFileName==None:
            localPath = ftpFileName
        else:
            localPath = os.path.normpath(localFileName)
            if os.path.isdir(localPath):
                localPath = os.path.join(localPath,ftpFileName)
        try:
            localFile = open(localPath, 'wb')
            outputMsg += self.f.retrbinary("RETR " + ftpFileName, localFile.write)
        except ftplib.all_errors as e:
            raise FtpLibraryError(str(e))
        return outputMsg

    def storbinary(self,localFileName,ftpFileName=None):
        outputMsg = ""
        remoteFileName = ""
        localFilePath = os.path.normpath(localFileName)
        if not os.path.isfile(localFilePath):
            raise FtpLibraryError("Valid file path should be provided.")
        else:
            if ftpFileName==None:
                fileTuple = os.path.split(localFileName)
                if len(fileTuple)==2:
                    remoteFileName = fileTuple[1]
                else:
                    remoteFileName = 'defaultFileName'
            else:
                remoteFileName = ftpFileName
            try:
                outputMsg += self.f.storbinary("STOR " + remoteFileName, open(localFilePath, "rb"))
            except ftplib.all_errors as e:
               raise FtpLibraryError(str(e))
        return outputMsg

    def size(self,ftpFileName):
        sizeOfFile = -1
        try:
            sizeOfFile = self.f.size(ftpFileName)
        except ftplib.all_errors as e:
            raise FtpLibraryError(str(e))
        return sizeOfFile

    def rename(self, srcFile, dstFile):
        outputMsg = ""
        try:
            outputMsg += self.f.rename(srcFile,dstFile)
        except ftplib.all_errors as e:
            raise FtpLibraryError(str(e))
        return outputMsg

    def delete(self,srcFile):
        outputMsg = ""
        try:
            outputMsg += self.f.delete(srcFile)
        except ftplib.all_errors as e:
            raise FtpLibraryError(str(e))
        return outputMsg

    def sendCmd(self,cmd):
        outputMsg = ""
        try:
            outputMsg += self.f.sendcmd(cmd)
        except ftplib.all_errors as e:
            raise FtpLibraryError(str(e))
        return outputMsg

    def close(self):
        try:
            self.f.close()
        except ftplib.all_errors as e:
            raise FtpLibraryError(str(e))

class FtpLibraryError(Exception):
    def __init__(self,msg):
        self.msg = msg

    def __str__(self):
        return self.msg

def __main():
    runTest = False
    mainMsg = "FtpLibrary is a functionality of FTP client for Robot Framework."
    mainMsg += " For instruction on how to use please visit "
    mainMsg += "http://sourceforge.net/projects/rf-ftp-py/"
    print(mainMsg)
    if runTest:
        whichConnect = 6
        if(whichConnect==1):
            ftp_connect('192.168.1.53','marcin','marcin')
        elif(whichConnect==2):
            ftp_connect('192.168.1.53')
        elif(whichConnect==3):
            ftp_connect('192.168.1.53','marcin','marcin',21,20)
        elif(whichConnect==4):
            ftp_connect('192.168.1.53','marcin','marcin',21)
        elif(whichConnect==5):
            ftp_connect('192.168.1.53','marcin','marcin',timeout=15)
        elif(whichConnect==6):
            ftp_connect('192.168.1.53','marcin','marcin',timeout=25,port=21)
        get_welcome()
        send_cmd('HELP')
        mkd('testDir8')
        cwd('testDir8')
        if pwd()=='/home/marcin/testDir8':
            print('OK')
        else:
            print('FAIL')
        upload_file('file.txt','ftpfile.txt')
        rename('ftpfile.txt','newfile.txt')
        if size('newfile.txt')==1:
            print('OK')
        else:
            print('FAIL')
        download_file('newfile.txt','filefromftp.txt')
        delete('newfile.txt')
        cwd('..')
        pwd()
        rmd('testDir8')
        dir()
        ftp_close()

if __name__ == '__main__':
    __main()
