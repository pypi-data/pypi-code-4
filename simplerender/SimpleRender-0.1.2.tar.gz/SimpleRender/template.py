import pystache, json, sys

class Template:

    @staticmethod
    def render(configFile, templateFile, outputFile=None):

        f = open(templateFile, 'r')
        template = f.read()

        data = open(configFile, 'r')

        if (outputFile is not None):
            sys.stdout = open(outputFile, 'w')

        print pystache.render(template, json.load(data))

        data.close()
        f.close()