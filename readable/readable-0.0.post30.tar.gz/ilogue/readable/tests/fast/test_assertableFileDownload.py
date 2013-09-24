import unittest
from mock import Mock
from ilogue.readable import assertionMethod, setupMethod
from shortuuid import uuid as shortuuid
import os


class AssertableResponseTestCase(unittest.TestCase):

    def setUp(self):
        self.createdTempFiles = []

    def tearDown(self):
        for tempFile in self.createdTempFiles:
            if os.path.exists(tempFile):
                os.remove(tempFile)

    def test_isBinary(self):
        from ilogue.readable.AssertableFileDownload import AssertableFileDownload
        imageDownload = AssertableFileDownload(
            self.setupResponseWithContentType('image/png'),
            Mock())
        binaryDownload = AssertableFileDownload(
            self.setupResponseWithContentType('application/octet-stream'),
            Mock())
        assertionMethod(imageDownload.isBinary).fails()
        assertionMethod(binaryDownload.isBinary).doesNotFail()

    def test_hasMinimumSize(self):
        from ilogue.readable.AssertableFileDownload import AssertableFileDownload
        download = AssertableFileDownload(
            Mock(), self.setupFileWithSize(200))
        assertionMethod(download.hasMinimumSize).failsIfPassed(300)
        assertionMethod(download.hasMinimumSize).doesNotFailIfPassed(100)

    def test_hasFilename(self):
        from ilogue.readable.AssertableFileDownload import AssertableFileDownload
        downloadWithoutFilename = AssertableFileDownload(
            self.setupResponseWithFilename(None),
            Mock())
        downloadWithFilename = AssertableFileDownload(
            self.setupResponseWithFilename('file.name'),
            Mock())
        assertionMethod(
            downloadWithoutFilename.hasFilename).failsIfPassed('anything')
        assertionMethod(
            downloadWithFilename.hasFilename).failsIfPassed('othername')
        assertionMethod(
            downloadWithFilename.hasFilename).doesNotFailIfPassed('file.name')

#resp.info().getheader('Connection')
#os.path.getsize
#header('Content-Disposition: attachment; filename="downloaded.pdf"');

    def setupResponseWithContentType(self, contentType):
        response = Mock()
        infoObject = Mock()
        setupMethod(infoObject.gettype).toReturn(contentType)
        setupMethod(response.info).toReturn(infoObject)
        return response

    def setupResponseWithFilename(self, filename):
        if filename is None:
            header = None
        else:
            header = 'Content-Disposition: attachment; filename="{0}"'.format(filename)
        response = Mock()
        infoObject = Mock()
        setupMethod(infoObject.getheader).toReturn(header)
        setupMethod(response.info).toReturn(infoObject)
        return response

    def setupFileWithSize(self, size):
        filename = '/tmp/test_testutils_filedwnl_'+shortuuid()+'.tmp'
        self.createdTempFiles.append(filename)
        f = open(filename, "wb")
        f.write(bytes("\0" * size, 'UTF-8'))
        f.close()
        return filename
