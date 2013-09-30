import json
import magic
import os
from tempfile import mkstemp
import uuid
from shutil import copyfile
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.http import HttpResponse
import logging as log
import mimetypes
from django.conf import settings
from pgcontent.models.attachment import DocumentAttachment, ImageAttachment
from django.core.files import File


class UploadView(View):

    """ View that enables Ajax style upload of attachments """

    def is_image(self, mime_type):

        """ Check whether the mime_type is 'image'-ish """
        try:
            return mime_type.split("/")[0] == "image"
        except:
            return False

    @csrf_exempt
    def post(self, request, *args, **kwargs):

        """ File upload view. If attachment_id is provided in the
        request params, assume it is an edit of an existing
        attachment. """

        temp_file = None
        file_name = None

        attachments = []
        attachment_type = request.REQUEST.get("attachment_type", "document")    

        try:
            attachment_id = int(request.REQUEST.get("attachment_id", None))
        except:
            attachment_id = None

        for filename in request.FILES.keys():

            fd, temp_file = self.create_temp_file(request.FILES[filename])
            file_name = request.FILES[filename].name
            mime_type = request.FILES[filename].content_type or \
                magic.Magic(mime=True).from_file(temp_file) or \
                mimetypes.guess_type(file_name)[0]

            # connect the uploaded file to an Attachment instance
            #
            log.debug("Uploaded file mime type: %s" % mime_type)

            relative_file_name = self.generate_relative_file_path(file_name,
                                                              mime_type,
                                                              attachment_type)

            if attachment_type in ["image", "avatar"]:

                if not self.is_image(mime_type):

                    log.error("Upload is not an image.")

                    response = HttpResponse(
                        json.dumps({'success': False,
                                    'msg': "Upload is not an image"
                                    }))

                    return response

                if attachment_id:
                    attachment = ImageAttachment.objects.get(pk=attachment_id)
                    attachment.original_filename = file_name
                else:
                    attachment = ImageAttachment(
                        mime_type=mime_type,
                        title=file_name,
                        original_filename=file_name
                        )

                if attachment_type == "avatar":
                    path = "avatars/%s" % relative_file_name
                else:
                    path = "images/%s" % relative_file_name

                attachment.image.save(path, File(open(temp_file)))
                attachment.save()
            else:
                store_path = os.path.join("documents", relative_file_name)
            
                self.store(temp_file, store_path)

                if attachment_id:
                    attachment = DocumentAttachment.objects.get(pk=attachment_id)
                    attachment.file = store_path
                    attachment.original_filename=file_name
                else:
                    attachment = DocumentAttachment.objects.create(
                        file=store_path,
                        mime_type=mime_type,
                        title=file_name,
                        original_filename=file_name
                        )
            
                attachment.save()

            attachments.append(attachment)

        # Send back results to the client. Client should 'handle'
        # file_id etc.
        #
        context = {}

        context["attachment_ids"] = [att.id for att in attachments]            

        if self.request.REQUEST.get("edit_type", "") == "field":
            if attachment_type == "image":
                template = "pgcontent/snippets/image.html"
            elif attachment_type == "avatar":
                template = "pgcontent/snippets/avatar.html"
            else:
                template = "pgcontent/snippets/document.html"
        else:
            if attachment_type == "image":
                template = "pgcontent/snippets/imageattachments.html"
            else:
                template = "pgcontent/snippets/documentattachments.html"

        context['html'] = render_to_string(template,
                                           {'attachments': attachments})

        context.update(self.extra_json_context(attachments))

        response = HttpResponse(json.dumps(context), content_type="text/plain")

        return response

    def extra_json_context(self, attachments):

        return {}

    def generate_relative_file_path(self, file_name, mime_type,
                                    attachment_type):

        """ Check on file type, and generate path accordingly """
        
        fn, file_extension = os.path.splitext(file_name)
        
        # Create a random filename, with the proper extension.
        #
        file_id = str(uuid.uuid4())
        file_name = os.path.join(
            file_id[:2],
            "%s%s" % (file_id, file_extension))
        
        return file_name

    def create_temp_file(self, data):

        fd, path = mkstemp()

        block = data.read(1024)
        while block:
            os.write(fd, block)
            block = data.read(1024)

        os.close(fd)
        return fd, path

    def store(self, temp_file, file_name):

        file_name = os.path.join(settings.MEDIA_ROOT, file_name)
        
        if not os.path.exists(os.path.dirname(file_name)):
            os.makedirs(os.path.dirname(file_name))

        copyfile(temp_file, file_name)
        os.unlink(temp_file)
