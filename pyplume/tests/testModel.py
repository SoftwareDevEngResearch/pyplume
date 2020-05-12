import sys,os,pytest,filecmp,shutil,pytest
main_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(main_dir,'..'))
import model
import itertools

def test_linearExpansionConnects():
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
