from archetypes.schemaextender.field import ExtensionField
from raptus.multilanguagefields import fields

class StringField(ExtensionField, fields.StringField):
    """ StringField
    """

class LinesField(ExtensionField, fields.LinesField):
    """ LinesField
    """

class TextField(ExtensionField, fields.TextField):
    """ TextField
    """

class FileField(ExtensionField, fields.FileField):
    """ FileField
    """
    
    def getIndexAccessor(self, instance):
        return lambda: self.getIndexable(instance)

class ImageField(ExtensionField, fields.ImageField):
    """ FileField
    """

try:
    class BlobFileField(ExtensionField, fields.BlobFileField):
        """ BlobFileField
        """
    
    class BlobImageField(ExtensionField, fields.BlobImageField):
        """ BlobImageField
        """
except:
    pass