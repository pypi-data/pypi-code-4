"""Distributed execution using an IPython cluster.

Uses IPython parallel to setup a cluster and manage execution:

http://ipython.org/ipython-doc/stable/parallel/index.html

Borrowed from Rory Kirchner's Bipy cluster implementation:

https://github.com/roryk/bipy/blob/master/bipy/cluster/__init__.py
"""
import os
import copy
import pipes
import time
import uuid
import subprocess
import contextlib

from bcbio import utils
from bcbio.log import setup_logging, logger
from bcbio.pipeline import config_utils

from IPython.parallel import Client
from IPython.parallel.apps import launcher
from IPython.utils import traitlets

# ## Custom launchers

timeout_params = ["--timeout=60", "--IPEngineApp.wait_for_url_file=960"]

class BcbioLSFEngineSetLauncher(launcher.LSFEngineSetLauncher):
    """Custom launcher handling heterogeneous clusters on LSF.
    """
    cores = traitlets.Integer(1, config=True)
    default_template = traitlets.Unicode("""#!/bin/sh
#BSUB -q {queue}
#BSUB -J bcbio-ipengine[1-{n}]
#BSUB -oo bcbio-ipengine.bsub.%%J
#BSUB -n {cores}
#BSUB -R "span[hosts=1]"
%s %s --profile-dir="{profile_dir}" --cluster-id="{cluster_id}"
    """ % (' '.join(map(pipes.quote, launcher.ipengine_cmd_argv)),
           ' '.join(timeout_params)))

    def start(self, n):
        self.context["cores"] = self.cores
        return super(BcbioLSFEngineSetLauncher, self).start(n)

class BcbioLSFControllerLauncher(launcher.LSFControllerLauncher):
    default_template = traitlets.Unicode("""#!/bin/sh
#BSUB -J bcbio-ipcontroller
#BSUB -oo bcbio-ipcontroller.bsub.%%J
%s --ip=* --log-to-file --profile-dir="{profile_dir}" --cluster-id="{cluster_id}" --nodb --hwm=5 --scheme=pure
    """%(' '.join(map(pipes.quote, launcher.ipcontroller_cmd_argv))))
    def start(self):
        return super(BcbioLSFControllerLauncher, self).start()

class BcbioSGEEngineSetLauncher(launcher.SGEEngineSetLauncher):
    """Custom launcher handling heterogeneous clusters on SGE.
    """
    cores = traitlets.Integer(1, config=True)
    pename = traitlets.Unicode("", config=True)
    default_template = traitlets.Unicode("""#$ -V
#$ -cwd
#$ -b y
#$ -j y
#$ -S /bin/sh
#$ -q {queue}
#$ -N bcbio-ipengine
#$ -t 1-{n}
#$ -pe {pename} {cores}
%s %s --profile-dir="{profile_dir}" --cluster-id="{cluster_id}"
"""% (' '.join(map(pipes.quote, launcher.ipengine_cmd_argv)),
      ' '.join(timeout_params)))

    def start(self, n):
        self.context["cores"] = self.cores
        self.context["pename"] = str(self.pename)
        return super(BcbioSGEEngineSetLauncher, self).start(n)

class BcbioSGEControllerLauncher(launcher.SGEControllerLauncher):
    default_template = traitlets.Unicode(u"""#$ -V
#$ -S /bin/sh
#$ -N ipcontroller
%s --ip=* --log-to-file --profile-dir="{profile_dir}" --cluster-id="{cluster_id}" --nodb --hwm=5 --scheme=pure
"""%(' '.join(map(pipes.quote, launcher.ipcontroller_cmd_argv))))
    def start(self):
        return super(BcbioSGEControllerLauncher, self).start()

def _find_parallel_environment():
    """Find an SGE/OGE parallel environment for running multicore jobs.
    """
    for name in subprocess.check_output(["qconf", "-spl"]).strip().split():
        if name:
            for line in subprocess.check_output(["qconf", "-sp", name]).split("\n"):
                if line.startswith("allocation_rule") and line.find("$pe_slots") >= 0:
                    return name
    raise ValueError("Could not find an SGE environment configured for parallel execution. " \
                     "See %s for SGE setup instructions." %
                     "https://blogs.oracle.com/templedf/entry/configuring_a_new_parallel_environment")

# ## Control clusters

def _start(parallel, profile, cluster_id):
    """Starts cluster from commandline.
    """
    scheduler = parallel["scheduler"].upper()
    ns = "bcbio.distributed.ipython"
    engine_class = "Bcbio%sEngineSetLauncher" % scheduler
    controller_class = "Bcbio%sControllerLauncher" % scheduler
    args = launcher.ipcluster_cmd_argv + \
        ["start",
         "--daemonize=True",
         "--IPClusterEngines.early_shutdown=240",
         "--delay=10",
         "--log-level=%s" % "WARN",
         "--profile=%s" % profile,
         #"--cluster-id=%s" % cluster_id,
         "--n=%s" % parallel["num_jobs"],
         "--%s.cores=%s" % (engine_class, parallel["cores_per_job"]),
         "--IPClusterStart.controller_launcher_class=%s.%s" % (ns, controller_class),
         "--IPClusterStart.engine_launcher_class=%s.%s" % (ns, engine_class),
         "--%sLauncher.queue='%s'" % (scheduler, parallel["queue"]),
         ]
    if scheduler in ["SGE"]:
        args += ["--%s.pename=%s" % (engine_class, _find_parallel_environment())]
    subprocess.check_call(args)

def _stop(profile, cluster_id):
    subprocess.check_call(launcher.ipcluster_cmd_argv +
                          ["stop", "--profile=%s" % profile,
                           #"--cluster-id=%s" % cluster_id
                          ])

