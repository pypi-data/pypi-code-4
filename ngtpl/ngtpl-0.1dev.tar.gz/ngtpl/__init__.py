#!/usr/bin/env python


def wrap_template(data, id, type="text/ng-template"):
    return """<script type="%s" id="%s">\n%s\n</script>""" % (
        type, id, data
    )


def main():
    import argparse
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument('templates', nargs='+',
                        help='The templates to collect.')
    args = parser.parse_args()

    buf = []
    for tplfn in args.templates:
        buf.append(wrap_template(open(tplfn).read(),
                                 os.path.basename(tplfn)))

    print '\n\n'.join(buf)
