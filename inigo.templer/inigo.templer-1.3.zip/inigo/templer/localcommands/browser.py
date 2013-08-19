from templer.core.vars import var
from inigo.templer.localcommands import SubTemplate

class Viewlet(SubTemplate):
    _template_dir = 'templates/browser/viewlet'
    summary = 'Adds an a Viewlet skeleton'

    vars = [
        var('viewlet_name', 'Viewlet name'),
        var('viewlet_manager', 'Viewlet manager', default='IBelowContentTitle'),
    ]

    def pre(self, command, output_dir, vars):
        vars['viewlet_filename'] = vars['viewlet_name'].replace(" ", "_").lower()
        vars['viewlet_classname'] = vars['viewlet_name'].replace(' ', '')
        vars['package_dashed_name'] = vars['package_dotted_name'].replace('.', '-')


class View(SubTemplate):
    _template_dir = 'templates/browser/view'
    summary = 'Adds a simple browserview'

    vars = [
        var('view_name', 'View name')
    ]

    def pre(self, command, output_dir, vars):
        vars['view_filename'] = vars['view_name'].replace(" ", "").lower()
        vars['view_classname'] = vars['view_name'].replace(' ', '')
