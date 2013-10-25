#
# Copyright 2013 Mortar Data Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import time

from mortar.api.v2 import clusters

# Job Status constants
STATUS_STARTING          = 'starting'
STATUS_GATEWAY_STARTING  = 'GATEWAY_STARTING' #Comes from task.
STATUS_VALIDATING_SCRIPT = 'validating_script'
STATUS_SCRIPT_ERROR      = 'script_error'
STATUS_PLAN_ERROR        = 'plan_error'
STATUS_STARTING_CLUSTER  = 'starting_cluster'
STATUS_RUNNING           = 'running'
STATUS_SUCCESS           = 'success'
STATUS_EXECUTION_ERROR   = 'execution_error'
STATUS_SERVICE_ERROR     = 'service_error'
STATUS_STOPPING          = 'stopping'
STATUS_STOPPED           = 'stopped'

# All statuses that indicate a completed job
COMPLETE_STATUSES = (\
    STATUS_SCRIPT_ERROR, 
    STATUS_PLAN_ERROR, 
    STATUS_SUCCESS, 
    STATUS_EXECUTION_ERROR, 
    STATUS_SERVICE_ERROR,
    STATUS_STOPPED)

def post_job_new_cluster(api, project_name, script_name, cluster_size, cluster_type=clusters.CLUSTER_TYPE_PERSISTENT,
                         git_ref='master', parameters=None, notify_on_job_finish=True, is_control_script=False,
                         pig_version=None):
    """
    Post a new job to a new cluster.
    
    :type api: :class:`mortar.api.v2.api.API`
    :param api: API

    :type project_name: str
    :param project_name: Name of Mortar project where job lives (e.g. myproject)
    
    :type script_name: str
    :param script_name: Name of pigscript or controlscript to run with no file extension (e.g. mypigscript)
    
    :type cluster_size: integer
    :param cluster_size: size in number of nodes of new cluster
    
    :type cluster_type: string
    :param cluster_type: Shutoff policy for cluster: immediately on job completion (single_job), after idle for one hour (persistent), or no automatic shutoff (permanent). Default: persistent.
    
    :type git_ref: string
    :param git_ref: branch or commit hash at which to run project code.  Default: master.

    :type parameters: dict
    :param parameters: pig parameters to pass to the script
    
    :type notify_on_job_finish: bool
    :param notify_on_job_finish: whether to send an email when the job finishes. Default: true.
    
    :type is_control_script: bool
    :param is_control_script: whether the script being run is a controlscript (not a pigscript). Default: false.
    
    :type pig_version: string
    :param pig_version: Major version of pig to run.  If null, uses the Mortar platform default (currently 0.9).
    
    :raises: requests.exception.HTTPError: if a 40x or 50x error occurs
    
    :rtype: str:
    :returns: job_id for newly created job
    """
    body = {'project_name': project_name,
            'git_ref': git_ref,            
            'cluster_size': cluster_size,
            'cluster_type': cluster_type,
            'parameters': parameters or {},
            'notify_on_job_finish': notify_on_job_finish
    }
    
    if is_control_script:        
        body["controlscript_name"] = script_name
    else:
        body["pigscript_name"] = script_name

    if pig_version:
        body["pig_version"] = pig_version

    return api.post('jobs', body)['job_id']


def post_job_existing_cluster(api, project_name, script_name, cluster_id, cluster_type=clusters.CLUSTER_TYPE_PERSISTENT,
                              git_ref='master', parameters=None, notify_on_job_finish=True, is_control_script=False,
                              pig_version=None):
    """
    Post a new job to an existing cluster.
    
    :type api: :class:`mortar.api.v2.api.API`
    :param api: API

    :type project_name: str
    :param project_name: Name of Mortar project where job lives (e.g. myproject)
    
    :type script_name: str
    :param script_name: Name of pigscript or controlscript to run with no file extension (e.g. mypigscript)
    
    :type cluster_id: string
    :param cluster_id: ID of cluster on which job should be run.
    
    :type git_ref: string
    :param git_ref: branch or commit hash at which to run project code.  Default: master.

    :type parameters: dict
    :param parameters: pig parameters to pass to the script
    
    :type notify_on_job_finish: bool
    :param notify_on_job_finish: whether to send an email when the job finishes. Default: true.
    
    :type is_control_script: bool
    :param is_control_script: whether the script being run is a controlscript (not a pigscript). Default: false.
    
    :type pig_version: string
    :param pig_version: Major version of pig to run.  If null, uses the Mortar platform default (currently 0.9).
    
    :raises: requests.exception.HTTPError: if a 40x or 50x error occurs
    
    :rtype: str:
    :returns: job_id for newly created job
    """
    body = {'project_name': project_name,
            'git_ref': git_ref,            
            'cluster_id': cluster_id,
            'parameters': parameters or {},
            'notify_on_job_finish': notify_on_job_finish
    }
    
    if is_control_script:        
        body["controlscript_name"] = script_name
    else:
        body["pigscript_name"] = script_name

    if pig_version:
        body["pig_version"] = pig_version

    return api.post('jobs', body)['job_id']
    

def get_job(api, job_id):
    """
    Get job details.
    
    :type api: :class:`mortar.api.v2.api.API`
    :param api: API

    :type job_id: str
    :param job_id: ID of job
    
    :raises: requests.exception.HTTPError: if a 40x or 50x error occurs
    
    :rtype: dict:
    :returns: dictionary with job details
    """
    return api.get('jobs/%s' % job_id)

def get_jobs(api, skip=None, limit=None):
    """
    Get multiple jobs from the API.
    
    :type api: :class:`mortar.api.v2.api.API`
    :param api: API

    :type skip: integer
    :param skip: Number of jobs in the list (sorted by descending start_timestamp) to skip before returning jobs
    
    :type limit: integer
    :param limit: Total number of jobs to return at once.
    
    :raises: requests.exception.HTTPError: if a 40x or 50x error occurs
    
    :rtype: list:
    :returns: list of dict of job details
    """
    return api.get('jobs', 
                   params={'skip': skip, 'limit': limit})

def block_until_job_complete(api, job_id, poll_frequency_sec=5.0):
    """
    Block until a job has completed, polling occasionally for status.
    
    :type api: :class:`mortar.api.v2.api.API`
    :param api: API

    :type job_id: str
    :param job_id: ID of job to poll
    
    :type poll_frequency_sec: integer
    :param poll_frequency_sec: How frequently to poll.  Default: 5.0 seconds.
    
    :raises: requests.exception.HTTPError: if a 40x or 50x error occurs
    
    :rtype: str:
    :returns: final status_code of job
    """
    
    while True:
        job_status = get_job(api, job_id)['status_code']
        if job_status in COMPLETE_STATUSES:
            return job_status
        time.sleep(poll_frequency_sec)
