"""
Version report for NetEase.

The paste app will report the version which get from {project}.nt_version.
Use the port of service to find the project.
if can not find project or `project.nt_version.version` return 'null'.
"""
import json
import logging

LOG = logging.getLogger(__name__)


port_map = {'8774': 'nova',
            '5000': 'keystone',
            '35357': 'keystone',
            '9292': 'glance',
            '7878': 'postman',
            '9800': 'umbrella',
            '9901': 'sentry'}


def _get_version(project):
    version_module_path = '%s.nt_version' % project
    try:
        version_module = __import__(version_module_path)
        version = getattr(version_module.nt_version, 'version')
    except (ImportError, AttributeError):
        LOG.error('Can not find "%s.nt_version". '
                    '/nt_version will not work.' % project)
        return None
    return version


def report_version_app(env, start_response):
    """
    Report the version of service.

    HTTP reponse example:
    {
        "version": "1.2.3",
        "service": "nova
    }
    """
    port = str(env['SERVER_PORT'])
    project = port_map.get(port, None)
    if not project:
        LOG.error("Unknow port %(port)s in %(port_map)s." % locals())

    version = _get_version(project)

    json_resp = {'version': version, 'service': project}
    headers = [('Content-Type', 'application/json')]
    start_response('200 OK', headers)
    return json.dumps(json_resp)


class ReportVersionFilter(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, env, start_response):
        if env['PATH_INFO'] == '/nt_version':
            return report_version_app(env, start_response)
        else:
            return self.app(env, start_response)


def app_factory(global_config, **local_config):
    return report_version_app


def filter_factory(global_config, **local_config):
    return ReportVersionFilter
