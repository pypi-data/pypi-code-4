"""Define a PERT browser view for the Task content type.
"""

from Acquisition import aq_inner

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.projectmanager.browser.utils import truncate

class DiagramView(BrowserView):
    """Diagram view of a Task
    """

    def getActions(self):
        """Method pattern implementation
        By default call getTaskActions
        """
        return self.getTaskActions()


    def getTaskActions(self, task=None):
        """Return a dictionary of all informations about actions of the task.
        """
        if task is None:
            context = aq_inner(self.context)
        else:
            context = task

        #TODO: use catalog
        actions = context.objectValues("PM_Action")
        action_values = {}
        portal_workflow = getToolByName(context, 'portal_workflow')
        getInfoFor = portal_workflow.getInfoFor


        user = self.request.AUTHENTICATED_USER.getId()

        for action in actions :
            humanressources = action.getMHumanRessources()
            action_uid = action.UID()
            for human in humanressources:
                if user == human.split(':')[0]:
                    userisassigned = True
                    break
            else:
                 userisassigned = False

            review_state = getInfoFor(action, 'review_state')
            title = action.Title()
            action_dict = {'label': truncate(title, 30),
                           'title': action.Title(),
                           'UID': action_uid,
                           'url': action.absolute_url(),
                           'review_state': review_state,
                           'StartDate': action.getMStartDate(),
                           'EstimatedEndDate': action.getMEstimatedEndDate(),
                           'EndDate': action.getMEndDate(),
                           'PreviousActions': action.getRawMPreviousAction(),
                           'HumanRessources': humanressources,
                           'userIsAssigned': userisassigned,
                           }

            action_values[action_uid] = action_dict

        return action_values

    def getTaskDate(self, action_info_list=None) :
        """Return a tuple of the first and last action dates if they exists,
        (None, None) otherwise.
        """
        if action_info_list is None :
            action_info_list = self.getActions()
        if not action_info_list :
            return (None, None)
        start_date = None
        end_date = None
        for action in action_info_list.values() :
            action_start_date = action['StartDate']
            if action_start_date and (start_date is None or action_start_date < start_date ) :
                start_date = action_start_date
            action_end_date = action['EndDate']
            if action_end_date is None :
                action_end_date = action['EstimatedEndDate']
            if action_end_date and (end_date is None or action_end_date > end_date) :
                end_date = action_end_date

        return (start_date, end_date)


    def getOrderedActionUIDs(self, action_info_list=None) :
        """Return a list of tuple (action uid, start_date or previous action last end date,
        end_date or estimated_end_date) ordered by their start date.
        """
        if action_info_list is None :
            action_info_list = self.getActions()
        if not action_info_list :
            return []

        action_list = []

        def findStartDate(action) :
            previous_uids = action['PreviousActions']
            end_date = None
            for previous_action in [action_info_list[uid] for uid in previous_uids] :
                previous_action_end_date = previous_action['EndDate']
                if previous_action_end_date is None and previous_action['PreviousActions'] :
                    previous_action_end_date = findStartDate(previous_action)
                if previous_action_end_date and (end_date is None or previous_action_end_date > end_date) :
                    end_date = previous_action_end_date
            return end_date

        def cmp_action(i1, i2) :
             x = i1[1]
             y = i2[1]
             if x is None and y is None :
                 return 0
             if x is None :
                 return 1
             if y is None :
                 return -1
             if x == y :
                 return 0
             if x < y :
                 return -1
             return 1

        for uid, action in action_info_list.items() :
            action_start_date = action['StartDate']
            action_end_date = action['EndDate']
            if action_end_date is None :
                action_end_date = action['EstimatedEndDate']
            if action_start_date is not None :
                #We know the start date
                action_list.append((uid, action_start_date, action_end_date))
            elif action['PreviousActions'] :
                #we have to search for the last end date of the action previous actions
                action_list.append((uid, findStartDate(action), action_end_date))
            else :
                #As we don't know the start date we set it to None
                action_list.append((uid, None, action_end_date))
        action_list.sort(cmp_action)
        return action_list

    def getProjectActions(self):
        """Process recursivly getTaskActions for all project manager tasks
        """
        context = aq_inner(self.context)
        tasks = context.objectValues("PM_Task")
        portal_workflow = getToolByName(context, 'portal_workflow')
        getInfoFor = portal_workflow.getInfoFor
        action_values = {}
        for task in tasks :
            action_values.update(self.getTaskActions(task))
        return action_values

class HumanRessources(BrowserView):

    pass