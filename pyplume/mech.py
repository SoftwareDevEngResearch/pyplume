import argparse, os, shutil, traceback, sys

def addMechFile(fname):
    """
    This function takes a given mechanism file and stores it for use with the
    plume model generator.

    This will automatically replace mechanism files in the program folder. They can be restored however with
    mechFileRestore()
    """
    #get directory path of mechanisms
    direc = os.path.join(os.path.dirname(os.path.abspath(__file__)),'mechanisms')
    #check if file exists - throw error if not
    print("Checking {} exists and is a file...".format(os.path.basename(fname)))
    try:
        if not os.path.exists(fname) or not os.path.isfile(fname):
            raise TypeError("{}: does not exist or is not a file.".format(fname))
    except TypeError as e:
        tb = traceback.format_exc()
        print(tb)
        sys.exit()
    #Copy file to new directory
    print("Adding {} to mechanisms...".format(os.path.basename(fname)))
    shutil.copyfile(fname,os.path.join(direc,os.path.basename(fname)))
    print("done.")

def mechFileRestore():
    """Use this function to restore the original mechanism files supplied."""
    #get directory path of package
    print("Restoring original mechanism files.\n")
    direc = os.path.dirname(os.path.abspath(__file__))
    opath = os.path.join(direc,"originals")
    npath = os.path.join(direc,"mechanisms")
    if not os.path.exists(npath):
        os.mkdir(npath)
    for f in os.listdir(opath):
        print("\tRestoring: {}...".format(f))
        shutil.copyfile(os.path.join(opath,f),os.path.join(npath,f))
    print("done.")

def mechCLI():
    parser = argparse.ArgumentParser(description="""This is the commandline interface for
    managing mechanism files of PyPlume.
    """)
    parser.add_argument("-r","--restore",action='store_true',help="""set this argument to true to restore mechanism files.""")
    parser.add_argument('-a','--add',default=None,type=str,help="""this can be used to add a mechanism file to the codes internal data.""")
    args = parser.parse_args()

    if args.restore:
        mechFileRestore()

    if args.add is not None:
        addMechFile(args.add)

if __name__ == "__main__":
    mechCLI()
