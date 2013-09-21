# FTree.py - file for generating text tree from a os.walk output
from os import walk, sep
from os.path import basename
from argparse import ArgumentParser

def prettify(path, file):

    folder_found = '\x1B[31;40m' if not file else ""
    file_found = '\x1B[32;40m' if not file else ""
    end = "\x1B[0m" if not file else ""
    
    output = ""
    
    for root, dirs, files in walk(path):
        level = root.replace(path, '').count(sep)
        indent = ' ' * 4 * level
        output+='{}{}{}/{}'.format(folder_found, indent, basename(root), end)+"\n"
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            output+='{}{}'.format(subindent, f)+"\n"
           
    return output        
            
def FTree(path, file):

    output = prettify(path, file)
    if file:
        try:
            f = open(file, "wb")
        except:
            print "Error opening file."
            print output
        else:
            f.write(output)
            f.close()
            print "written"
            
    else:
        print(output)
    
def main():
    from os import getcwd
    parser = ArgumentParser(None, "%s [-p <path> -f <file>]"%__file__, description="Generate a file tree from given path. If file not specified, output will be printed to the screen.")
    parser.add_argument("-p", "--path", default=getcwd(), help="Path for scanning.")
    parser.add_argument("-f", "--file", help="File where output will be stored (optional).")
    del getcwd
    args = parser.parse_args()
    FTree(args.path, args.file)
    
if __name__ == "__main__":
    main()
