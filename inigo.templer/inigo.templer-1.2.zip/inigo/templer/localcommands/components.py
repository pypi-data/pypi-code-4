from templer.core.vars import var
from inigo.templer.localcommands import SubTemplate

class Vocabulary(SubTemplate):
    _template_dir = 'templates/components/vocabulary'
    summary = 'Adds a VocabularyFactory skeleton'

    vars = [
        var('vocabulary_name','Vocabulary name'),
    ]

    def pre(self, command, output_dir, vars):
        vars['vocabulary_filename'] = vars['vocabulary_name'].replace(" ", "_").lower()
        vars['vocabulary_classname'] = vars['vocabulary_name'].replace(' ', '')
