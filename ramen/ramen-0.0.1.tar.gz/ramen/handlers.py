from tornado import web, gen
from tornado.escape import parse_qs_bytes

from pycket.session import SessionMixin
from ramen.pjs import Page



import re
import json

class Path(list):
    @property
    def next(self):
        return self.pop(0)



def wrap(fn):
    def wrap_inner(*args, **kwargs):
        callback = kwargs.pop('callback', lambda x:x)
        return callback(fn(*args, **kwargs))
    return wrap_inner

class Redirect(object):
    def __init__(self, url):
        self.url = url

class Error(object):
    def __init__(self, code):
        self.code = code


class BaseHandler(web.RequestHandler, SessionMixin):

    root_template = 'base.html'
    template_name = ''
    page_context = 'body'
    json_method = unicode
    full_render = False
    context = {}
    no_wrapper = False

    _paginate = {}
    _pages = {}
    _with_wrapper = False

    def initialize(self, *args, **kwargs):
        self.trans = self.application.settings['translators']
        self.lang = self.detect_language()
        self.env = self.application.settings['jinja_env']()
        self.env.install_gettext_translations(self.trans[self.lang], newstyle=True)

    @property
    def db(self):
        return self.application.db

    @property
    def is_ajax(self):
        return self.request.headers.get('X-Requested-With', '').startswith('XMLHttpRequest')

    def collect_titles(self, cls):
        titles = []

        if self.__class__ == cls and hasattr(cls, '_page_title'):
            titles.append(cls._page_title)

        for b in cls.__bases__:
            if hasattr(b, '_page_title'):
                titles.append(b._page_title)

            titles.extend(self.collect_titles(b))
        return titles

    def prepare(self):
        reg_b = re.compile(r"android.+mobile|avantgo|bada\\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\\/|plucker|pocket|psp|symbian|treo|up\\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino", re.I|re.M)
        reg_v = re.compile(r"1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\\-(n|u)|c55\\/|capi|ccwa|cdm\\-|cell|chtm|cldc|cmd\\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\\-s|devi|dica|dmob|do(c|p)o|ds(12|\\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\\-|_)|g1 u|g560|gene|gf\\-5|g\\-mo|go(\\.w|od)|gr(ad|un)|haie|hcit|hd\\-(m|p|t)|hei\\-|hi(pt|ta)|hp( i|ip)|hs\\-c|ht(c(\\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\\-(20|go|ma)|i230|iac( |\\-|\\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\\/)|klon|kpt |kwc\\-|kyo(c|k)|le(no|xi)|lg( g|\\/(k|l|u)|50|54|e\\-|e\\/|\\-[a-w])|libw|lynx|m1\\-w|m3ga|m50\\/|ma(te|ui|xo)|mc(01|21|ca)|m\\-cr|me(di|rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\\-2|po(ck|rt|se)|prox|psio|pt\\-g|qa\\-a|qc(07|12|21|32|60|\\-[2-7]|i\\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\\-|oo|p\\-)|sdk\\/|se(c(\\-|0|1)|47|mc|nd|ri)|sgh\\-|shar|sie(\\-|m)|sk\\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\\-|v\\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\\-|tdg\\-|tel(i|m)|tim\\-|t\\-mo|to(pl|sh)|ts(70|m\\-|m3|m5)|tx\\-9|up(\\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|xda(\\-|2|g)|yas\\-|your|zeto|zte\\-", re.I|re.M)
        user_agent = self.request.headers.get('User-Agent', '')
        self.is_mobile = bool(reg_b.search(user_agent) or reg_v.search(user_agent[0:4])) or int(self.arguments.get('mode', 1024)) < 767

    def context(self):
        return {
            't': self.path_list,
            'domain': self.application.settings['domain'],
            'lang': self.lang,
            'is_ajax': self.is_ajax,
            'path': self.request.path,
            'link_up': self.link_up,
            'is_mobile': self.is_mobile
        }

    def page(self):
        return Page('$', self.page_context, self.arguments, self.is_mobile, path=self.request.path, back=self.link_up)

    @property
    def arguments(self):
        arguments = {}

        if self.request.method == 'GET':
            query = self.request.query
        else:
            query = self.request.body

        for key, value in parse_qs_bytes(query, keep_blank_values=True).items():

            value = [x.decode('utf-8') for x in value]

            v = value
            if key.endswith('[]'):
                key = key[:-2]
            else:
                v = value[0]
            td = arguments
            parts = key.split('[')
            for i, tkey in enumerate(parts):
                tkey = tkey.strip('[]')
                if i+1 < len(parts):
                    td = td.setdefault(tkey, {})
            try:
                td[key.split('[')[-1].strip('[]')] = v
            except:
                pass

        return arguments

    @property
    def link_up(self):
        parts = self.request.path.split('/')
        if len(parts) > 2:
            parts.pop(-2)
        return '/'.join(parts)

    def can_get(self, context):
        return True

    def can_post(self, context):
        return True

    def can_put(self, context):
        return True

    def can_delete(self, context):
        return True

    def do_get(self, context):
        return {}

    def do_post(self, context):
        return True, {}

    def do_put(self, context):
        return True, {}

    def do_delete(self, context):
        return True, {}

    def do_get_page(self, page, context):
        return page

    def do_post_page(self, page, context):
        return page

    def do_put_page(self, page, context):
        return page

    def do_delete_page(self, page, context):
        return page

    @gen.engine
    @web.asynchronous
    @web.addslash
    def get(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        self.add_header('Pragma', 'no-cache')
        self.add_header('Expires', '0')
        self.add_header('Cache-Control', 'must-revalidate, post-check=0, pre-check=0')

        if self.lang_redirect:
            self.redirect('/%s%s' % (self.lang, self.request.uri))
        else:

            self.session['lang'] = self.kwargs.get('lang', self.lang)
            if self.kwargs.get('city_name'):
                self.session['city'] = self.kwargs.get('city_name')

            accept = self.request.headers.get('Accept', 'text/html')

            context = yield gen.Task(wrap(self.context))
            can = yield gen.Task(wrap(self.can_get), context = context)
            if isinstance(can, Redirect):
                self.redirect(can.url)
            elif isinstance(can, Error):
                self.send_error(can.code)
            else:
                response_context = yield gen.Task(wrap(self.do_get), context = context)
                title = []

                page_no = self.get_page_no()
                for key, page_size in self._paginate.items():
                    if key in response_context:
                        response_context[key].skip((page_no - 1) * page_size).limit(page_size)

                if isinstance(response_context, Redirect):
                    self.redirect(response_context.url)
                elif isinstance(response_context, Error):
                    self.send_error(response_context.code)
                else:
                    if 'application/javascript' in accept:
                        context.update(response_context)
                        page = yield gen.Task(wrap(self.do_get_page), page = self.page(), context = context)
                        page.title(context['page_title'])
                        self.finish(page.render())

                    elif 'application/json' in accept:
                        self.json(response_context)
                    else:
                        context.update(response_context)
                        if self.is_ajax and not self.full_render:
                            self.finish(self.render_string(self.template_name, **context))
                        else:
                            self.finish(self.render_string(self.root_template, **context))

    @gen.engine
    @web.asynchronous
    def post(self, *args, **kwargs):
        self.add_header('Pragma', 'public')
        self.add_header('Expires', '0')
        self.add_header('Cache-Control', 'must-revalidate, post-check=0, pre-check=0')

        if self.arguments.get('_action') == 'delete':
            self.delete(*args, **kwargs)
            return

        self.args = args
        self.kwargs = kwargs

        accept = self.request.headers.get('Accept', 'text/html')

        context = yield gen.Task(wrap(self.context))
        can = yield gen.Task(wrap(self.can_post), context = context)
        if isinstance(can, Redirect):
            self.redirect(can.url)
        elif not can:
            self.send_error(403)
        else:
            response_result, response_context = yield gen.Task(wrap(self.do_post), context = context)

            if isinstance(response_result, Error):
                self.send_error(response_result.code)
            else:

                if 'application/javascript' in accept:
                    context.update(response_context)
                    page = yield gen.Task(wrap(self.do_post_page), page = self.page(), context = context)
                    self.finish(page.render())

                elif 'application/json' in accept:
                    if isinstance(response_result, Redirect) or response_result == True:
                        response_context['_success'] = True
                        self.json(response_context)
                    else:
                        response_context['_success'] = False

                        if isinstance(response_result, dict):
                            response_context['_errors'] = response_result

                        self.json(response_context)

                else:
                    if isinstance(response_result, Redirect):
                        self.redirect(response_result.url)
                    else:
                        context.update(response_context)
                        self.finish(self.render_string(self.root_template, **context))

    @gen.engine
    @web.asynchronous
    def put(self, *args, **kwargs):

        self.add_header('Pragma', 'public')
        self.add_header('Expires', '0')
        self.add_header('Cache-Control', 'must-revalidate, post-check=0, pre-check=0')

        self.args = args
        self.kwargs = kwargs

        accept = self.request.headers.get('Accept', 'text/html')

        context = yield gen.Task(wrap(self.context))
        can = yield gen.Task(wrap(self.can_put), context = context)
        if isinstance(can, Redirect):
            self.redirect(can.url)
        elif not can:
            self.send_error(403)
        else:
            response_result, response_context = yield gen.Task(wrap(self.do_put), context = context)

            if 'application/javascript' in accept:
                context.update(response_context)
                page = yield gen.Task(wrap(self.do_put_page), page = self.page(), context = context)
                self.finish(page.render())

            elif 'application/json' in accept:
                if isinstance(response_result, Redirect) or response_result == True:
                    response_context['_success'] = True
                    self.json(response_context)
                else:
                    response_context['_success'] = False

                    if isinstance(response_result, dict):
                        response_context['_errors'] = response_result

                    self.json(response_context)

            else:
                if isinstance(response_result, Redirect):
                    self.redirect(response_result.url)
                else:
                    context.update(response_context)
                    self.finish(self.render_string(self.root_template, **context))

    @gen.engine
    @web.asynchronous
    def delete(self, *args, **kwargs):

        self.add_header('Pragma', 'public')
        self.add_header('Expires', '0')
        self.add_header('Cache-Control', 'must-revalidate, post-check=0, pre-check=0')

        self.args = args
        self.kwargs = kwargs

        accept = self.request.headers.get('Accept', 'text/html')

        context = yield gen.Task(wrap(self.context))
        can = yield gen.Task(wrap(self.can_delete), context = context)
        if isinstance(can, Redirect):
            self.redirect(can.url)
        elif not can:
            self.send_error(403)
        else:
            response_result, response_context = yield gen.Task(wrap(self.do_delete), context = context)

            if 'application/javascript' in accept:
                context.update(response_context)
                page = yield gen.Task(wrap(self.do_delete_page), page = self.page(), context = context)
                self.finish(page.render())

            elif 'application/json' in accept:
                if isinstance(response_result, Redirect) or response_result == True:
                    response_context['_success'] = True
                    self.json(response_context)
                else:
                    response_context['_success'] = False

                    if isinstance(response_result, dict):
                        response_context['_errors'] = response_result

                    self.json(response_context)

            else:
                if isinstance(response_result, Redirect):
                    self.redirect(response_result.url)
                else:
                    context.update(response_context)
                    self.finish(self.render_string(self.root_template, **context))

    def __init__(self, *args, **kwargs):

        self.namespaces = kwargs.pop('namespaces', [])
        self.lang_redirect = kwargs.pop('lang_redirect', False)

        self.path_list = Path([])
        path = ''

        for namespace in self.namespaces:
            path = '%s%s/' % (path, namespace)
            self.path_list.append('%s_wrapper.html' % path)

        self.path_list.append(self.template_name)
        super(BaseHandler, self).__init__(*args, **kwargs)

    def detect_language(self):
        locales = []
        default = 'en'
        parts = self.request.path.split('/')[1:-1]
        if parts and len(parts[0]) == 2 and parts[0] in self.trans:
            default = parts[0]
        elif self.session.get('lang'):
            default = self.session.get('lang')
        else:
            if "Accept-Language" in self.request.headers:
                languages = self.request.headers["Accept-Language"].split(",")
                for language in languages:
                    parts = language.strip().split(";")
                    if len(parts) > 1 and parts[1].startswith("q="):
                        try:
                            score = float(parts[1][2:])
                        except (ValueError, TypeError):
                            score = 0.0
                    else:
                        score = 1.0
                    locales.append((parts[0].split('-')[0], score))
                if locales:
                    locales.sort(key=lambda (l, s): s, reverse=True)

            for code, score in locales:
                if code in self.trans:
                    default = code
                    self.session['locale'] = code
                    break

        return default

    def get_page_no(self):
        return int(self.arguments.get('page', self.kwargs.get('page', 1)))

    def json(self, data):
        self.add_header('Content-Type', 'application/json')
        self.finish(self.to_json(data))

    def to_json(self, data):
        return json.dumps(data, default=self.json_method)

    def from_json(self, data):
        return json.loads(data)

    def render_string(self, template_name, **kwargs):
        new_template = self.env.get_template(template_name)
        return new_template.render(**kwargs)

