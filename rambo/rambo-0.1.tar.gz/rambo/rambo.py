import subprocess
import os
import sys
import argparse

config = {
    'input_dir': 'images/sprites',
    'output_dir': 'images',
    'output_file': '_sprites.scss',
    'css_output_dir': 'css',
    'test_page': 'test_page.html',
    'test_page_dir': 'site',
    'sass_output_dir': 'sass/sprites'
}

def parse_args(args=None):
        d = '\033[32mAutomatically create sprites from a directory.\nIt assumes your structure is something like: \n\n[images] \n\t[sprites]\n\t\t[sprite-name]\n\t\t\timage-file.png\n\t\t\timage-file-2.png\n\t\t[sprite-name-2x]\n\t\t\timage-file.png  \n\nRight now, this is pretty beta. It assumes you\'re using SaSS.\nBut you can just re-name the output file if you want.    \033[0m'
        parser = argparse.ArgumentParser(description=d, formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('--input',
                            help='\033[90mInput directory, \033[34mimages/sprites\033[0m',
                            default=config['input_dir']
                            )
        parser.add_argument('--output',
                            help='\033[90mOutput directory, \033[34mimages/\033[0m',
                            default=config['output_dir']
                            )

        parser.add_argument('--cssfile',
                            help='\033[90mCSS filename, \033[34m_sprites.scss\033[0m',
                            default=config['output_file']
                            )
        parser.add_argument('--csspath',
                            help='\033[90mCSS output path, \033[34mcss\033[0m',
                            default=config['css_output_dir']
                            )
        parser.add_argument('--sasspath',
                            help='\033[90mSaSS output path,  \033[34msass/sprites\033[0m',
                            default=config['sass_output_dir']
                            )
        parser.add_argument('--testpage_dir',
                            help='\033[90mCheat sheet dir, \033[34msite/\033[0m',
                            default=config['test_page_dir']
                            )
        parser.add_argument('--testpage_name',
                            help='\033[90mCheat sheet, \033[34mcheat_sheet.html\033[0m',
                            default=config['test_page']
                            )
        return parser.parse_args(args)

# Main app 
def main(args=None):
    args = parse_args(args)

    if sys.version_info[0] != 2 or sys.version_info[1] < 6:
        print("This script requires Python version 2.6 or newer")
        sys.exit(1)

    path = os.path.dirname(os.path.realpath(__file__))
    subprocess.call([path + '/sprites.sh', "--input", args.input, "--output", args.output, "--css", args.csspath, "--sass", args.sasspath, "--file", args.cssfile, "--testpage_dir", args.testpage_dir, "--testpage_name", args.testpage_name])


# Boot it!
if __name__ == '__main__':    
    sys.exit(main())