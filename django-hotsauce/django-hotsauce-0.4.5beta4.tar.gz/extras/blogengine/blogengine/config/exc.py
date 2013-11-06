"""Common exceptions classes"""

__all__ = ['ObjectDoesNotExist', 'AuthorDoesNotExist']


class ObjectDoesNotExist(Exception):
    pass

class AuthorDoesNotExist(ObjectDoesNotExist): # PermissionError
    pass



