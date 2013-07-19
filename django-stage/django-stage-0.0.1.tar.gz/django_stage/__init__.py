import os


# load stage settings
def settings():
    PROJECT_ROOT = os.environ.get('PROJECT_ROOT')
    STAGE = os.environ.get('STAGE').lower()
    APPLICATION = os.environ.get('DJANGO_APPLICATION_NAME')
    path = '%s/%s/settings/%s.py' % (
        PROJECT_ROOT, APPLICATION, STAGE
    )
    namespace = {}
    execfile(path, namespace)
    return namespace
