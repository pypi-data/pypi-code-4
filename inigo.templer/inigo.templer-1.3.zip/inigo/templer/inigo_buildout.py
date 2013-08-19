import copy

from templer.buildout import BasicBuildout
from templer.core.vars import StringVar, EASY, EXPERT

from templer.localcommands import SUPPORTS_LOCAL_COMMANDS
from templer.localcommands import LOCAL_COMMANDS_MESSAGE


class InigoBuildout(BasicBuildout):
    _template_dir = 'templates/inigo_buildout'
    summary = 'A Plone buildout with dev/prod cfg, and OpenShift'
    help = ''''''
    post_run_msg = LOCAL_COMMANDS_MESSAGE
    category = 'Plone Development'
    use_cheetah = True
    use_local_commands = True
    required_templates = []
    default_required_structures = []
    vars = copy.deepcopy(BasicBuildout.vars)
