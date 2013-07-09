
whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/ofc/OpenFlashChart - generate Flash chart
{{/include}}

The <code>whiff_middleware/OpenFlashChart</code>
middleware formats an
<a href="http://teethgrinder.co.uk/open-flash-chart-2/">Open Flash Chart (version 2)
[http://teethgrinder.co.uk/open-flash-chart-2/]</a>.
All required components for the chart widget come pre-packaged with the WHIFF distribution.

{{include "iframeExample"}}

{${env whiff.content_type: "text/html"/}$}

{${include "whiff_middleware/ofc/OpenFlashChart"}$}

{
  "width": 400,
  "height": 200,
  "elements": [
    {
      "type": "bar",
      "values": [
        9,
        8,
        7,
        6,
        5,
        4,
        3,
        2,
        1
      ]
    }
  ],
  "title": {
    "text": "Wed Sep 02 2009"
  }
}

{${/include}$}

{{/include}}
"""

from whiff.middleware import misc
from whiff.middleware import insertIfNeeded
from whiff import gateway
from whiff import whiffenv
from whiff.rdjson import jsonParse
import types

class OpenFlashChart(misc.utility):
    def __init__(self, page=None, height=None, width=None, **other_args):
        self.page = page
        self.height = height
        self.width = width
        self.other_args = other_args
    def add_env_defaults(self, env, page):
        """
        add environment overrides if missing.
        For example default title in
            env["ofc.title.text"] = "my title"
        only if the title isn't specified elsewhere
        """
        prefix = "ofc." # xxxx this should be a parameter...
        lprefix = len(prefix)
        # find entries that start with prefix
        for (name, value) in env.items():
            if name.startswith(prefix):
                remainder = name[lprefix:]
                sname = remainder.split(".")
                self.add_default(sname, value, page)
    def add_default(self, names, value, dictionary):
        #pr "add_default", (names, value, dictionary.keys())
        lnames = len(names)
        assert len(names)>0, "names cannot be empty"
        firstname = names[0]
        if lnames==1:
            # install the default value only if no value is present
            if not dictionary.has_key(firstname):
                #pr "setting", (firstname, value), dictionary.keys()
                dictionary[firstname] = value
            # otherwise ignore the default
        else: # lnames>1, add default in dictionary component
            firstdict = dictionary.get(firstname)
            if firstdict is None:
                firstdict = dictionary[firstname] = {}
            self.add_default(names[1:], value, firstdict)
            #pr "added sub-component", dictionary.keys()
    def __call__(self, env, start_response):
        page = self.param_json(self.page, env)
        if page is None:
            page = {}
        height = self.param_json(self.height, env)
        width = self.param_json(self.width, env)
        assert type(page) is types.DictType, \
               "page should be a json dictionary "+repr(type(page))
        other_args = {}
        # other args override JSON page values
        for (name, value) in self.other_args.items():
            # XXXX maybe interpret non-json value as simple string?
            page[name] = self.param_json(value, env)
        # XXXX later add additional dictionary entries from environment
        #pr "before", page.keys()
        self.add_env_defaults(env, page)
        #pr "after", page.keys()
        # check height and width
        if height is None:
            height = page.get("height")
            if height:
                del page["height"]
        if width is None:
            width = page.get("width")
            if width:
                del page["width"]
        if type(height) is not types.IntType:
            raise ValueError, "chart height must be specified as an integer "+repr(height)
        if type(width) is not types.IntType:
            raise ValueError, "chart width must be specified as an integer "+repr(width)
        # derive html fragment substitutions
        substitutions = {}
        # add the swfobject library and other javascript if not added yet
        swfobject_js = whiffenv.absPath(env, "whiff_middleware/ofc/swfobject.js") # this may get a bit redundant
        additional = ADDITIONAL_JAVASCRIPT_TEMPLATE % {
            "swfobject_js": swfobject_js}
        addApp = insertIfNeeded.__middleware__(text=additional,
                                               doneFlag="OpenFlashChart.swfobject")
        additional_javascript = self.param_value(addApp, env)
        # find the flash library location
        open_flash_chart_swf = whiffenv.absPath(env, "whiff_middleware/ofc/open-flash-chart.swf")
        # get the data as a json dictionary formatted in a json string
        jsonData = jsonParse.format(page, readable=False)
        data = jsonParse.format(jsonData)
        target_div_id = gateway.getResource(env, ["freshName", "OFCdiv"])
        data_function = gateway.getResource(env, ["freshName", "OFCdata"])
        substitutions["additional_javascript"] = additional_javascript
        substitutions["open_flash_chart_swf"] = open_flash_chart_swf
        substitutions["target_div_id"] = target_div_id
        substitutions["data_function"] = data_function
        substitutions["height"] = height
        substitutions["width"] = width
        substitutions["data"] = data
        # generate the html fragment
        fragment = HTML_FRAGMENT_TEMPLATE % substitutions
        return self.deliver_page(fragment, env, start_response)

ADDITIONAL_JAVASCRIPT_TEMPLATE = """
<script type="text/javascript" src="%(swfobject_js)s"></script>
<script type="text/javascript">
function ofc_ready() {
    // alert("ofc_ready called"); // for debugging...
}
</script>

"""

HTML_FRAGMENT_TEMPLATE = """

%(additional_javascript)s

<script type="text/javascript">
swfobject.embedSWF(
    "%(open_flash_chart_swf)s",
    "%(target_div_id)s",
    %(width)s,
    %(height)s,
    "9.0.0",
    "expressInstall.swf", // xxxx huh?
    {"get-data": "%(data_function)s"}
)

function %(data_function)s () {
    return %(data)s;
}
</script>

<div id="%(target_div_id)s">
If this text isn't replaced a chart<br>
failed to load.<br>
You may need to upgrade your flash player.
</div>
"""

__middleware__ = OpenFlashChart
