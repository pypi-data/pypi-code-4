import os
import subprocess


class LTFSSource (object):
    def __init__(self, path):
        self.path = path


class LTFSJob (object):
    def __init__(self):
        self.id = 0
        self.source = []

        self.group = '0'
        self.selected_tape = 'UNASSIGNED'
        self.has_copy2 = 'no'
        self.copy2_id = ''
        self.status = 'QUEUED'
        self.copied = '0'
        self.total = '0'
        self.type = 'BACKUP'
        self.export = False
        self.start = '--:--'
        self.duration = '--:--'
        self.name = ''
        self.destination = ''
        self.delete_source = False

        self.destination2 = ''
        self.group2 = None
        self.export2 = False

    def clone(self):
        j = LTFSJob()
        j.__dict__.update(self.__dict__)
        return j


class LTFSJobsBackend (object):
    def __init__(self):
        self.jobs = []
        self.root = '/var/lib/syslink/archive'

    def parse_job(self, id, file):
        lines = file.read().splitlines()
        j = LTFSJob()
        j.id = id

        (j.group, j.selected_tape, j.has_copy2, j.copy2_id,
         j.status,  j.copied, j.total, j.type, j.export,
         j.start, j.duration, j.name, j.destination,
         j.delete_source) = lines[:14]

        j.export = j.export == 'yes'
        j.delete_source = j.delete_source == 'yes'
        j.progress = 1.0 * int(j.copied) / (int(j.total) + 1)
        return j

    def save_job(self, j, file):
        file.write('\n'.join((
            j.group, j.selected_tape, j.has_copy2, str(j.copy2_id),
            j.status,  j.copied, j.total, j.type, 'yes' if j.export else 'no',
            j.start, j.duration, j.name, j.destination,
            'yes' if j.delete_source else 'no',
        )) + '\n')

    def save_job_files(self, job, file):
        file.write('\n'.join(_.path for _ in job.source) + '\n')

    def get_log_path(self, job):
        return self.get_path(job, dir='logs') + '.log'

    def get_path(self, job, dir='jobs'):
        return os.path.join(self.root, dir, str(job.id))

    def run_action(self, action, job):
        subprocess.call([os.path.join(self.root, action + '.sh'), str(job.id)])
        self.reload()

    def create_job(self, job):
        id = 0
        for f in os.listdir(os.path.join(self.root, 'jobs')):
            if not '.' in f:
                if int(f) >= id:
                    id = int(f) + 1

        job.id = id
        self.save_job(job, open(self.get_path(job), 'w'))
        self.save_job_files(job, open(self.get_path(job) + '.files', 'w'))
        os.symlink(self.get_path(job), self.get_path(job, 'queue'))
        self.reload()

    def resave_job(self, job):
        self.save_job(job, open(self.get_path(job), 'w'))

    def reload(self):
        self.jobs = []

        for f in os.listdir(os.path.join(self.root, 'jobs')):
            if not '.' in f:
                j = self.parse_job(int(f), open(os.path.join(self.root, 'jobs', f)))
                j.source = [
                    LTFSSource(x)
                    for x in filter(None, open(os.path.join(self.root, 'jobs', f + '.files')).read().splitlines())
                ]
                self.jobs.append(j)

        self.jobs = sorted(self.jobs, key=lambda x: -x.id)
