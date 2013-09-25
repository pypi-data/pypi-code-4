"""Define a Gantt browser view for the ProjectManager content type.
"""

from Acquisition import aq_inner
from diagramview import DiagramView
from ganttview import GanttView

class ProjectGanttView(GanttView):
    """Gantt diagram view of a ProjectManager
    """
    def getActions(self):
        """redefine getActions call
        """
        return self.getProjectActions()
