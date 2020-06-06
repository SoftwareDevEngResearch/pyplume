
import sys,os,pytest,filecmp,shutil,pytest
main_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(main_dir,'..'))
import mech

def getMechPath(fname=None):
    """This function gets the mechanism path. NOT A TEST"""
    newfile = os.path.join(main_dir,'..')
    pathList=['mechanisms',]
    if fname is not None:
        pathList.append(fname)
    for item in pathList:
        newfile = os.path.join(newfile,item)
    return newfile

def test_mechFileAdd_exit(fname="gri30"):
    """Test that the function exits properly with bad input"""
    with pytest.raises(SystemExit) as output:
        mech.mechFileAdd(fname)
        assert output.type == SystemExit
        assert output.value.code == 42

def test_mechFileAdd(fname=os.path.join(main_dir,"gri30.cti")):
    """This function tests adding the mechanism files."""
    #Run file copy
    mech.mechFileAdd(fname)
    #Create new file path
    newfile = getMechPath(fname=os.path.basename(fname))
    #Compare files
    assert filecmp.cmp(fname,newfile,shallow=False)

def test_mechFileDelete(fname="Ajgkdlsageiwon.cti"):
    """This function tests adding the mechanism files."""
    #Get directory name
    fname = getMechPath(fname=os.path.basename(fname))
    #Create file
    f = open(fname,'w')
    f.close()
    #delete file
    mech.mechFileDelete(fname)
    #List files in directory
    dirFiles = os.listdir()
    #Compare files
    assert os.path.basename(fname) not in dirFiles

def test_mechFileRestore():
    """Use this function to test that the files are restored properly."""
    #Get paths
    mPath = getMechPath()
    omPath = os.path.join(os.path.join(mPath,'..'),"originals")
    #Remove folder of mechanisms
    shutil.rmtree(mPath)
    #Run restore
    mech.mechFileRestore()
    #Compare contents
    for f in os.listdir(omPath):
        ofile = os.path.join(omPath,f)
        nfile = os.path.join(mPath,f)
        assert filecmp.cmp(ofile,nfile,shallow=False)

def runTests():
    """Use this function to run pytests."""
    pytest.main([__file__,"--verbose"])
