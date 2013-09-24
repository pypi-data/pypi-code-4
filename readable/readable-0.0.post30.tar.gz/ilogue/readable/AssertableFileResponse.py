import os


class AssertableFileResponse(object):
    binaryContentTypes = ['application/octet-stream']
    DISPOHDR = 'Content-Disposition: attachment; filename="{0}"'
    def __init__(self, responseObject, tempLocalFile=None):
        assert responseObject
        #assert tempLocalFile
        self.response = responseObject
        self.cachedFile = tempLocalFile

    def isBinary(self):
        contentType = self.response.info().gettype()
        if not contentType in self.binaryContentTypes:
            raise AssertionError(
                'Binary file download had content-type: '+contentType)
        return self

    def hasFilename(self, expName):
        dispoHeader = self.response.headers['Content-Disposition']
        if dispoHeader is None:
            raise AssertionError(
                'File download did not specify a filename.')
        actName = dispoHeader.split('"')[-2]
        if not actName == expName:
            raise AssertionError(
                ('File download filename was "{0}", not "{1}": '
                    .format(actName,expName)))
        return self

    def hasMinimumSize(self, expMinSize):
        actSize = os.path.getsize(self.cachedFile)
        msg = 'File download size ({0}) less than expected ({1})'
        if actSize <  expMinSize:
            raise AssertionError(msg.format(actSize,expMinSize))
        return self

# Move this stuff to AFD??:

#    def responseToAssertableFileDownload(self, response):
#        filename = '/tmp/test_ploy_filedwnl_'+shortuuid()+'.tmp'
#        self.readResponseToFile(response, filename)
#        return AssertableFileDownload(response,filename)

#    def readResponseToFile(self, response, localFile):
#        CHUNK = 16 * 1024
#        with open(localFile, 'wb') as fp:
#          while True:
#            chunk = response.read(CHUNK)
#            if not chunk: break
#            fp.write(chunk)

