from flask import Blueprint
import uploader

blueprint = uploader.file_uploader

def getBlueprint():
    return blueprint
