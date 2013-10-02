from tw2.core import Widget, Param, JSSource
from tg import json_encode


class UIDJSSource(JSSource):
    def __eq__(self, other):
        return self.id == other.id


class RactiveGlobalJSSource(UIDJSSource):
    id = 'RactiveWidgets'
    location = 'head'
    src = '''
document.RAWidgets = {};
document.RAWidgets.display = function(id, WidgetClass, data) {
    var placeholder = document.getElementById(id);
    var parentNode = placeholder.parentNode;
    var widget = document.RAWidgets[id] = new WidgetClass({el: parentNode, append: true, data: data});
    parentNode.insertBefore(parentNode.lastChild, placeholder);
    placeholder.remove();
};
'''


class RactiveTemplateSource(UIDJSSource):
    inline_engine_name = 'genshi'
    template = '''
<script id="${w.id}" type="text/ractive">
    ${w.src}
</script>'''


class RactiveClassSource(UIDJSSource):
    template_id = Param('Ractive template dom id')
    ractive_base = Param('Ractive Base Widget Class', default='Ractive')

    inline_engine_name = 'genshi'
    template = '''
<script>
    var ${w.id} = ${w.ractive_base}.extend({
        template: "#${w.template_id}",
        init: $w.src
    });
</script>
'''


class RactiveWidget(Widget):
    template = '<div xmlns:py="http://genshi.edgewall.org/" py:attrs="w.attrs"/>'
    inline_engine_name = 'genshi'

    ractive_template = Param('The template of the Ractive Widget')
    ractive_init = Param('Ractive initialization function', default='function(options){ if (this._super !== undefined) this._super(options); }')
    ractive_base = Param('Name of the base Ractive class', default='Ractive')
    ractive_class = Param('Name of the Ractive Widget', default=None)


    @classmethod
    def post_define(cls):
        if not hasattr(cls, 'ractive_template'):
            return

        if cls.ractive_class is None:
            cls.ractive_class = cls.__name__

        template_id = '_'.join(('rt_template', cls.ractive_class))

        cls.resources.append(RactiveGlobalJSSource())
        cls.resources.append(RactiveTemplateSource(id=template_id,
                                                   src=cls.ractive_template))
        cls.resources.append(RactiveClassSource(id=cls.ractive_class,
                                                ractive_base=cls.ractive_base,
                                                template_id=template_id,
                                                src=cls.ractive_init))

    @classmethod
    def activate(cls):
        resources = [r.req() for r in cls.resources]
        for r in resources:
            r.prepare()

    def prepare(self):
        super(RactiveWidget, self).prepare()
        self.safe_modify('attrs')
        self.attrs['id'] = self.id

        if self.value is None:
            self.value = {}

        self.safe_modify('resources')
        self.resources.append(JSSource(src='''
document.RAWidgets.display("%(id)s", %(RactiveClass)s, %(value)s);
''' % dict(id=self.id, RactiveClass=self.ractive_class,
           value=json_encode(self.value))))



