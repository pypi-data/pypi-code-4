"""
Check if we are inside an AuthoringProject
"""

try:
    context.getAuthoringProject()
    return 1
except AttributeError:
    return 0
