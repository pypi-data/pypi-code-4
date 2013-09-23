from django.http import HttpResponse
from django.shortcuts import get_object_or_404


def download_attachment(request, slug):
    from ella_attachments.models import Attachment
    import mimetypes
    attachment = get_object_or_404(Attachment, slug=slug)

    # Create the HttpResponse object with the appropriate PDF headers.
    if attachment.type is None:
        mimetype = mimetypes.guess_type(attachment.attachment.url)[0]
    else:
        mimetype = attachment.type.mimetype
    response = HttpResponse(mimetype=mimetype)
    response['Content-Disposition'] = 'attachment; filename="%s"' % attachment.filename

    response.write(attachment.attachment.read())
    return response
