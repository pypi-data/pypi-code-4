import threading
import time

from jenkinsapi.jenkins import Jenkins

from pybm.Job import Status
from pybm.Job import Job


class JenkinsMonitor():
    def __init__(self, url, view):
        self.url = url
        self.view = view
        self.job_list = []

    def get_job_list(self):
        return self.job_list

    def start(self):
        self.alive = True
        self.thread = threading.Thread(target=self.run)
        self.thread.setDaemon(True)
        self.thread.start()

    def run(self):
        while self.alive:
            J = Jenkins(self.url)
            views = J.views.keys()

            temp_job_list = []

            for view in views:
                if view == self.view:
                    for jobname in sorted(J.views[view].get_job_dict().keys()):
                        job = J.get_job(str(jobname))
                        lastBuild = job.get_last_buildnumber()

                        try:
                            lastGoodBuild = job.get_last_good_buildnumber()
                        except:
                            lastGoodBuild = -1  # no successful build found

                        try:
                            lastFailedBuild = job.get_last_failed_buildnumber()
                        except:
                            lastFailedBuild = -1  # no successful build found

                        running = False
                        try:
                            running = job.is_running()
                            jenkins_status = job.get_last_build().get_status()
                            if jenkins_status == 'UNSTABLE':
                                status = Status.WARNING
                            elif jenkins_status == 'SUCCESS':
                                status = Status.OK
                            elif jenkins_status == 'ABORTED' or jenkins_status == 'NOT_BUILT' or not job.is_enabled():
                                status = Status.UNKNOWN
                            elif jenkins_status == 'FAILURE':
                                status = Status.ERROR
                            running = job.get_last_buildnumber() != job.get_last_completed_buildnumber()
                            if running:
                                status = Status.BUILDING

                            temp_job_list.append(Job(jobname, status, 100))
                        except:
                            if lastBuild == lastFailedBuild:
                                status = Status.ERROR
                            elif lastBuild == lastGoodBuild:
                                status = Status.OK
                            else:
                                status = Status.UNKNOWN
                            if not job.is_enabled():
                                status = Status.UNKNOWN

                            running = job.get_last_buildnumber() != job.get_last_completed_buildnumber()
                            if running:
                                status = Status.BUILDING
                            temp_job_list.append(Job(jobname, status, 100))

            self.job_list = []
            for job in temp_job_list:
                self.job_list.append(job)

            time.sleep(5)

    def stop(self):
        self.alive = False