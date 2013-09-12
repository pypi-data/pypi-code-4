#-*- coding: utf-8 -*-
from pyramid_rest.exceptions import BadRequest, ValidationError, Forbidden
from pyramid.view import view_config
from pyramid_rest.config import Config
from pyramid_rest.logger import Logger
import transaction
from pyramid_rest.files.models import Files
from pyramid_rest.security.decorators import AllowToGroups
import re
from pyramid_rest.security.models import Sessions

UPLOAD_FILENAME_PAT = re.compile("^\w+\.\w+$")


def upload_file(request):
    if request.is_xhr:
        FILENAME = request.headers.get("X-File-Name", None)
        if not FILENAME:
            return BadRequest(info = "In xhr query you must send X-File-Name header").serialize(request)
        if not UPLOAD_FILENAME_PAT.search(FILENAME):
            return ValidationError(info = "Incorrect file name. Must contain only letter symbols and extension.").serialize(request)
        
        
        
        with transaction.manager:
            db_sid = Sessions._get(sid = request.cookies.get("SID", -1))
            
            if db_sid is None or db_sid.user is None:
                raise Forbidden(info = "Allowed only for registered users")
            
            db_file = Files(filename = FILENAME)._add()._flush()
            
            db_file.user_id = db_sid.user.id
            
            with open(db_file.path, "wb") as fd:
                fd.write(request.body)
            
            return db_file.__json__(request)
        
    else:
        return BadRequest(info = "Only XHR upload allowed now").serialize(request)
    
def includeme(config):
    Logger().files.info("Added route for files upload: %s", Config()["pyramid_rest.files.upload_url"])
    config.add_route("_rest_files", Config()["pyramid_rest.files.upload_url"], view = upload_file, renderer = "json")
    