import os


def find_project_root(path='.', max_depth=5):
    for i in range(max_depth):
        files = os.listdir(path)
        if not (set(['bin', 'include', 'lib']) - set(files)):
            return os.path.realpath(path)
        path = os.path.join(path, '..')


def find_project_name(path=None):
    if not path:
        return
    for name in os.listdir(path):
        full_path = os.path.join(path, name)
        if os.path.isdir(full_path) and 'manage.py' in os.listdir(full_path):
            return name


def print_usage():
    print "Usage: dj <command>"
    print
    print "  dj new myproject"
    print "  cd myproject/"
    print "  dj app hello"
    print "  vi myproject/myproject/models.py"
    print "  dj sync hello"
    print "  dj run"
    print "  dj shell"
    print "  dj install gunicorn ..."
