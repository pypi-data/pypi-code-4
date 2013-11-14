class NaverCafe(object):
    """
    *Note: not implemented yet*.

    Implementation for `Naver Cafe`_. It accepts the following
    configuration options: ``username``, ``password``, ``cafe_ids``.

    ``username`` and ``password`` are your Naver username and password.
    They are needed to view posts in private cafes that restrict access
    from anonymous users or non-member users.

    ``cafe_ids`` is a list of identifiers of cafes to watch. The identifier of
    a cafe can be found in its URL after ``http://cafe.naver.com/``.
    Restricting the scope to individual boards in a cafe rather than
    the entire cafe is not supported for now, but it may be implemented in a
    future release.

    .. _`Naver Cafe`: http://cafe.naver.com/

    """

    def __init__(self, config):
        self.config = config
        # TODO implement

    def get_new_posts(self):
        # TODO implement
        return []
