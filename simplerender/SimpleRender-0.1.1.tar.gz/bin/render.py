import argparse
#from SimpleRender import template

def main():
    #start parse command line arguments
    parser = argparse.ArgumentParser(description='Merge config and template files with the mustache templating engine.')
    parser.add_argument('config', help='The config file (JSON format)')
    parser.add_argument('template', help='The template file')
    parser.add_argument('-o', '--out', nargs='?',
                       help='The output file')

    args = parser.parse_args()
    #end parse command line arguments

    template.Template.render(args.config, args.template, args.out)
    

if __name__ == "__main__":
    main()