#coding=utf8
from OFS.Image import File
from Products.ATContentTypes.content.file import ATFile
from Products.validation.config import validation
from StringIO import StringIO
from prdg.plone.util.validators import FileExtensionValidator
import transaction
import unittest
from .base import BaseTestCase


ALLOWED_EXTENSIONS = ('.txt', '.log')


class FileExtensionValidatorTestCase(BaseTestCase):
    """Mix unit testing and functional testing."""

    def setUp(self):
        BaseTestCase.setUp(self)

        # For unit tests.
        self.validator = FileExtensionValidator(ALLOWED_EXTENSIONS)
        self.sample_file = File(
            'ofs_file_id',
            'ofs_file_title',
            'File contents.'
        )
        self.sample_file.filename = 'ofs_file_filename'

        # For functional tests.
        validation.register(self.validator)
        ATFile.schema['file'].validators.append(self.validator.name)

        transaction.commit()

        self.login_browser()

    def test_validator_code(self):
        """Test the validator without using the browser (unit test)."""
        self.validate(ALLOWED_EXTENSIONS[0], True)
        self.validate(ALLOWED_EXTENSIONS[1].upper(), True)
        self.validate(ALLOWED_EXTENSIONS[0] + 'z', False)
        self.validate('', False)
        self.validate('.zzz' + ALLOWED_EXTENSIONS[0], True)
        self.validate(ALLOWED_EXTENSIONS[0] + '.zzz', False)

    def validate(self, extension, is_valid):
        """is_valid must be bool."""
        self.sample_file.filename = 'some_file_name' + extension
        result = self.validator(self.sample_file)

        self.failUnless(
            result,
            'Validators can return only True or an error string. '
                'Return value was: %s' % result
        )

        if is_valid:
            self.failUnless(result is True)
        else:
            self.failUnless(self.validator.error_msg in result)

    def create_file_functional(self, file_extension):
        """Create a file using the browser (for functional tests)."""
        self.browser.open(self.portal_url + '/createObject?type_name=File')
        self.browser.getControl(name='title').value = 'title'
        ctrl = self.browser.getControl(name='file_file')
        filename = 'sample_filename' + file_extension
        ctrl.filename = filename
        ctrl.value = StringIO('data')

        self.browser.getControl(name='form.button.save').click()

        return filename

    def test_functional_fail(self):
        """Functional test."""
        self.create_file_functional(ALLOWED_EXTENSIONS[0] + 'z')
        self.dump_browser_contents()
        self.failUnless(self.validator.error_msg in self.browser.contents)

    def test_functional_success(self):
        """Functional test."""
        filename = self.create_file_functional(ALLOWED_EXTENSIONS[0])
        self.failIf(self.validator.error_msg in self.browser.contents)
        self.failUnless(filename in self.browser.contents)

    def test_error_msg(self):
        # Check if default error msg is used if a custom one is not provided.
        validator = FileExtensionValidator(ALLOWED_EXTENSIONS)
        result = validator(self.sample_file)
        self.failUnless(FileExtensionValidator.error_msg in result)

        # Check if a custom msg is used.
        custom_msg = 'zzzzz'
        validator = FileExtensionValidator(ALLOWED_EXTENSIONS, custom_msg)
        result = validator(self.sample_file)
        self.failUnless(custom_msg in result)

        # Changing the custom message after instantiation.
        custom_msg = 'yyyyyy'
        validator.error_msg = custom_msg
        result = validator(self.sample_file)
        self.failUnless(custom_msg in result)





def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FileExtensionValidatorTestCase))
    return suite
