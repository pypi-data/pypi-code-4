import polib
import argparse
import sys

# take an input po and convert it back to a xtb
argparser = argparse.ArgumentParser()
argparser.add_argument('input')
argparser.add_argument('-l','--language', help="Language code to output")

from clover.command import Command

class ConvertPO(Command):
    def start(self, args):
        parsed_args = argparser.parse_args(args)
        po = polib.pofile(parsed_args.input)

        string = ['<translationbundle lang="%s">\n' % parsed_args.language]
        for entry in po:
            id, name = entry.msgid.split('___')
            message = entry.msgstr

            occurance = None

            if getattr(entry, 'occurrences', []):
                # get the path of the first occurance
                occurance = entry.occurrences[0][0]
                string.append('<translation id="%s" name="%s" source="%s">%s</translation>\n' % (id, name, occurance, message))
            else:

                string.append('<translation id="%s" name="%s">%s</translation>\n' % (id, name, message))

        string.append('</translationbundle>\n')

        print ''.join(string)

if __name__ == '__main__':
    ConvertPO.run(sys.argv[1:])