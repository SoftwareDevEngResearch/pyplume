import argparse, os, shutil, traceback, sys
import pyplume.tests.testMechs

def mechFileAdd(fname):
    """
    This function takes a given mechanism file and stores it for use with the
    plume model generator.

    This will automatically replace mechanism files in the program folder. They can be restored however with
    mechFileRestore()
    """
    #get directory path of mechanisms
    direc = os.path.join(os.path.dirname(os.path.abspath(__file__)),'mechanisms')
    #check if file exists - throw error if not
    print("\nChecking {} exists and is a file...\n".format(os.path.basename(fname)))
    try:
        if not os.path.exists(fname) or not os.path.isfile(fname):
            raise TypeError("{}: does not exist or is not a file.".format(fname))
    except TypeError as e:
        tb = traceback.format_exc()
        print(tb)
        sys.exit()
    #Copy file to new directory
    print("Adding {} to mechanisms...\n".format(os.path.basename(fname)))
    shutil.copyfile(fname,os.path.join(direc,os.path.basename(fname)))
    print("done.\n")

def mechFileRestore():
    """Use this function to restore the original mechanism files supplied."""
    #get directory path of package
    print("\nRestoring original mechanism files...\n")
    direc = os.path.dirname(os.path.abspath(__file__))
    opath = os.path.join(direc,"originals")
    npath = os.path.join(direc,"mechanisms")
    if not os.path.exists(npath):
        os.mkdir(npath)
    for f in os.listdir(opath):
        print("\tRestoring: {}...".format(f))
        shutil.copyfile(os.path.join(opath,f),os.path.join(npath,f))
    print("done.\n")

def mechFileDelete(fname):
    """Use this function to delete a mechanism file supplied."""
    #get directory path of package
    print("\nRemoving {} mechanism file...\n".format(fname))
    direc = os.path.dirname(os.path.abspath(__file__))
    npath = os.path.join(direc,"mechanisms")
    os.remove(os.path.join(npath,fname))
    print('done.\n')

def mechFileList():
    """Use this function to list mechanism files supplied."""
    #get directory path of package
    print("\nListing mechanism files.\n")
    direc = os.path.dirname(os.path.abspath(__file__))
    npath = os.path.join(direc,"mechanisms")
    for file in os.listdir(npath):
        print("\t"+file)
    print("done.\n")

def mechCLI():
    """This function is used for the command line interface option of mech"""
    parser = argparse.ArgumentParser(description="""This is the commandline interface for
    managing mechanism files of PyPlume.
    """)
    parser.add_argument("-r","--restore",action='store_true',help="""set this flag to restore mechanism files.""")
    parser.add_argument("-l","--list",action='store_true',help="""set this flag to list mechanism files.""")
    parser.add_argument('-a','--add',default=None,type=str,help="""this can be used to add a mechanism file to the codes internal data.""")
    parser.add_argument('-d','--delete',default=None,type=str,help="""this can be used to delete a mechanism file to the codes internal data.""")
    parser.add_argument("-t","--test",action='store_true',help="""set this flag to run test functions.""")
    args = parser.parse_args()

    if args.restore:
        mechFileRestore()

    if args.add is not None:
        mechFileAdd(args.add)

    if args.delete is not None:
        mechFileDelete(args.delete)

    if args.list:
        mechFileList()

    if args.test:
        pyplume.tests.testMechs.runTests()

if __name__ == "__main__":
    mechCLI()
