import requests


class CodebaseClient(object):

    BASE_URL = 'https://api3.codebasehq.com'

    def __init__(self, username, key):
        self.username = username
        self.key = key
        self.auth = (username, key)

    def _plain_request(self, endpoint, project=None, params={}):
        """
        Helper method for performing the actual request to Codebase API

         endpoint - actual Codebase endpoint like 'project', or 'tickets'
         project - permalink of the project if needed for the request
         params - extra parameters for the request
        """
        if project:
            url = '%s/%s/%s.json' % (self.BASE_URL, project, endpoint)
        else:
            url = '%s/%s.json' % (self.BASE_URL, endpoint)
        return requests.get(
            url,
            params=params,
            auth=self.auth
        ).json()

    def _group_by_id(self, items, key, _id="id"):
        """
        Codebase API returns the results in a really ugly format::

            [{ "event" {actual_information_of_the_event} }, ...]

        This helper methods converts that into something more usable like::

            {id: {actual_information_of_the_event}}

         items - original response
         key - key in which the objects are included, like "event" on above example
         _id - object id which will become the new dict's key
        """
        build = lambda item: (item[key][_id], item[key])
        return dict(map(build, items))

    def _request_by_id(self, endpoint, key, _id='id', project=None, params={}):
        """
        Wraps both _plain_request and _group_by_id methods
        """
        response = self._plain_request(endpoint, project, params)
        return self._group_by_id(response, key, _id)

    def global_activity(self, page=1):
        """
        Request to '/activity.json'. Returns last activity on
        the global account, paginated by 20 elements.
        """
        return self._request_by_id(
            endpoint="activity",
            key="event",
            params={"page": page}
        )

    def activity(self, project, page=1):
        """
        Request to '/<project>/activity.json'.
        Returns latest events for the given project, paginated by 20 elements.
        """
        return self._request_by_id(
            endpoint='activity',
            project=project,
            key="event",
            params={"page": page}
        )

    def all_projects(self):
        """
        Request to '/projects.json'. Returns all the projects in
        the user's domain
        """
        return self._request_by_id(
            endpoint='projects',
            key='project',
            _id='permalink'
        )

    def active_projects(self):
        result = {}
        for key, value in self.all_projects().items():
            if value["status"] == "active":
                result[key] = value

        return result

    def project(self, project):
        """
        Request to '/<project>.json'. Returns all information for
        the given project
        """
        return self._plain_request(endpoint=project)['project']

    def project_groups(self):
        """
        Request to '/project_groups.json'. Returns all the groups for the
        user's domain.
        """
        return self._request_by_id(
            endpoint='project_groups',
            key='project_group'
        )

    def assignments(self, project):
        """
        Request to '/<project>/assignments.json'. Returns all the people
        assigned to the given project
        """
        return self._request_by_id(
            endpoint='assignments',
            project=project,
            key='user',
            _id='username'
        )

    def repositories(self, project):
        """
        Request to '/<project>/repositories.json'. Returns all the repositories
        within the given project
        """
        return self._request_by_id(
            endpoint='repositories',
            project=project,
            key='repository',
            _id='permalink'
        )

    def repository(self, project, repository):
        """
        Request to '/<project>/<repository>.json'. Returns data for
        the given repository
        """
        return self._plain_request(
            endpoint=repository,
            project=project
        )['repository']

    def tickets(self, project, params={}):
        """
        Request to '/<project>/tickets.json'. Returns tickets for the given
        project, paginated by 20.
        """
        return self._request_by_id(
            endpoint='tickets',
            project=project,
            params=params,
            key='ticket',
            _id='ticket_id'
        )

    def all_tickets(self, project, params={}):
        """
        Request to '/<project>/tickets.json'. Returns *all* the tickets
        related with the given project. Use with caution, as it does
        number_of_tickets / 20 requests to Codebase API.

        Apologies for that, but Codebase API doesn't allow to retrieve more
        than 20 tickets per request.
        """
        result = self.tickets(project, params)
        if result:
            _params = params.copy()
            page = _params.get("page", 0)
            _params["page"] = page + 1
            result.update(self.all_tickets(project, _params))
        return result

    def statuses(self, project):
        """
        Request to '/<project>/statuses.json'. Returns all the statuses
        within the given project
        """
        return self._request_by_id(
            endpoint='tickets/statuses',
            project=project,
            key='ticketing_status')

    def priorities(self, project):
        """
        Request to '/<project>/priorities.json'. Returns all the priorities
        within the given project
        """
        return self._request_by_id(
            endpoint='tickets/priorities',
            project=project,
            key='ticketing_priority')

    def categories(self, project):
        """
        Request to '/<project>/categories.json'. Returns all the categories
        within the given project
        """
        return self._request_by_id(
            endpoint='tickets/categories',
            project=project,
            key='ticketing_category')

    def milestones(self, project):
        """
        Request to '/<project>/milestones.json'. Returns all the milestones
        within the given project
        """
        return self._request_by_id(
            endpoint='milestones',
            project=project,
            key='ticketing_milestone')

    def active_milestones(self, project):
        result = {}
        for key, value in self.milestones(project).items():
            if value["status"] == "active":
                result[key] = value

        return result
