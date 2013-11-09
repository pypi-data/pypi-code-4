#!/usr/bin/python

import argparse, os, re, json

from sh import find

from jinja2 import Template

from pygments import highlight
from pygments.lexers import CheetahJavascriptLexer
from pygments.formatters import HtmlFormatter

parser = argparse.ArgumentParser(description='HTML generator for Dox Documentation')

parser.add_argument('dir', nargs='?', default='.', help='Directory to search for .json files in.')
parser.add_argument('-t', '--title', type=str, default='Untitled Project', help='The project title. Default is "Untitled Project".')
parser.add_argument('-d', '--description', type=str, default='', help='The project description. Default is blank.')
parser.add_argument('-l', '--layout', type=str, choices=['bootstrap'], default='bootstrap', help='The template to render the documentation with. Default is bootstrap.')

args = parser.parse_args()

templates = {}

templates['bootstrap'] = '''
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<title>{{title}}{% if description %} - {{description}}{% endif %}</title>
<link rel="stylesheet" href="http://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.0.0/css/bootstrap.min.css" />
<style>

.hll{background-color:#ffc}.c{color:#998;font-style:italic}.err{color:#a61717;background-color:#e3d2d2}.k{color:#000;font-weight:700}.o{color:#000;font-weight:700}.cm{color:#998;font-style:italic}.cp{color:#999;font-weight:700;font-style:italic}.c1{color:#998;font-style:italic}.cs{color:#999;font-weight:700;font-style:italic}.gd{color:#000;background-color:#fdd}.ge{color:#000;font-style:italic}.gr{color:#a00}.gh{color:#999}.gi{color:#000;background-color:#dfd}.go{color:#888}.gp{color:#555}.gs{font-weight:700}.gu{color:#aaa}.gt{color:#a00}.kc{color:#000;font-weight:700}.kd{color:#000;font-weight:700}.kn{color:#000;font-weight:700}.kp{color:#000;font-weight:700}.kr{color:#000;font-weight:700}.kt{color:#458;font-weight:700}.m{color:#099}.s{color:#d01040}.na{color:teal}.nb{color:#0086B3}.nc{color:#458;font-weight:700}.no{color:teal}.nd{color:#3c5d5d;font-weight:700}.ni{color:purple}.ne{color:#900;font-weight:700}.nf{color:#900;font-weight:700}.nl{color:#900;font-weight:700}.nn{color:#555}.nt{color:navy}.nv{color:teal}.ow{color:#000;font-weight:700}.w{color:#bbb}.mf{color:#099}.mh{color:#099}.mi{color:#099}.mo{color:#099}.sb{color:#d01040}.sc{color:#d01040}.sd{color:#d01040}.s2{color:#d01040}.se{color:#d01040}.sh{color:#d01040}.si{color:#d01040}.sx{color:#d01040}.sr{color:#009926}.s1{color:#d01040}.ss{color:#990073}.bp{color:#999}.vc{color:teal}.vg{color:teal}.vi{color:teal}.il{color:#099}

@media (max-width: 992px) {

    .container {
        width: 970px !important;
        max-width: none !important;
    }
    .col-md-3 {
        width: 25% !important;
        float: left;
    }
    .col-md-9 {
        width: 75% !important;
        float: left;
    }

}

.method {
    margin-bottom: 40px;
}

.permalink {
    position: absolute;
    margin-left: -25px;
    font-weight: normal;
    color: #eee;
}

.permalink:hover {
    color: #666;
    text-decoration: none;
}

.bs-footer {
    margin: 50px auto;
    color: #777;
    text-align: center;
}

</style>
</head>

<body>

<div class="wrap">

    <div class="container">

        <div class="page-header">
            <div class="pull-right">
                <label><input type="checkbox" name="toggle-code" class="toggle-code-blocks" /> Toggle Code Blocks</label><br />
                <label><input type="checkbox" name="toggle-private" class="toggle-private" /> Toggle Private Methods/Function</label>
            </div>
            <h1>{{title}}{% if description %} <small>{{description}}</small>{% endif %}</h1>
        </div>

        <div class="row">

            <div class="col-md-3">

                <ul class="nav">

                {% for nav in navigation %}

                <li class="scope-{{nav.scope}}"><a href="#{{nav.uid}}">{{nav.name}}</a></li>

                {% endfor %}

                </ul>

            </div>

            <div class="col-md-9">

                {% for method in methods %}

                <div class="method scope-{{method.scope}}">

                    <h2 id="{{method.uid}}"><a href="#{{method.uid}}" class="permalink">#</a>{{method.name}} {% if method.scope == "private" %}<span class="label label-default">private</span>{% endif %}</h2>

                    {{method.description}}

                    {% if method.params %}

                    <h3>Parameters</h3>

                    {% for param in method.params %}

                    <p>
                        <b>{{param.name}}</b>
                        <code>{{param.type}}</code>
                        {% if param.optional %}
                        <span class="label label-default">Optional</span>
                        {% endif %}
                    </p>
                    <p>{{param.description}}</p>

                    {% endfor %}

                    {% endif %}

                    {% if method.properties %}

                    <h3>Properties</h3>

                    {% for property in method.properties %}

                    <p><b>{{property.name}}</b> <code>{{property.type}}</code></p>
                    <p>{{property.description}}</p>

                    {% endfor %}

                    {% endif %}

                    {% for key, vars in method.data.iteritems() %}

                    {% if vars %}

                    <h3>{{key|capitalize}}</h3>

                    {% for var in vars %}

                    <p>
                        <b>{{var.name}}</b>
                        <code>{{var.type}}</code>
                        {% if var.optional %}
                        <span class="label label-default">Optional</span>
                        {% endif %}
                    </p>
                    <p>{{var.description}}</p>

                    {% endfor %}

                    {% endif %}

                    {% endfor %}

                    {% if method.examples %}

                    <h3>Examples</h3>

                    {{method.examples}}

                    {% endif %}

                    <div class="code">

                        <h3>Code</h3>

                        {{method.code}}

                    </div>

                    <h3>Returns</h3>

                    <p>{{method.return}}</p>

                </div>

                {% endfor %}

            </div>

        </div>

    </div>

</div>

<footer class="bs-footer">

    <div class="container">

        <p>Documentation generated with <a href="https://github.com/visionmedia/dox">dox</a> and <a href="https://github.com/neogeek/doxdox">doxdox</a>.

    </div>

</footer>

<script src="http://cdnjs.cloudflare.com/ajax/libs/jquery/2.0.3/jquery.min.js"></script>
<script>

(function () {

    var hash = window.location.hash,
        $hash_elem = $('[id="' + hash.replace(/#/, '') + '"]'),
        $code_block = $('.code'),
        $scope_private = $('.scope-private'),
        $toggle_code_blocks = $('.toggle-code-blocks')
        $toggle_private = $('.toggle-private');

    $toggle_code_blocks.on('click', function () {

        if ($toggle_code_blocks.is(':checked')) {
            $code_block.show();
        } else {
            $code_block.hide();
        }

    });

    $toggle_private.on('click', function () {

        if ($toggle_private.is(':checked')) {
            $scope_private.show();
        } else {
            $scope_private.hide();
        }

    });

    $code_block.hide();
    $scope_private.hide();

    if ($hash_elem.length && !$hash_elem.is(':visible')) {

        $toggle_private.trigger('click');

    }

}());

</script>

</body>
</html>
'''

