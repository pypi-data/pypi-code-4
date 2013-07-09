whiffCategory = "logic"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/dictsToSequences - linearize a mappings into a sequences
{{/include}}

The <code>whiff_middleware/dictsToSequences</code>
extracts values for a sequence of keys from a sequence
of mappings and puts them as a sequence in the environment.

{{include "example"}}
{{using targetName}}dictsToSequences{{/using}}
{{using page}}

{{include "whiff_middleware/dictsToSequences"}}
    {{using dicts}}
        [
        {"species":"dog", "name":"dingo"},
        {"species":"cat", "name":"wolfgang"}
        ]
    {{/using}}
    {{using names}} ["name", "species"] {{/using}}
    {{using variable}}myVariable{{/using}}
    {{using page}}
        myVariable = {{get-env myVariable/}}
    {{/using}}
{{/include}}

{{/using}}
{{/include}}

"""

# import must be absolute
from whiff.middleware import misc
from whiff import whiffenv
from whiff import resolver

class dictsToSequences(misc.utility):
    def __init__(self,
                 page,
                 names,
                 dicts,
                 variable,
                 ):
        self.page = page
        self.names = names
        self.dicts = dicts
        self.variable = variable
    def __call__(self, env, start_response):
        names = self.param_json(self.names, env)
        dicts = self.param_json(self.dicts, env)
        variable = self.param_value(self.variable, env)
        variable = variable.strip()
        relativeVariable = whiffenv.getName(env, variable)
        env = env.copy()
        sequences = [ [ dict.get(name) for name in names ] for dict in dicts ]
        env[relativeVariable] = sequences
        return self.deliver_page(self.page, env, start_response)

__middleware__ = dictsToSequences
