import sys,os,pytest,filecmp,shutil,pytest
main_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(main_dir,'..'))
import model
import itertools
import numpy as np

def test_linearExpansionModel():
    """This function tests that linearExpansion connects is working properly."""
    #This portions test to make sure the code fails with n values that cause non-integer steps
    with pytest.raises(SystemExit) as output:
        model.PlumeModel.linearExpansionModel(14)
        assert output.type == SystemExit
        assert output.value.code == 42

    #Manually check that it produces correct adj matrix otherwise
    n=10
    connects = model.PlumeModel.linearExpansionModel(n).connects
    ones = [(0,1),(0,2),(1,3),(1,4),(1,5),(2,3),(2,4),(2,5)]
    ones += [(3,6),(3,7),(3,8),(3,9),(4,6),(4,7),(4,8),(4,9),(5,6),(5,7),(5,8),(5,9)]
    ones += [(n,0),(n,1),(n,2),(n,3),(n,5),(n,6),(n,9)]
    trange = range(connects.shape[0])
    for i in trange:
        for j in trange:
            if (i,j) in ones:
                assert connects[i,j] == 1
            else:
                assert connects[i,j] == 0


def test_gridModel():
    """Use this function to test grid model connects matrix."""
    #Manually check that it produces correct adj matrix otherwise
    n = m = 3
    connects = model.PlumeModel.gridModel(n=n,m=m).connects
    ones = np.zeros(connects.shape)
    diag=4
    ones[0,1:diag] = 1
    diagStart = diag
    for i in range(1,int(n*m-2)):
        ones[i,diagStart] = 1
        diagStart+=1
    for ext in [0,1,3,4,6,7,9]:
        ones[-1,ext] = 1
    trange = range(connects.shape[0])
    for i in trange:
        for j in trange:
            assert connects[i,j] == ones[i,j]

def test_simpleModel():
    """Use this function to test grid model connects matrix."""
    #Manually check that it produces correct adj matrix otherwise
    n = m = 3
    connects = model.PlumeModel.simpleModel().connects
    ones = np.zeros(connects.shape)
    for i,row in enumerate(connects):
        for j,val in enumerate(row):
            if i == 1 and j == 0:
                assert connects[i,j] == 1
            else:
                assert connects[i,j] == 0

def test_connectReactors():
    """Use this function to test the mass flow connections"""

def test_createReactors():
    """Use this function to test creation of reactors."""

def runTests():
    """Use this function to run pytests."""
    pytest.main([__file__,"--verbose"])
