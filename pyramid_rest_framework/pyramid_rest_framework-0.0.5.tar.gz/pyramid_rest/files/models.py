#-*- coding: utf-8 -*-
"""
Реализует таблицу для хранения файлов. Модуль файлов требует следующие параметры,
прописанные в .ini:

    * **pyramid_rest.files.upload_url** - url - префикс для ресурса файлов.
    * **pyramid_rest.files.upload_path** - path для сохранения файлов. 
    * **pyramid_rest.files.deep** - глубина вложенности каталогов
    * **pyramid_rest.files.name_length** - длинна имени папки во вложенной структуре

Upload файлов производится через xhr на URL указанный в конфиге. При этом **обязательно** должен быть передан хидер **X-File-Name**. После upload'а возвращается
JSON объект сохраненного файла, который можно использовать для дальнейших действий. Для подключения модуля надо выполнить::

    files.includeme(config)
    
В __init__.py приложения.
    
"""
from pyramid_rest.security.models import Base
from sqlalchemy.types import Integer, String
import random
from pyramid_rest.config import Config
import uuid
import os
import subprocess
from pyramid_rest.models_crud import constructSuperModel, CRUD
from sqlalchemy import event
from pyramid_rest.logger import Logger
from sqlalchemy.schema import Column, ForeignKey


class Files(Base, CRUD):
    __tablename__ = "_rest_files"
    
    type = Column(String(200))
    
    __mapper_args__ = {'polymorphic_identity': '_rest_users',
                       'polymorphic_on': type}
    
    id = Column(Integer, primary_key = True)
    filename = Column(String(100))
    path = Column(String(200))
    url = Column(String(200))
    ext = Column(String(200))
    user_id = Column(Integer, ForeignKey("_rest_users.id"))
    
    def __init__(self, filename, *a, **k):
        self.filename = filename
        name = filename
        ext = filename.split(".")[-1]
        self.ext = ext

        def _generate_name(len):
            name = ""
            for i in range(len):
                name += random.choice("qazwsxedcrfvtgbyhnujmikolpQAZWSXEDCRFVTGBYHNUJMIKOLP1234567890")
            return name

        PATH = ""
        for i in range(int(Config()["pyramid_rest.files.deep"])):
            PATH = os.path.join(PATH, _generate_name(int(Config()["pyramid_rest.files.name_length"])))

        PATH = os.path.join(PATH, str(uuid.uuid4()))    

        self.url = os.path.join(Config()["pyramid_rest.files.upload_url"] or "/upload/",PATH, name)

        PATH = os.path.join(Config()["pyramid_rest.files.upload_path"], 
            PATH)

        subprocess.call("mkdir -p %s"%PATH,
         shell = True)
        
        self.path = os.path.join(PATH, name)
        
    def __json__(self, request):
        return {
                    "id": self.id,
                    "filename": self.filename,
                    "url": self.url
                }

def _files_delete_event(maper, connection, target):
    try:
        os.remove(target.path)
    except:
        Logger().files.warning("File with path %s doesn't exists"%target.path)
        
event.listen(Files, "after_delete", _files_delete_event)


