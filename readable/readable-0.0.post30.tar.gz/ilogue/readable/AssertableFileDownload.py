import os


class AssertableFileDownload(object):
    binaryContentTypes = ['application/octet-stream']
    DISPOHDR = 'Content-Disposition: attachment; filename="{0}"'
    def __init__(self, responseObject, tempLocalFile):
        assert responseObject
        assert tempLocalFile
        self.response = responseObject
        self.cachedFile = tempLocalFile

    def isBinary(self):
        contentType = self.response.info().gettype()
        if not contentType in self.binaryContentTypes:
            raise AssertionError(
                'Binary file download had content-type: '+contentType)
        return self

    def hasFilename(self, expName):
        dispoHeader = self.response.info().getheader('Content-Disposition')
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

