import django.template

def simple_tag(fn):
  def simple_tag(parser, token):
      params = token.split_contents()[1:]
      params = [parser.compile_filter(p) for p in params]

      class Node(django.template.Node):
          def render(self, context):
              paramvals = [p.resolve(context) for p in params]
              return fn(context, *paramvals)
      return Node()
  simple_tag.func_name = fn.func_name
  return simple_tag
