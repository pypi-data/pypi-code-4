from fabric.api import local
from fabric.contrib.console import confirm


def install():
    local("mkdir media static; return 0")
    local("virtualenv --distribute --system-site-packages virtualenv")
    local("virtualenv/bin/pip install -r requirements.txt")


def syncdbmigrate():
    local("python manage.py syncdb --noinput")
    local("python manage.py update_permissions")
    local("python manage.py loaddata {{ project_name }}/fixtures/*")
    local("python manage.py migrate")


def quickdeploy():
    local("sudo find -L static/ -type l -delete")
    local("sudo virtualenv/bin/python manage.py collectstatic --noinput -l "
          "|| sudo virtualenv/bin/python manage.py collectstatic --clear --noinput -l")
    local("sudo chown -RL :www-data media/")
    local("sudo chown root:root cronjobs && sudo chmod a=r,u=rw cronjobs; exit 0")
    local("sudo chmod -R a=rX /var/www/django_static/")
    local("sudo chmod -R g=rwX media/")
    local("sudo chmod -R g+rX ./")


def drop_create_db():
    local("cat drop_create_db.sql | python manage.py dbshell")


def deploy():
    install()
    syncdbmigrate()
    quickdeploy()


def clean():
    local("sudo rm -rf virtualenv/")


def cleaninstall():
    clean()
    deploy()


def test():
    """Run test suite."""
    local('./manage.py test')

applist = [
    "prescription",
    "risk",
    "stakeholder",
    "document",
    "implementation",
    "report"]


def clobbermodels():
    for app in applist:
        local('./manage.py schemamigration --initial --update ' + app)
    local('./manage.py migrate')


def graphmodels():
    local("echo ./manage.py graph_models -X User -X Audit -e -d -l fdp -o"
          " ~/Desktop/{{ project_name }}.png {0}".format(" ".join(applist)))
    for app in applist:
        local(
            "./manage.py graph_models -X User -X Audit -e -o"
            " ~/Desktop/{0}.png {0}".format(app))


def testmodels():
    import sys
    sys.path.append(".")
    from settings import INSTALLED_APPS
    for app in INSTALLED_APPS:
        print("Checking models/admin for app " + app)
        try:
            __import__(app + ".models")
        except ImportError as e:
            print(e)
        try:
            __import__(app + ".admin")
        except ImportError as e:
            print(e)


def metrics(self):
    local('pep8 --exclude=virtualenv,migrations . > reports/pep8.report')
    local('sloccount....')
    local('pyflakes ')

