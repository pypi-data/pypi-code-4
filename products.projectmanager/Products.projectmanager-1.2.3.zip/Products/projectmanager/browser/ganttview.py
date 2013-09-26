"""Define a Gantt browser view for the Task content type.
"""

from zope.component.hooks import getSite

from diagramview import DiagramView

class GanttView(DiagramView):
    """Gantt diagram view of a Task
    """
    def getYearsMonthsAndWeeksAndDays(self, start_date, delta, first_week_day = 1):
        """Return tuple of one list of (year number, number of days),
        one list of (month number, number of days),
        and one list of (week number, number of days),
        and one list of day number
        """
        if not delta or delta <= 0 :
            return ([],[],[],[])
        years = []
        months = []
        weeks = []
        days = []
        for index in xrange(int(delta)) :
            current_day = start_date + index
            day = current_day.day()
            dow = current_day.dow()
            month = current_day.month()
            week = current_day.week()
            year = current_day.year()
            if index == 0 :
                years = [(year, 1)]
                months = [(month, 1)]
                weeks  = [(week, 1)]
                days = [day]
            else :
                if month == 1 and day == 1 :
                    years.append((year, 1))
                else :
                    year_item = years.pop()
                    new_year_item = (year, year_item[1] + 1)
                    years.append(new_year_item)
                if day == 1 :
                    months.append((month, 1))
                else :
                    month_item = months.pop()
                    new_month_item = (month, month_item[1] + 1)
                    months.append(new_month_item)
                if dow == first_week_day :
                    weeks.append((week, 1))
                else :
                    week_item = weeks.pop()
                    new_week_item = (week, week_item[1] + 1)
                    weeks.append(new_week_item)
                days.append(day)
        return (years, months, weeks, days)

    def states(self):
        wtool = getSite().portal_workflow
        workflow = wtool['PM_ActionWorkflow']
        values = []
        for state in workflow['states'].values():
            values.append({
                      'title': state.title,
                      'id': state.id})

        return values
