import django.db.models.fields.files
import magic

@property
def mime(self):
    self.open()
    try:
        return magic.from_buffer(self.read(1024), mime=True)
    finally:
        self.close()

django.db.models.fields.files.FieldFile.mime = mime

@property
def typename(self):
    self.open()
    try:
        return magic.from_buffer(self.read(1024))
    finally:
        self.close()

django.db.models.fields.files.FieldFile.typename = typename
