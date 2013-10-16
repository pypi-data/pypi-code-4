#-*- coding: utf-8 -*-
from pyramid_rest.exceptions import BadRequest, ValidationError, Forbidden,\
    ExceptionInterface
from pyramid.view import view_config
from pyramid_rest.config import Config
from pyramid_rest.logger import Logger
import transaction
from pyramid_rest.files.models import Files
from pyramid_rest.security.decorators import AllowToGroups
import re
from pyramid_rest.security.models import Sessions
from pyramid_rest.request import Request
from pyramid.response import Response

UPLOAD_FILENAME_PAT = re.compile("^\w+\.\w+$")


def upload_file(request):
    try:
        file = request.POST["file"]
        FILENAME = file.filename
        if not FILENAME:
            request.response.status_code = 400
            raise BadRequest(info = "No filename")
        
        if not UPLOAD_FILENAME_PAT.search(FILENAME):
            request.response.status_code = 400
            raise BadRequest(info = "Incorrect file name. Must contain only letter symbols and extension.")
        
        with transaction.manager:
            db_sid = Sessions._get(sid = request.cookies.get("SID", -1))
            
            if db_sid is None or db_sid.user is None:
                request.response.status_code = 403
                raise BadRequest(info = "Allowed only for registered users")
            
            db_file = Files(filename = FILENAME)._add()._flush()
            
            db_file.user_id = db_sid.user.id
            
            with open(db_file.path, "wb") as fd:
                fd.write(file.file.read())
            
            return db_file.__json__(request)
    except ExceptionInterface as x:
        return x.pyramid_serialize(request)
    
def includeme(config):
    Logger().files.info("Added route for files upload: %s", Config()["pyramid_rest.files.upload_url"])
    config.add_route("_rest_files", Config()["pyramid_rest.files.upload_url"], view = upload_file, renderer = "json")
    