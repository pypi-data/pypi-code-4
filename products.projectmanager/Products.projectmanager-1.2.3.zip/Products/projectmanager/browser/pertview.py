"""Define a Pert browser view for the Task content type.
"""

from Acquisition import aq_inner
from diagramview import DiagramView

from Products.projectmanager.gvgen import GvGen
import tempfile
import os

from Products.Five.browser import BrowserView
from Products.Five.browser.resource import Resource
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserPublisher
from Products.CMFCore.utils import getToolByName

#class PertView(DiagramView):
#    """Pert diagram view of a Task
#    """

class PertImage(DiagramView):
    """Pert diagram view of a Task
    """
    def _genImage(self, actions, ordered_action_uids, task_begin_date):
        def calcDuration(start_date, end_date):
            """Calculate duration between start_date and end_date
            """
            if start_date is None:
                return 'None'
            if end_date is None:
                return 'None'
            return str(int(end_date - start_date))

        def createLink(node1, node2, label):
            """Create a link between two nodes and apply given label
            """
            link = graph.newLink(node1, node2)
            graph.propertyAppend(link, "label", label)

        def createNode(num, date):
            """Return a node with given label and Node style applied to it
            """
            node = graph.newItem('''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8"
><TR><TD BGCOLOR="gray69">%s</TD></TR><TR><TD PORT="here" BGCOLOR="gray92">%s</TD></TR></TABLE>>''' % (num, date))
            graph.styleApply("Node", node)
            return node

        def genLinkLabel(title, duration):
            """Generate label with given title and duration
            """
            return action['title'] + r'\n' + action_duration + ' ' + _(u"days", domain='projectmanager').encode('utf-8')

        context = aq_inner(self.context)
        # FIXME: should use a MessageCatalog instead
        _ = context.translate

#        graph = GvGen(_(u"Legend", domain='projectmanager').encode('utf-8'))
        graph = GvGen()
        graph.options += "rankdir=LR;"
        graph.styleAppend("Node", "shape", "plaintext")
#        graph.legendAppend("Node", _(u"num|begin date in days", domain='projectmanager').encode('utf-8'), 1)
        nodes = {}
        node_idx = 0

        # create initial node
        nodes['0'] = createNode(str(node_idx) + ' (begin)', '0')

        # first pass: creating all nodes
        for uid, start_date, end_date in ordered_action_uids:
            node_idx += 1
            action = actions[uid]
            action_begin_at = calcDuration(task_begin_date, end_date)
            nodes[uid] = createNode(str(node_idx), action_begin_at)

        # second pass: creating all links
        for uid, start_date, end_date in ordered_action_uids:
            action = actions[uid]
            prev_actions = action['PreviousActions']
            if not prev_actions:
                # it's the first action, we create a link from the begin node to this action's node
                action_duration = calcDuration(start_date, end_date)
                label = genLinkLabel(action['title'], action_duration)
                createLink(nodes['0'], nodes[uid], label)
            else:
                # for each previous actions, create a link from the previous node to this action's node
                for prev_uid in action['PreviousActions']:
                    action_duration = calcDuration(start_date, end_date)
                    label = genLinkLabel(action['title'], action_duration)
                    createLink(nodes[prev_uid], nodes[uid], label)

        # create temporary file to save the dot file (the file is removed when closed)
        fdot = tempfile.NamedTemporaryFile()
        #thedot = graph.dot()
        #thedot.replace('label="0 (begin)|0', '''label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD ROWSPAN="3" BGCOLOR="yellow">class</TD></TR><TR><TD PORT="here" BGCOLOR="lightblue">qualifier</TD></TR></TABLE>>''')
        graph.dot(fdot)
        fdot.flush()
        # don't close the file now, we need fdot.name later

#        fdot.seek(0)
#        dotcontent = fdot.read()
#        print dotcontent

        # create temporary file to save the dot file (the file is removed when closed)
        fpng = tempfile.NamedTemporaryFile()

        # call dot command to generate PNG file from the DOT file
        os.system("dot -Tpng %s > %s" % (fdot.name, fpng.name))

        # now we can close (and so remove) the dot file
        fdot.close()

        # read the generated PNG file and return the data
        fpng.seek(0)
        pngcontent = fpng.read()
        fpng.close()
        return pngcontent

    def __call__(self):
        response = self.request.response
        response.setHeader('Pragma', 'no-cache')
        response.setHeader('Cache-Control', 'no-cache')
        response.setHeader('Content-Type', 'image/png')

        method = self.request.get('method', 'view')
        if method == 'download':
            response.setHeader('Content-Disposition',
                               'attachment; filename="%s-pertdiagram.png"' % self.context.getId())

        # FIXME: getMultiAdapter
        #from zope.component import getMultiAdapter
        #view = getMultiAdapter((self.context, self.request), name='pm_view_diagram')
        view = self
        actions = view.getActions()
        ordered_action_uids = view.getOrderedActionUIDs(actions)
        task_begin_date = view.getTaskDate(actions)[0]

        data = self._genImage(actions, ordered_action_uids, task_begin_date)
        return data
#        response.write(data)
#        return None

class ProjectPertImage(PertImage):
    """Pert diagram view of a ProjectManager
    """
    def getActions(self):
        """Change the default call to getProjectActions
        """
        return self.getProjectActions()

