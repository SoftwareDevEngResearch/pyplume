
import sys,os,pytest,filecmp,shutil
main_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(main_dir,'..'))
import pyplume

def getMechPath(fname=None):
    """This function gets the mechanism path."""
    newfile = os.path.join(main_dir,'..')
    pathList=['pyplume','mechanisms']
    if fname is not None:
        pathList.append(fname)
    for item in pathList:
        newfile = os.path.join(newfile,item)
    return newfile

def test_addMechFile_exit(fname="gri30"):
    """Test that the function exits properly with bad input"""
    with pytest.raises(SystemExit) as output:
        pyplume.mech.addMechFile(fname)
        assert output.type == SystemExit
        assert output.value.code == 42

def test_addMechFile(fname=os.path.join(main_dir,"gri30.cti")):
    """This function tests adding the mechanism files."""
    #Run file copy
    pyplume.mech.addMechFile(fname)
    #Create new file path
    newfile = getMechPath(fname=os.path.basename(fname))
    #Compare files
    assert filecmp.cmp(fname,newfile,shallow=False)


def test_mechFileRestore():
    """Use this function to test that the files are restored properly."""
    #Get paths
    mPath = getMechPath()
    omPath = os.path.join(os.path.join(mPath,'..'),"originals")
    #Remove folder of mechanisms
    shutil.rmtree(mPath)
    #Run restore
    pyplume.mech.mechFileRestore()
    #Compare contents
    for f in os.listdir(omPath):
        ofile = os.path.join(omPath,f)
        nfile = os.path.join(mPath,f)
        assert filecmp.cmp(ofile,nfile,shallow=False)
