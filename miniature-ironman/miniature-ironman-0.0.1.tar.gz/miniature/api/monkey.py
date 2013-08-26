from django.http import HttpResponse
from tastypie import resources

__author__ = 'ir4y'


def build_content_type(format, encoding='utf-8'):
    """
    Appends character encoding to the provided format if not already present.
    """
    if 'charset' in format:
        return format

    return "%s; charset=%s" % (format, encoding)


def create_response(self, request, data, response_class=HttpResponse,
                    **response_kwargs):
    desired_format = self.determine_format(request)
    serialized = self.serialize(request, data, desired_format)
    return response_class(content=serialized,
                          content_type=build_content_type(desired_format),
                          **response_kwargs)

setattr(resources.Resource, 'create_response', create_response)
