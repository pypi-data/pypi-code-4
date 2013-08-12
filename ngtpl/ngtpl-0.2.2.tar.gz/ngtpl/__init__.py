#!/usr/bin/env python


def wrapper_html(data, id, type="text/ng-template"):
    return """<script type="%s" id="/%s">\n%s\n</script>""" % (
        type, id, data
    )


def wrapper_jinja2(*args, **kwargs):
    html = wrapper_html(*args, **kwargs)

    return """{%% raw -%%}\n%s\n{%%- endraw -%%}""" % (html,)


def main():
    import argparse
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument('templates', nargs='+',
                        help='The templates to collect.')
    parser.add_argument('-w', '--wrapper', choices=['html', 'jinja2'],
                        default='html')
    args = parser.parse_args()

    wrapper_func = globals()['wrapper_' + args.wrapper]
    buf = []
    for tplfn in args.templates:
        buf.append(wrapper_func(open(tplfn).read(),
                                os.path.basename(tplfn)))

    print '\n\n'.join(buf)