def file_get_contents(file):

    if os.path.isfile(file):

        file = open(file, 'r')
        content = file.read()
        file.close()

        return content

class doxdox:

    navigation = []
    methods = []

    def __init__(self):

        template = Template(templates[args.layout])

        files = find(args.dir, '-type', 'f', '-name', '*.json').strip().split('\n')

        for file in files:
            self.generate(file)

        if len(self.methods):
            print(template.render(title=args.title, description=args.description, navigation=self.navigation, methods=self.methods))

        else:
            parser.print_help()

    def generate(self, file):

        if os.path.isfile(file):

            dox = json.loads(file_get_contents(file))

            for item in dox:

                if 'ignore' in item and item['ignore'] == False and 'ctx' in item:

                    data = {
                        'uid': re.sub(r'[^a-z0-9\.]+', '', item['ctx']['string'].lower()),
                        'name': re.sub(r'\.prototype', '', item['ctx']['string']),
                        'description': item['description']['summary'],
                        'examples': False,
                        'code': False,
                        'params': [],
                        'properties': [],
                        'data': {},
                        'scope': 'public',
                        'return': False
                    }

                    if item['description']['body']:
                        data['examples'] = re.sub(r'<(\/)?(pre|code)>', '', item['description']['body'])
                        data['examples'] = highlight(data['examples'], CheetahJavascriptLexer(), HtmlFormatter())

                    if item['code']:
                        data['code'] = re.sub(r'\n\t', '\n', item['code'])
                        data['code'] = highlight(data['code'], CheetahJavascriptLexer(), HtmlFormatter())

                    if 'tags' in item:

                        for tag in item['tags']:

                            if tag['type'] == 'api':
                                data['scope'] = tag['visibility'].lower()

                            elif tag['type'] == 'return':
                                data['return'] = '<code>' + tag['types'][0] + '</code> ' + tag['description'];

                            else:

                                optional = False

                                if 'types' in tag:
                                    tag['types'] = '|'.join(tag['types'])

                                if 'name' not in tag:
                                    matches = re.findall(r'\{([^\}]+)\} ([^ ]+) (.+$)', tag['string'])
                                    tag['name'] = matches[0][1]
                                    tag['types'] = matches[0][0]
                                    tag['description'] = matches[0][2]

                                if re.search(r'\?$', tag['types']):
                                    optional = True
                                    tag['types'] = re.sub(r'\?$', '', tag['types'])

                                temp = {
                                    'name': tag['name'],
                                    'type': tag['types'],
                                    'description': tag['description'],
                                    'optional': optional
                                }

                                if tag['type'] == 'param':
                                    data['params'].append(temp)

                                elif tag['type'] == 'property':
                                    data['properties'].append(temp)

                                else:

                                    if tag['type'] not in data['data']:
                                        data['data'][tag['type']] = []

                                    data['data'][tag['type']].append(temp)

                    self.navigation.append({ 'uid': data['uid'], 'name': data['name'], 'scope': data['scope'].lower() })

                    self.methods.append(data)

if __name__ == "__main__":

    doxdox()