whiffCategory = "formatting"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/sortTable - tool for building tables with sorted rows
{{/include}}

The <code>whiff_middleware/sortTable</code>
middleware uses cgi arguments and environment entries
to prepare input data for a table with rows sorted by
one of the column values

{{include "example"}}
{{using targetName}}sortTable{{/using}}
{{using page}}
<pre>
{{include "whiff_middleware/sortTable"}}
    {{set-id Data}}
        [
            {"fn": "armand", "ln": "withers"},
            {"fn": "chris", "ln": "cooty"},
            {"fn": "sandy", "ln": "mango"},
            {"fn": "lou", "ln": "lemon"},
            {"fn": "nick", "ln": "apple"}
        ]
    {{/set-id}}
    {{set-cgi "sort_col"}}ln{{/set-cgi}}
    {{using page}}
        {{get-id Data/}}
    {{/using}}
{{/include}}
</pre>
{{/using}}
{{/include}}

"""
# import must be absolute
from whiff.middleware import misc
from whiff import whiffenv
from whiff import resolver

class sortTable(misc.utility):
    def __init__(self,
                 page):
        self.page = page
    def __call__(self, env, start_response):
        env = resolver.process_cgi(env, parse_cgi=True)
        cgi_parameters = env[whiffenv.CGI_DICTIONARY]
        data = whiffenv.getId(env, "Data")
        sort_cols = cgi_parameters.get("sort_col")
        if not data:
            raise ValueError, "sortTable requires environment argument 'Data'"
        if not sort_cols:
            raise ValueError, "sortTable requires cgi argument 'sort_col'"
        sort_col = sort_cols[0]
        # interpret the cgidata as json (if needed)
        data = self.param_json(data, env)
        start = 0
        starts = cgi_parameters.get("start")
        if starts:
            start = int(starts[0])
        end = len(data)
        ends = cgi_parameters.get("end")
        if ends:
            end = int(ends[0])
        reverses = cgi_parameters.get("reverse")
        reverse = False
        if reverses:
            # parse reverse as json (should be true or false)
            reverse = self.param_json(reverses[0], env)
        sortingList = [ (d.get(sort_col), d) for d in data ]
        sortingList.sort()
        newdata = [ d for (x, d) in sortingList ]
        if reverse:
            newdata.reverse()
        newdata = newdata[start:end]
        whiffenv.setId(env, "Data", newdata)
        return self.deliver_page(self.page, env, start_response)

__middleware__ = sortTable
