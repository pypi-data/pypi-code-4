'''
flask-yamlpage
==============
Flatpages in yaml syntax

app.py
------
    from flask import Flask
    from flask_yamlpage import FlaskYamlPage


    app = Flask(__name__)
    yamlpages = FlaskYamlPage(app)


    @app.route('/')
    def index():
        return 'index'


    if __name__ == '__main__':
        app.run(debug=True, port=8000)


yamlpages/test#.yml
-------------------
    title: test yamlpage
    body: |
        Yamlpage
        ========
        Hello, world!
        {{ url_for('index') }}


templates/yamlpage.html
-----------------------
    <title>{{ page.title }}</title>

    {{ page.body | render | markdown | safe }}


config defaults
---------------
    'YAMLPAGE_CONTENT_DIR'      : './yamlpages',
    'YAMLPAGE_DEFAULT_TEMPLATE' : 'yamlpage.html',
    'YAMLPAGE_AUTO_ROUTING'     : True,
    'YAMLPAGE_MARKDOWN_FILTER'  : True,
    'YAMLPAGE_RENDER_FILTER'    : True,

'''


import flask
import yamlpage


__version__ = '0.0.2'


class FlaskYamlPage(yamlpage.YamlPage):
    defaults = {
        'YAMLPAGE_CONTENT_DIR'      : './yamlpages',
        'YAMLPAGE_DEFAULT_TEMPLATE' : 'yamlpage.html',
        'YAMLPAGE_AUTO_ROUTING'     : True,
        'YAMLPAGE_MARKDOWN_FILTER'  : True,
        'YAMLPAGE_RENDER_FILTER'    : True,
    }

    def __init__(self, app):
        self.app = app
        for k, v in self.defaults.iteritems():
            app.config.setdefault(k, v)
        super(FlaskYamlPage, self).__init__(app.config['YAMLPAGE_CONTENT_DIR'])

        if app.config['YAMLPAGE_AUTO_ROUTING']:
            @app.after_request
            def routing(response):
                if(response.status_code == 404):
                    res = self.render(flask.request.path)
                    if res:
                        return app.make_response(res)
                return response

        if app.config['YAMLPAGE_MARKDOWN_FILTER']:
            import misaka

            @app.template_filter('markdown')
            def markdown_filter(s):
                return misaka.html(s)

        if app.config['YAMLPAGE_MARKDOWN_FILTER']:
            @app.template_filter('render')
            def render_filter(s):
                return flask.render_template_string(s)


    def get_or_404(self, url):
        page = self.get(url)
        if page is None:
            flask.abort(404)
        return page

    def render(self, url):
        page = self.get_or_404(url)
        if page is None:
            return
        template = page.get('template',
                self.app.config['YAMLPAGE_DEFAULT_TEMPLATE'])
        return flask.render_template(template, page=page)
