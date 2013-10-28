from newsstand_db import newsstandDB as ndb
from glob import glob
import argparse
from sqlite3 import ProgrammingError


def newsstanddb_create():
    parser = argparse.ArgumentParser(description='Create a DB.')
    parser.add_argument('filename', help='the filename of the database')
    
#     print '\n'
#     parser.print_help()
#     print '\n'
    
    args = parser.parse_args()
    
    filename = args.filename
        
    try:
        db = ndb(filename)
        db.createDB()
    except IOError:
        print 'Unable to createDB'
        
    print "\n== Database creation was successful ==\n"
        
def newsstanddb_import():
    parser = argparse.ArgumentParser(description='Import files into the DB.')
    parser.add_argument('filename', help='the file(s) to import', nargs='+')
    
    print '\n'
    parser.print_help()
    print '\n'
    
    args = parser.parse_args()
    
    try:
        db = ndb(newsstanddb_getdbfile())
    except IOError:
        print 'Couldn\'nt connect to DB'
        
    files = args.filename
    count = len(files)
    try:
        db.multiImport(*files)
    except ProgrammingError as e:
        print "Some files could not be imported: {0}".format(e.message,)
        count -= len(e.message.split(','))
    except:
        raise #TODO: Better exception handling
    
    print "\n== Import Successful (%i file(s) imported) ==\n" % (count,)

def newsstanddb_autoupdate(): #basedir='.',pattern=('N_D_W*','O_S_W*'),outputFile='stats.md'
    parser = argparse.ArgumentParser(description='Auto update the DB.')
    parser.add_argument('-d', '--basedir', dest='basedir', 
                        help='the directory to search for new files',default='.')
    parser.add_argument('-p','--pattern', dest='pattern',help='the pattern to search for', 
                        nargs='+',default=['N_D_W*','O_S_W*'])
    parser.add_argument('-o','--output', dest='outputFile', help='the file to write the stats out',
                        default='stats.md')
    parser.add_argument('-v','--verbose', action='count', help='adjust verbosity level')
    
    args = parser.parse_args()
    
    if args.verbose:
        print '\n'
        parser.print_help()
        print '\n'
    
    try:
        db = ndb(newsstanddb_getdbfile())
    except IOError:
        print 'Couldn\'nt connect to DB'
        
    count = 0
    
    for pat in args.pattern:
        files = glob('/'.join([args.basedir,pat]))
        if args.verbose > 1:
            print files #Debug
        count += len(files)
        try:
            db.multiImport(*files)
        except ProgrammingError as e:
            if args.verbose > 0:
                print "Some files could not be imported: {0}".format(e.message,)
            count -= len(e.message.split(','))
        except:
            raise #TODO: Better exception handling
        
    db.buildStats()
    db.writeStats()
    db.outputStats('/'.join([args.basedir,args.outputFile]))
    
    print "\n== Update Successful (%i files imported) ==\n" % (count,)
    
    db.printStats()

def newsstanddb_getstats():
    try:
        db = ndb(newsstanddb_getdbfile())
    except IOError:
        print 'Couldn\'nt connect to DB'
        
    db.buildStats()
    db.printStats()

def newsstanddb_getdbfile():
    try:
        db = ndb(':memory:')
    except IOError:
        print 'Couldn\'nt connect to DB'
        
    return db.getDBFile()

def newsstanddb_setdbfile():
    parser = argparse.ArgumentParser(description='Set the DB file.')
    parser.add_argument('file', help='the file to set as persistent DB')
    
    print '\n'
    parser.print_help()
    print '\n'
    
    args = parser.parse_args()
    
    try:
        db = ndb(':memory:')
    except IOError:
        print 'Couldn\'nt connect to DB'
        
    db.setDBFile(args.file)
    
def newsstanddb_addproduct():
    parser = argparse.ArgumentParser(description='Add product definition to DB.')
    parser.add_argument('date', help='the cut-off date (when this change took effect)')
    parser.add_argument('product', help='the product identifier')
    parser.add_argument('proceeds', type=float, help='the product\'s developer proceeds')
    
    args = parser.parse_args()
    
    try:
        db = ndb(newsstanddb_getdbfile())
    except IOError:
        print 'Couldn\'nt connect to DB'
        
    db.addProduct(args.date,args.product,args.proceeds)