def _is_up(profile, cluster_id, n):
    try:
        #client = Client(profile=profile, cluster_id=cluster_id)
        client = Client(profile=profile)
        up = len(client.ids)
        client.close()
    except IOError, msg:
        return False
    else:
        return up >= n

@contextlib.contextmanager
def cluster_view(parallel, config):
    """Provide a view on an ipython cluster for processing.

    parallel is a dictionary with:
      - scheduler: The type of cluster to start (lsf, sge).
      - num_jobs: Number of jobs to start.
      - cores_per_job: The number of cores to use for each job.
    """
    delay = 10
    max_delay = 960
    max_tries = 10
    profile = parallel["profile"]
    cluster_id = str(uuid.uuid1())
    num_tries = 0
    while 1:
        try:
            _start(parallel, profile, cluster_id)
            break
        except subprocess.CalledProcessError:
            if num_tries > max_tries:
                raise
            num_tries += 1
            time.sleep(delay)
    try:
        client = None
        slept = 0
        while not _is_up(profile, cluster_id, parallel["num_jobs"]):
            time.sleep(delay)
            slept += delay
            if slept > max_delay:
                raise IOError("Cluster startup timed out.")
        #client = Client(profile=profile, cluster_id=cluster_id)
        client = Client(profile=profile)
        # push config to all engines and force them to set up logging
        client[:]['config'] = config
        client[:].execute('from bcbio.log import setup_logging')
        client[:].execute('setup_logging(config)')
        client[:].execute('from bcbio.log import logger')
        yield client.load_balanced_view()
    finally:
        if client:
            client.close()
        _stop(profile, cluster_id)

def dictadd(orig, k, v):
    """Imitates immutability by adding a key/value to a new dictionary.
    Works around not being able to deepcopy view objects; can remove this
    once we create views on demand.
    """
    view = orig.pop("view", None)
    new = copy.deepcopy(orig)
    new[k] = v
    if view:
        orig["view"] = view
        new["view"] = view
    return new

def _find_cores_per_job(fn, parallel, item_count, config):
    """Determine cores and workers to use for this stage based on function metadata.
    """
    all_cores = [1]
    for prog in (fn.metadata.get("resources", []) if hasattr(fn, "metadata") else []):
        resources = config_utils.get_resources(prog, config)
        cores = resources.get("cores")
        if cores:
            all_cores.append(cores)
    cores_per_job = max(all_cores)
    total = parallel["cores"]
    if total > cores_per_job:
        return min(total // cores_per_job, item_count), cores_per_job
    else:
        return 1, total

cur_num = 0
def _get_checkpoint_file(cdir, fn_name):
    """Retrieve checkpoint file for this step, with step number and function name.
    """
    global cur_num
    fname = os.path.join(cdir, "%s-%s.done" % (cur_num, fn_name))
    cur_num += 1
    return fname

def add_cores_to_config(args, cores_per_job):
    """Add information about available cores for a job to configuration.
    Ugly hack to update core information in a configuration dictionary.
    """
    def _is_std_config(x):
        return (isinstance(x, dict) and x.has_key("algorithm") and x.has_key("resources"))
    def _is_nested_config(x):
        return (isinstance(x, dict) and x.has_key("config") and
                _is_std_config(x["config"]))

    new_i = None
    for i, arg in enumerate(args):
        if _is_std_config(arg) or _is_nested_config(arg):
            new_i = i
            break
    if new_i is None:
        raise ValueError("Could not find configuration in args: %s" % args)

    new_arg = copy.deepcopy(args[new_i])
    if _is_nested_config(new_arg):
        new_arg["config"]["algorithm"]["num_cores"] = int(cores_per_job)
    elif _is_std_config(new_arg):
        new_arg["algorithm"]["num_cores"] = int(cores_per_job)
    else:
        raise ValueError("Unexpected configuration dictionary: %s" % new_arg)
    args = list(args)[:]
    args[new_i] = new_arg
    return args

def runner(parallel, fn_name, items, work_dir, config):
    """Run a task on an ipython parallel cluster, allowing alternative queue types.

    This will spawn clusters for parallel and custom queue types like multicore
    and high I/O tasks on demand.

    A checkpoint directory keeps track of finished tasks, avoiding spinning up clusters
    for sections that have been previous processed.
    """
    setup_logging(config)
    out = []
    checkpoint_dir = utils.safe_makedir(os.path.join(work_dir, "checkpoints_ipython"))
    checkpoint_file = _get_checkpoint_file(checkpoint_dir, fn_name)
    fn = getattr(__import__("{base}.ipythontasks".format(base=parallel["module"]),
                            fromlist=["ipythontasks"]),
                 fn_name)
    items = [x for x in items if x is not None]
    num_jobs, cores_per_job = _find_cores_per_job(fn, parallel, len(items), config)
    parallel = dictadd(parallel, "cores_per_job", cores_per_job)
    parallel = dictadd(parallel, "num_jobs", num_jobs)
    # already finished, run locally on current machine to collect details
    if os.path.exists(checkpoint_file):
        logger.info("ipython: %s -- local; checkpoint passed" % fn_name)
        for args in items:
            if args:
                data = fn(args)
                if data:
                    out.extend(data)
    # Run on a standard parallel queue
    else:
        logger.info("ipython: %s" % fn_name)
        if len(items) > 0:
            items = [add_cores_to_config(x, cores_per_job) for x in items]
            with cluster_view(parallel, config) as view:
                for data in view.map_sync(fn, items, track=False):
                    if data:
                        out.extend(data)
    with open(checkpoint_file, "w") as out_handle:
        out_handle.write("done\n")
    return out
