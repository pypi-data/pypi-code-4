
#############################################################################################
## Exception
class TaskExtractorJiraCreationError(Exception):
    def __init__(self, arg):
        self.message = arg

class TaskExtractorJiraValidationError(Exception):
    def __init__(self, arg):
        self.message = arg

class TaskExtractorTemplateErrorProject(Exception):
    def __init__(self, arg):
        self.message = arg

class TaskExtractorTemplateErrorJson(Exception):
    def __init__(self, arg):
        self.error_element = arg

class TaskExtractorJiraHostProblem(Exception):
    def __init__(self, arg):
        self.message = arg


