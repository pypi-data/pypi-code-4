#!/usr/bin/python
# -*-coding:utf8 -*

import argparse,os.path
# Import the xml module
try:
    from xml.etree import ElementTree as et # Python >= 2.5
except ImportError:
    import elementtree.ElementTree as et # Original python module

#########################################################################
#                               Functions                               #
#########################################################################
def SearchFor(prog,tree):
    flag= False
    for elem in tree.findall(".//prog_list/prog"):
        if elem.text == prog:
            return True
    return False

def DeleteFrom(prog,tree):
    for elem in tree.findall(".//prog_list/prog"):
        if elem.text == prog:
            return elem
    return False

#########################################################################
#                           Manage the Arguments                        #
#########################################################################
def toolsbk():
    parser = argparse.ArgumentParser(description='Tools Backup allows you to save all your usefull programs and to reinstall them easily', epilog='Created by Antoine Durand')
    parser.add_argument('-v','--version', action='version', version='%(prog)s v0.1 License GPLv3', help='version')
    parser.add_argument('-a','--add',action='store_true', help='Add a program to save it')
    parser.add_argument('-d','--delete',action='store', dest='delete', metavar='name', type=str, nargs=1, help='Remove a program from the database')
    parser.add_argument('-s','--search',action='store', dest='search', metavar='name', type=str, nargs=1, help='Search for a program in the database')
    parser.add_argument('-i','--install',action='store_true',help='Install all the programs from the XML file')
    parser.add_argument("filename",help='XML file where all the programs are saved')
    args = parser.parse_args()

    # Test if the file exist
    if not os.path.exists(args.filename) and not args.install:
        # Create the file
        database = et.Element("database")
        ppa_list = et.Element("ppa_list")
        prog_list = et.Element("prog_list")
        database.append(ppa_list)
        database.append(prog_list)
        # Write the XML in the file
        tree = et.ElementTree(database)
        tree.write(args.filename)
    elif not os.path.exists(args.filename) and args.install:
        print "file %s doen't exist" % args.filename
    elif os.path.exists(args.filename) and args.install:
        #Install all the stuff
        # Parse the file and construct an xml object
        tree = et.parse(args.filename)
        for elem in tree.findall('.//ppa_list/ppa'):
            cmd = 'sudo add-apt-repository ppa:' + elem.text
            os.system(cmd)
        # Update the repositories
        os.system('sudo apt-get update')
        for elem in tree.findall('.//prog_list/prog'):
            cmd = 'sudo apt-get install -y' + elem.text
            os.system(cmd)
    else:
        # Parse the file and construct an xml object
        tree = et.parse(args.filename)
        database = tree.getroot() 

    # Add a program
    if args.add:
        print "Enter the name of the program"
        prog = raw_input()
        if not SearchFor(prog,tree):
            newProg = et.SubElement(database[1],"prog")
            newProg.text = prog
            answer = raw_input("Is it present in the officials repositories? [y/N] ")
            if answer != "y":
                print "Enter the repository location"
                ppa = raw_input()
                NewPPA = et.SubElement(database[0],"ppa")
                NewPPA.text = ppa 
            # Update the file
            f = file(args.filename,"w")
            f.write(et.tostring(database))
            print "The program has been successfully added to the database"
        else:
            print "This program is already in the database"
    # Search for a program
    elif args.search != None:
        if SearchFor(args.search[0],tree):
            print "the program '%s' is already in the database" % args.search[0]
        else:
            print "the program '%s' is not in the database" %args.search[0]
    # Delete a program from the database
    elif args.delete != None:
        todelete = DeleteFrom(args.delete[0],tree)
        if todelete != False:
            try:
                database[1].remove(todelete)
                # Update the file
                f = file(args.filename,"w")
                f.write(et.tostring(database))
                print "the program has been successfully deleted from the database"
            except IOError:
                print "Error while deleting the program '%s'" % args.delete[0]
        else:
            print "This program is not in the database"

if __name__ == "__main__":
    toolsbk()
