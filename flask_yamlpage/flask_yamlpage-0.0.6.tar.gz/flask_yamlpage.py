import flask
import yamlpage


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
                    url = flask.request.path
                    res = self.render(url)
                    if res:
                        return app.make_response(res)
                    redirect_url = None
                    if url.endswith('/'):
                        if url != '/':
                            redirect_url = url[:-1]
                    else:
                        redirect_url = url + '/'
                    if redirect_url and self.exists(redirect_url):
                        return flask.redirect(redirect_url)
                return response

        if app.config['YAMLPAGE_MARKDOWN_FILTER']:
            import misaka

            @app.template_filter('markdown')
            def markdown_filter(s):
                return misaka.html(s)

        if app.config['YAMLPAGE_MARKDOWN_FILTER']:
            @app.template_filter('render')
            def render_filter(s):
                if '{{' in s or '{%' in s:
                    return flask.render_template_string(
                        s, **flask.g.yamlpage_context)


    def get_or_404(self, url):
        page = self.get(url)
        if page is None:
            flask.abort(404)
        return page

    def render(self, url):
        page = self.get(url)
        if page is None:
            return
        template = page.get('template',
                self.app.config['YAMLPAGE_DEFAULT_TEMPLATE'])
        context = {'page': page}
        flask.g.yamlpage_context = context
        return flask.render_template(template, **context)
