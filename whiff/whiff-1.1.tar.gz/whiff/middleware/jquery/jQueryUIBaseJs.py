
whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/jquery/jQueryUIBaseJs - jquery support
{{/include}}

The <code>jQueryUIBaseJs</code> middleware provides support for generating
javascript fragments frequently useful for using the <code>jquery</code>
javascript library -- please see the <code>whiff/jquery</code> tutorial for more information.
The <code>jQueryUIBaseJs</code> generates only the javascript -- not the supporting
libraries or the surrounding script tags.
"""


from whiff.middleware import misc
from whiff.middleware import callTemplate

class jQueryUI(misc.utility):
    def __init__(self,
                 targetId,
                 widget,
                 **other_parameters):
        self.targetId = targetId
        self.widget = widget
        self.other_parameters = other_parameters
    def __call__(self, env, start_response):
        targetId = self.param_value(self.targetId, env).strip()
        widget = self.param_value(self.widget, env).strip()
        # generate javascript includes if needed
        #libsApplication = callTemplate.callTemplate("whiff_middleware/jquery/jQueryUILib")
        #libs = self.param_value(libsApplication, env)
        # collect options, events, methods, gets, sets
        options = []
        events = []
        methods = []
        gets = []
        sets = []
        others = self.other_parameters.items()
        others.sort()
        for (name, app) in others:
            appValue = self.param_value(app, env)
            if name.startswith("option_"):
                optionName = name[7:]
                optionText = '%s : %s' % (optionName, appValue)
                options.append(optionText)
            elif name.startswith("event_"):
                eventName = name[6:]
                eventText = '%s : %s' % (eventName, appValue)
                events.append(eventText)
            elif name.startswith("method_"):
                methodName = name[7:]
                methodText = makeMethodText(methodName, appValue, targetId, widget)
                methods.append(methodText)
            elif name.startswith("get_"):
                optionName = name[4:]
                getText = makeGetText(optionName, appValue, targetId, widget)
                gets.append(getText)
            elif name.startswith("set_"):
                optionName = name[4:]
                setText = makeSetText(optionName, appValue, targetId, widget)
                sets.append(setText)
            else:
                raise ValueError, "I don't know what to do with this argument name "+repr(name)
        # yield response
        start_response('200 OK', [('Content-Type', 'application/javascript')])
        # methods (names may be needed in initializer)
        for methodFunction in gets+sets+methods:
            yield methodFunction
            yield ";\n"
        yield '$(function(){\n'
        #yield '    //al("executing initializer");\n'
        yield '    $("#%s").%s ({\n' % (targetId, widget)
        inside = False
        for text in options+events:
            yield '        '
            if inside:
                yield ','
            yield text
            yield '\n'
            inside = True
        yield '    });\n'
        yield '});\n'
        #yield '</script>\n'

def makeGetText(optionName, functionName, targetId, widget):
    D = {}
    D["optionName"] = optionName
    D["functionName"] = functionName
    D["targetId"] = targetId
    D["widget"] = widget
    return """
    var %(functionName)s = function () {
        return $('#%(targetId)s').%(widget)s('option', '%(optionName)s');
    }
    """ % D

def makeSetText(optionName, functionName, targetId, widget):
    D = {}
    D["optionName"] = optionName
    D["functionName"] = functionName
    D["targetId"] = targetId
    D["widget"] = widget
    return """
    function %(functionName)s(optionValue) {
        return $('#%(targetId)s').%(widget)s('option', '%(optionName)s', optionValue);
    }
    """ % D

def makeMethodText(methodName, functionName, targetId, widget):
    D = {}
    D["targetId"] = targetId
    D["widget"] = widget
    D["methodName"] = methodName
    D["functionName"] = functionName
    template = """
    var %(functionName)s = function () {
        var target = $('#%(targetId)s');
        var args = ["%(methodName)s"];
        for (var i=0; i<arguments.length; i++) {
            args.push(arguments[i]);
        }
        return target.%(widget)s.apply(target, args);
    }
    """
    return template % D

__middleware__ = jQueryUI
