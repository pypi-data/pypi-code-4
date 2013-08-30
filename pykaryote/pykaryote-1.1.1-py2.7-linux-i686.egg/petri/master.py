#!/usr/bin/env python
"""Code to execute on master thread.

The master thread holds a thread pool and a queue of jobs. It sends jobs to
worker processors and reports status on running jobs.
"""
from mpi4py import MPI
import os.path
import shutil
import time
import datetime
import ConfigParser
from collections import deque
import tags
from pykaryote.utils.comparison import get_config as load_from_cmp
from pykaryote.utils.comparison import make_cfg

comm = MPI.COMM_WORLD


class Master(object):
    """Object to run on the master processor.

    Master controls the queuing of jobs and the reporting of job status.
    """
    def __init__(self, dest_dir, status_interval=10):
        # the directory where mpi jobs are saved
        self.dest_dir = dest_dir
        # the amount of time (in seconds) to wait before printing a status
        # update. default is 10 seconds.
        self._status_interval = status_interval
        # the time when the last status update was displayed
        self._last_status = time.time()

        # data structures to hold the processor pool and queue of jobs
        self._idle_processes = deque(range(1, comm.Get_size()))
        self._busy_processes = set()
        self._waiting_jobs = deque()
        self._running_jobs = []
        self._finished_jobs = []
        self._comparisons = {}
        # flag - true when inside the _wait_and_log() method
        # indicates that Master is waiting for status and it is safe to send
        # send queued jobs
        self._running = False

    def log(self, string):
        """Prints a string to the log.

        The function could later be used to write to a log file.
        """
        print string

    def _processes_needed(self):
        """Returns the number of processes needed to finish the job.

        Used to know how many idle processes to shutdown.
        """
        return len(self._waiting_jobs)

    def add_comparisons(self, batch_config, num_runs=None, clean=True):
        """Adds comparisons from a config file.

        Optionally overrides the number of runs.
        Config files are in .ini format, where each section is the name of a
        comparison. For example:
        
            [my-comparison]
            comparison_config = configs/cmp.cfg
            simulation_config = configs/sim.cfg
            num_runs = 80
        """
        config = ConfigParser.RawConfigParser()
        try:
            with open(batch_config) as f:
                config.readfp(f)
        except IOError:
            print 'Error adding batch: no such file \'{}\''.format(batch_config)
            return
        for comparison_name in config.sections():
            cmp_cfg = os.path.expanduser(config.get(comparison_name,
                                         'comparison_config'))
            sim_cfg = os.path.expanduser(config.get(comparison_name,
                                         'simulation_config'))
            if num_runs is None:
                runs = config.getint(comparison_name, 'num_runs')
            else:
                runs = num_runs
            self.add_comparison(cmp_cfg, sim_cfg, comparison_name, runs,
                                clean=clean)

    def add_comparison(self, comparison_config_filename, sim_config_filename,
                       comparison_name, num_runs, clean=True):
        """Queues a comparison to run.
        """
        # load each comparison option into a list
        vary_attrs, values = load_from_cmp(comparison_config_filename)

        # ensure that the comparison has a valid, unused name
        # a comparisons must contain 'omparison' in its name
        if not 'omparison' in comparison_name:
            comparison_name = 'comparison-{}'.format(comparison_name)
        reserved_names = os.listdir(self.dest_dir)
        reserved_names.extend(self._comparisons.keys())
        if comparison_name in reserved_names:
            num = 0
            while '{}-{}'.format(comparison_name, num) in reserved_names:
                num += 1
            comparison_name = '{}-{}'.format(comparison_name, num)

        # create configuration files from cmp.cfg
        config_filenames = []
        config_dir = os.path.join(self.dest_dir, comparison_name,
                                  'sim_configs')
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        gen_limits = []
        for x, vals in enumerate(values):
            out_filename = os.path.join(config_dir, 'sim-{}.cfg'.format(x))
            config_filenames.append(out_filename)
            make_cfg(vary_attrs, vals, sim_config_filename, out_filename)
            config = ConfigParser.RawConfigParser()
            config.read(out_filename)
            gen_limits.append(config.getint('global', 'generation_limit'))
        
        # copy comparison config file to comparison directory
        shutil.copyfile(comparison_config_filename, os.path.join(self.dest_dir, 
                        comparison_name, 'cmp.cfg'))

        # store data about this comparison
        comparison = {}
        comparison['num_runs'] = num_runs
        comparison['values'] = values
        comparison['vary_attrs'] = vary_attrs
        comparison['total_processes'] = len(values) * num_runs
        comparison['num_done'] = 0
        comparison['num_failed'] = 0
        comparison['num_running'] = 0
        comparison['num_waiting'] = len(values) * num_runs
        comparison['graphed'] = False
        comparison['current_gens'] = 0
        comparison['clean'] = clean
        # get total number of generations to be run
        target_gens = 0
        for target_gen in gen_limits:
            target_gens += target_gen * num_runs
        comparison['target_gens'] = target_gens
        comparison['gen_limits'] = gen_limits
        self._comparisons[comparison_name] = comparison

        # create jobs and add to waiting jobs list
        for run_num in range(num_runs):
            for sim_num, config_filename in enumerate(config_filenames):
                target_gen = gen_limits[sim_num]
                job = self._create_comparison_job(config_filename, 
                                                  comparison_name, run_num,
                                                  sim_num, target_gen)
                self._add_job(job)
        self.log('added comparison: {}'.format(comparison_name))

    def _create_comparison_job(self, config_filename, comparison_name, run_num,
                               sim_num, target_gen):
        # target_gen is the generation at which the simulation is set to stop
        job = {}
        job['config_filename'] = config_filename
        job['type'] = 'comparison'
        job['comparison_name'] = comparison_name
        job['run_num'] = run_num
        job['sim_num'] = sim_num
        job['status'] = (0, target_gen, -1)
        return job

    def _add_job(self, job, high_priority=False):
        """Queues a job to run.

        High priority jobs are put in the front of the queue. Regular jobs go
        to the back of the queue.
        """
        if high_priority:
            self._waiting_jobs.appendleft(job)
        else:
            self._waiting_jobs.append(job)
        self._send_jobs()

    def _send_jobs(self):
        """Sends waiting jobs to idle processes.
        """
        while self._waiting_jobs and self._idle_processes and self._running:
            job = self._waiting_jobs.popleft()
            process_id = self._idle_processes.popleft()
            job['process_id'] = process_id

            comm.send(job, process_id, tag=tags.JOB_TAG)

            self._running_jobs.append(job)
            self._busy_processes.add(process_id)
            if job['type'] == 'comparison':
                cmp_name = job['comparison_name']
                self._comparisons[cmp_name]['num_running'] += 1
                self._comparisons[cmp_name]['num_waiting'] -= 1

    def wait_and_log(self):
        """Starts the main loop.

        Call this after adding jobs to the queue. This is the main loop of the
        program, which sends jobs and prints status reports.
        """
        start_time = time.time()
        self._running = True
        self._send_jobs()
        self._report_status()
        while self._busy_processes:
            # shutdown unneeded idle processes
            num_needed = self._processes_needed()
            while num_needed < len(self._idle_processes):
                process_id = self._idle_processes.popleft()
                comm.send(-1, process_id, tag=tags.SHUTDOWN_TAG)

            # wait for a worker to message
            status = MPI.Status()
            message = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG,
                                status=status)

            process_id = status.source
            if status.tag == tags.SUCCESS_TAG:
                self._on_job_done(message, status.tag)
            elif status.tag == tags.FAILED_TAG:
                self._on_job_done(message, status.tag)
            elif status.tag == tags.STATUS_TAG:
                self._on_recive_status(message[0], message[1], message[2],
                                       process_id)
        print 'all jobs done'
        elapsed = datetime.timedelta(seconds=time.time() - start_time)
        print 'runtime: {} (hh:mm:ss)'.format(elapsed)

    def _on_recive_status(self, current_gen, target_gen, eta, process_id):
        """Processes status updates received from running simulations.
        """
        # TODO: store jobs better for O(1) access time
        for job in self._running_jobs:
            if job['process_id'] == process_id:
                job['status'] = (current_gen, target_gen, eta)
                break
        if time.time() - self._last_status > self._status_interval:
            self._report_status()

    def _report_status(self):
        """Reports status on running jobs.

        called at most every self._status_interval seconds.
        """
        for comp in self._comparisons.itervalues():
            comp['current_gens'] = 0

        for job in self._finished_jobs:
            if job['type'] == 'comparison':
                g = job['status'][1]
                self._comparisons[job['comparison_name']]['current_gens'] += g
        for job in self._running_jobs:
            if job['type'] == 'comparison':
                g = job['status'][0]
                self._comparisons[job['comparison_name']]['current_gens'] += g

        total_gens_done = 0
        total_gens_target = 0
        no_target_gen = False

        # generate status strings for each comparison
        comparisons = []
        for name, comp in self._comparisons.iteritems():
            if comp['target_gens'] == 0:
                percent_done = '??'
                no_target_gen = True
            else:
                total_gens_done += comp['current_gens']
                total_gens_target += comp['target_gens']
                percent_done = comp['current_gens'] / float(comp['target_gens'])
                percent_done = '{:.2%}'.format(percent_done)
            header = '{name}: {percent_done}'.format(name=name,
                                                     percent_done=percent_done)
            summary = '({} running, {} done, {} failed, {} queued)'.format(
                                        comp['num_running'], comp['num_done'], 
                                        comp['num_failed'], comp['num_waiting'])
            comparisons.append('{}\n\t{}'.format(header, summary))
        if not total_gens_target:
            no_target_gen = True
        # generate status string for total
        if no_target_gen:
            total_progress = 'NA'
        else:
            percent = total_gens_done / float(total_gens_target)
            total_progress = '{:.2%}'.format(percent)

        # print status information
        print '\nTotal: {} ({}/{})'.format(total_progress, total_gens_done, 
                                         total_gens_target)
        for comparison_status in comparisons:
            print comparison_status
        # print jobs with top 3 ETAs
        print 'Top 3 slowest jobs:'
        sort_key = lambda j: j.get('status', (0, 0, -1))[2]
        for job in sorted(self._running_jobs, key=sort_key, reverse=True)[:3]:
            eta = job.get('status', (0, 0, -1))[2]
            if eta == -1:
                eta_str = 'N/A'
            else:
                eta_str = '{} min {} sec'.format(eta/60, eta%60)
            print '\t{} eta: {}'.format(self._job_to_str(job), eta_str)
        print

        self._last_status = time.time()

    def _on_job_done(self, job, tag):
        """Called when a job is finished or died.

        Checks to see if the entire comparison is finished and sends waiting
        jobs.
        """
        # mark process as idle
        process_id = job['process_id']
        self._busy_processes.remove(process_id)
        self._idle_processes.append(process_id)
        #TODO: store jobs so that access by process id is O(1)
        index = 0
        for j in self._running_jobs:
            if j['process_id'] == process_id:
                break
            index += 1
        job = self._running_jobs.pop(index)
        self._finished_jobs.append(job)

        if job['type'] == 'comparison':
            cmp_name = job['comparison_name']
            comp = self._comparisons[cmp_name]
            # update statistics
            comp['num_running'] -= 1
            # target_gen = comp['gen_limits'][job['sim_num']]
            # comp['current_gens'] += target_gen
            if tag == tags.SUCCESS_TAG:
                # process finished successfully.
                self.log('job done: {}'.format(self._job_to_str(job)))
                comp['num_done'] += 1
            elif tag == tags.FAILED_TAG:
                # process failed or was killed
                self.log('job failed: {}'.format(self._job_to_str(job)))
                comp['num_failed'] += 1
            if self._comparison_ready_to_graph(cmp_name):
                if comp['num_done'] == 0:
                    # don't graph if all the runs failed
                    self.log('finished comparison {}, but all runs failed'.format(cmp_name))
                else:
                    self._send_graph_comparison_job(cmp_name)
                    self.log('graphing {}'.format(cmp_name))
        elif job['type'] == 'comparison_graph':
            cmp_name = job['comparison_name']
            if tag == tags.SUCCESS_TAG:
                self._comparisons[cmp_name]['graphed'] == True
                self.log('finished comparison: {}'.format(cmp_name))
            else:
                self.log('finished comparison: {}, but graphing failed'.format(cmp_name))

        # send waiting jobs
        self._send_jobs()

    def _job_to_str(self, job):
        """Return a human readable string representation of a job.
        """
        if job['type'] == 'comparison':
            return '{comparison_name} sim {sim_num} run {run_num}'.format(**job)
        elif job['type'] == 'comparison_graph':
            return 'graph {}'.format(job['comparison_name'])

    def _comparison_ready_to_graph(self, cmp_name):
        """Returns True if a comparison of the given name is ready to be graphed.
        """
        comp = self._comparisons[cmp_name]
        return (comp['num_done'] + comp['num_failed'] == 
                comp['total_processes'])

    def _send_graph_comparison_job(self, cmp_name):
        """Queues a worker to aggregate and graph a finished comparison.
        """
        job = {}
        job['type'] = 'comparison_graph'
        job['comparison_name'] = cmp_name
        job['values'] = self._comparisons[cmp_name]['values']
        job['num_runs'] = self._comparisons[cmp_name]['num_runs']
        job['clean'] = self._comparisons[cmp_name]['clean']
        self._add_job(job, high_priority=True)

    def shutdown(self):
        """Shuts down all processes and clear the list of queued jobs.

        If a job is currently running, that job will not shutdown until
        it finishes.

        No jobs can be sent after this call.
        """
        for process_id in range(1, comm.Get_size()):
            comm.send(-1, process_id, tag=tags.SHUTDOWN_TAG)
        self._idle_processes = deque()
        self._busy_processes = set()
        self._waiting_jobs = deque()
        self._running_jobs = []
