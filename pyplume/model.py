# @Author: Anthony Walker
# @Date:   2020-04-09T12:53:51-07:00
# @Email:  walkanth@oregonstate.edu
# @Filename: gs.py
# @Last modified by:   Anthony Walker
# @Last modified time: 2020-04-10T09:53:34-07:00

#imports
import cantera as ct
import itertools as it
import sys,os
class PlumeModel(object):
    """PlumeModel class is used to generate a reactor network for modeling exhaust plume"""

    def __init__(self, ncols,etree,cmech,mechs,setCanteraPath=None):
        """constructor for plume model.
        Parameters:
        ncol - number of columns in the reactor model
        etree - exhaust tree integer is the exponential rate at which columns are divided into reactors
                e.g. ncols=2,etree=3 1 reactor goes to 3 reactors (two columns).
        cmech - mechanism file for the combustor as a path to file (relative or absolute)
        mechs - list or array like container of mechanism files can be one or multiple and
                will be assigned to columns successively.
        setCanteraPath - path variable to cantera mech files
        """
        super(PlumeModel, self).__init__()
        self.ncols = ncols
        self.cmech = cmech
        self.mechs = it.cycle(mechs)
        # Add cantera or mechanisms path
        if setCanteraPath is not None:
            ct.add_directory(setCanteraPath)
        else:
            self.mechPath = os.path.dirname(os.path.abspath(__file__))
            self.mechPath = os.path.join(self.mechPath,"mechanisms")
            sys.path.append(self.mechPath)
        #Create base combustor as constant pressure reactor
        self.createCombustor()

    def __call__(self):
        """Use this function to call the object and iterate the reactor through time."""
        pass

    def createExecutableModel(self):
        """Use this function to create an executable binary"""
        pass

    def createCombustor(self):
        """The combustor uses a single constant pressure reactor to burn the fuel.
        and act as inlet to other reactors.
        """
        gas = ct.Solution(self.cmech)
        inlet = ct.Reservoir(gas)
        self.combustor = ct.ConstPressureReactor(gas)
        self.network = ct.ReactorNet([self.combustor,])
        print(self.network)

if __name__ == "__main__":
    pm = PlumeModel(2,"gri30.cti",["air.cti",])
