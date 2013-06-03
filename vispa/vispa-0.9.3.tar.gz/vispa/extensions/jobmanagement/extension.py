# -*- coding: utf-8 -*-

# imports
import cherrypy
import vispa
import vispa.rpc

from vispa import AbstractExtension

# import the controller
from controller import JobmanagementController

#import the jobpool
from job import JobPool


class JobmanagementExtension(AbstractExtension):

    def __init__(self, server):
        AbstractExtension.__init__(self, server)

        self._jobPool = JobPool(self)

    def get_name(self):
        return 'jobmanagement'

    def dependencies(self):
        return []

    def setup(self, extensionList):
        controller = JobmanagementController(extension=self)
        self.controller(controller)
        self.js('js/extension.js')
        #vispa.rpc.add_package_files(remote)

        """
        general
        """
        self.css('css/common.css')
        self.js("js/common/guid.js")
        self.js("js/common/DataModel.js")
        self.js("js/common/JobAjaxHandler.js")
        self.js("js/common/BatchManagerSelector.js")
        self.js("js/common/SelectableTable.js")
        self.js("js/common/SimpleButton.js")


        """
        job submission
        """
        self.js("js/jobsubmission/ajax.js")
        self.js("js/jobsubmission/submission.js")
        self.js("js/jobsubmission/view.js")
        self.css('css/jobsubmission.css')


        """
        job dashboard
        """
        self.js("js/jobdashboard/ajax.js")
        self.js("js/jobdashboard/dashboard.js")
        self.js("js/jobdashboard/view.js")
        self.css('css/jobdashboard.css')


        """
        job designer
        """
        self.js("js/jobdesigner/ajax.js")
        self.js("js/jobdesigner/jobdesigner.js")
        self.js("js/jobdesigner/view.js")
        self.css('css/jobdesigner.css')