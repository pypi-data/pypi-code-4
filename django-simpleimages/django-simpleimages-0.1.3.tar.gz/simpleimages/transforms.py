from StringIO import StringIO

from PIL import Image

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files import File


def scale(height=None, width=None):
    def scale_image_function(django_file):
        pil_image = pil_image_from_django_file(django_file)
        max_height = height or pil_image.size[0]
        max_width = width or pil_image.size[1]
        dimensions = (max_height, max_width)
        transformed_pil_image = pil_image.copy()
        transformed_pil_image.thumbnail(dimensions, Image.ANTIALIAS)
        tranformed_django_file = django_file_from_pil_image(
            transformed_pil_image,
            django_file.name
        )
        return tranformed_django_file
    return scale_image_function


def pil_image_from_django_file(django_file):
    if not isinstance(django_file, File):
        raise TypeError(
            'image is a {0}, not a django File'.format(type(django_file))
        )
    if not django_file.file:
        raise ValueError(
            'the django file has no file saved to it.'
        )
    django_file.open()
    return Image.open(django_file.file)


def django_file_from_pil_image(transformed_pil_image, file_name):
    if not isinstance(transformed_pil_image, Image.Image):
        raise TypeError(
            'image is a {0}, not a PIL Image'.format(type(transformed_pil_image))
        )
    temp_io = StringIO()
    transformed_pil_image.save(temp_io, format='JPEG')
    temp_io.seek(0)
    django_file = InMemoryUploadedFile(
        file=temp_io,
        field_name=None,
        name=file_name,
        content_type='image/jpeg',
        size=temp_io.len,
        charset=None,
    )
    return django_file
