#TODO: add old manifest map global variable set on clear, use in map method

import json
import os

from utils import *


class MetaFileManifest(MetaDataFileUtil):
    _persisted_data = {}
    _old_manifest_data = {}

    @property
    def _DATA_FILE(cls):
        return os.path.join(env.project_path, "config/manifest.json")

    def data_text(cls):
        return json.dumps(cls._persisted_data)

    def path(cls, filepath):
        return cls._persisted_data[filepath]

    def map(cls, mapped_filepath, target_filepath, remove_old=True):
        if remove_old and mapped_filepath in cls._persisted_data and target_filepath != cls.path(mapped_filepath):
            os.remove(cls.path(mapped_filepath))

        cls._persisted_data[mapped_filepath] = target_filepath

    def remove(cls, mapped_filepath, remove_file=True):
        if remove_file and mapped_filepath in cls._persisted_data:
            os.remove(cls.path(mapped_filepath))

        del cls._persisted_data[mapped_filepath]

    def clear(cls):
        cls._old_manifest_data = cls._persisted_data
        cls._persisted_data = {}
        return cls._old_manifest_data

    def remove_orphans(cls, old_manifest_data):
        for orphan_filepath in (set(old_manifest_data) - set(cls._persisted_data)):
            os.remove(old_manifest_data[orphan_filepath])

class FileManifest(object): __metaclass__ = MetaFileManifest