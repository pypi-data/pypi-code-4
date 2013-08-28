import os


CWD = os.path.dirname(os.path.realpath(__file__))

LOCAL_FOLDER = "%s/.pylocalsmtp/" % os.path.expanduser("~")
DB_NAME = "%sinbox.db" % LOCAL_FOLDER

TEMPLATES_DIR = "%s/templates/" % CWD
MEDIAS_DIR = "%s/medias/" % CWD


if not os.path.exists(LOCAL_FOLDER):
    os.makedirs(LOCAL_FOLDER)
