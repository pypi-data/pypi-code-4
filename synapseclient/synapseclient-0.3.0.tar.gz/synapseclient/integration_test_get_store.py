## integration tests for get and store commands
############################################################

## to run tests: nosetests -vs synapseclient/integration_test_get_store.py
## to run single test: nosetests -vs synapseclient/integration_test_get_store.py:test_foo

from nose.tools import *
import synapseclient
from entity import Entity, Project, Folder, File
from entity import Data
import utils
import uuid
import filecmp
import os
from datetime import datetime as Datetime


def setup_module(module):
    print '~' * 60
    print 'testing Entity'

    ## if testing endpoints are set in the config file, use them
    ## this was created 'cause nosetests doesn't have a good means of
    ## passing parameters to the tests
    if os.path.exists(synapseclient.client.CONFIG_FILE):
        try:
            import ConfigParser
            config = ConfigParser.ConfigParser()
            config.read(synapseclient.client.CONFIG_FILE)
            if config.has_section('testEndpoints'):
                repoEndpoint=config.get('testEndpoints', 'repo')
                authEndpoint=config.get('testEndpoints', 'auth')
                fileHandleEndpoint=config.get('testEndpoints', 'file')
                print "Testing against endpoint:"
                print "  " + repoEndpoint
                print "  " + authEndpoint
                print "  " + fileHandleEndpoint
        except Exception as e:
            print e

    syn = synapseclient.Synapse()
    syn.login()
    module.syn = syn
    module._to_cleanup = []

def teardown_module(module):
    cleanup(module._to_cleanup)


def get_cached_synapse_instance():
    """return a cached synapse instance, so we don't have to keep logging in"""
    return globals()['syn']

def create_project(name=None):
    """return a newly created project that will be cleaned up during teardown"""
    if name is None:
        name = str(uuid.uuid4())
    project = {'entityType':'org.sagebionetworks.repo.model.Project', 'name':name}
    project = syn.createEntity(project)
    schedule_for_cleanup(project)
    return project

def schedule_for_cleanup(item):
    """schedule a file of Synapse Entity to be deleted during teardown"""
    globals()['_to_cleanup'].append(item)

def cleanup(items):
    """cleanup junk created during testing"""
    for item in items:
        if isinstance(item, Entity):
            try:
                syn.deleteEntity(item)
            except Exception as ex:
                print "Error cleaning up entity: " + str(ex)
        elif isinstance(item, basestring) and os.path.exists(item):
            try:
                os.remove(item)
            except Exception as ex:
                print ex
        else:
            sys.stderr.write('Don\'t know how to clean: %s' % str(item))


def test_get_and_store():
    name = str(uuid.uuid4())
    project = Project(name, description='A silly project')
    syn = get_cached_synapse_instance()

