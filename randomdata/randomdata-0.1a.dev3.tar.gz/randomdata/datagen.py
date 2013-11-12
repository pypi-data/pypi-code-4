"""
datagen.py
@author RNDuldulao, Jr.
@version 0.1

"""
import math
import os
import randomdata.generators as rdgen


def _generate_data(generators, fformat):
    """Returns one line of data"""
    items = [ gen.generate() for gen in generators ]
    if fformat.lower() == 'csv':
        return ','.join([ '\"%s\"' % str(i) for i in items]) + os.linesep 
    return None



def main(generators=None, items=100, files=1, filepref='datagen', 
         fformat='csv', outputdir='.'):
    """
    datagen main
    """
    i_count = 0
    lines_per_file = math.ceil( items / files )
    for i in xrange(files):
        filename = '%s/%s_%06d.%s' % (outputdir, filepref, i, fformat)
        with open(filename, 'w') as datafile:
            for _ in xrange(int(lines_per_file)):
                datafile.write( _generate_data(generators, fformat))
                i_count += 1
                if i_count == items:
                    break  

if __name__ == '__main__':
    import argparse
    import imp

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--specfile",
        help="File path where the data speclist is described", 
        default='./spec.conf')
    parser.add_argument("-l", "--lines", 
        help="Number of data lines to generate", 
        default=100, type=int)
    parser.add_argument("-f", "--files", 
        help="Number of files to distribute the lines to", 
        default=1, type=int)
    parser.add_argument("-p", "--prefix", 
        help="Filename prefix of generated files", 
        default='datagen')
    parser.add_argument("-d", "--outputdir", 
        help='Output directory', default='.')
    parser.add_argument("-t", "--type", 
        help='Output file type', choices=['csv'], default='csv')
    args = parser.parse_args()
    speclist = []
    with open(args.specfile) as specfile:
        for line in specfile:
            if not line.strip() or line.strip().startswith('#'):
                continue

            spec = [ s.strip() for s in line.split(',', 2)]
            genclass = spec[1]
            cls = None
            params = None
            if (spec[2:]):
                if (spec[2].strip().startswith('{') and
                    spec[2].strip().endswith('}')):
                    params = eval(spec[2])
                else:
                    raise ValueError('%s should be enclosed in { }' % spec[2])
            
            if '.' in genclass:  #if generator class name is fully qualified
                i = genclass.rfind('.')
                mname, clsname = genclass[:i], genclass[i+1:]
                fn, path, desc = imp.find_module(mname)
                module = imp.load_module(mname, fn, path, desc)
                cls = getattr(module, clsname)
            else:                #builtin generator
                cls = getattr(rdgen, genclass)
            if not issubclass(cls, rdgen.Generator):
                raise ValueError('%s is not a Generator subclass' % str(cls))

            if params:
                speclist.append(cls(**params))
            else:
                speclist.append(cls())

    main(speclist, items=args.lines, files=args.files, filepref=args.prefix,
         fformat = args.type, outputdir = args.outputdir)

