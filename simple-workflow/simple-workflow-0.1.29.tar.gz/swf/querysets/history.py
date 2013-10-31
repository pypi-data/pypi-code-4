
class HistoryQuerySet(BaseQuerySet):
    """WorkflowExecution history queryset"""
    def __init__(self, domain, *args, **kwargs):
        super(HistoryQuerySet, self).__init__(*args, **kwargs)
        self.domain = domain

    def get(run_id, workflow_id, page_size=None, max_results=None, reverse=None):
        reverse = reverse or False
        events = []

        response = self.connection.get_workflow_execution_history(
            self.domain.name,
            run_id,
            workflow_id,
            maximum_page_size=page_size,
            reverse_order=reverse)
        events = response['events']

        next_page = response.get('nextPageToken')
        while next_page is not None and len(events) < max_results:
            response = self.connection.get_workflow_execution_history(
                self.domain.name,
                run_id,
                workflow_id,
                maximum_page_size=page_size,
                next_page_token=next_page,
                reverse_order=reverse
            )
            events.extend(response['events'])
            next_page = response.get('nextPageToken')

        return History.from_event_list(events)
