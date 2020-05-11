# @Author: Anthony Walker
# @Date:   2020-04-09T12:53:51-07:00
# @Email:  walkanth@oregonstate.edu
# @Filename: gs.py
# @Last modified by:   Anthony Walker
# @Last modified time: 2020-04-10T09:53:34-07:00

#imports
import cantera as ct
import itertools as it
import numpy as np
import sys,os

class PlumeModel(object):
    """PlumeModel class is used to generate a reactor network for modeling exhaust plume"""

    def __init__(self,mechs,connections,massFlows,setCanteraPath=None,build=False,bin=False):
        """constructor for plume model.
        Parameters:
        ncols - number of columns in the exhaust reactor network.
        cmech - mechanism file for the combustor as a path to file (relative or absolute)
        emech - mechanism file for the exhaust stream.
        efun - a single parameter function e.g. f(n) that returns the number of reactors in a column
            default: efun=lambda x:x (linear)
        setCanteraPath - path variable to cantera mech files
        build -  boolean that builds network strictly from configuration in mechanism files (T,P) if true.
            default: build=false
        bin - boolean that builds
        """
        super(PlumeModel, self).__init__()
        self.ncols = ncols
        self.cmech = cmech
        self.emech = emech
        self.build = build
        self.efun = efun
        self.fuel = ct.Solution(self.cmech)
        self.air = ct.Solution(self.emech)
        # Add cantera or mechanisms path
        if setCanteraPath is not None:
            ct.add_directory(setCanteraPath)
        else:
            self.mechPath = os.path.dirname(os.path.abspath(__file__))
            self.mechPath = os.path.join(self.mechPath,"mechanisms")
            sys.path.append(self.mechPath)

        #Setting values for parameters constant at the moment but will need updated
        self.mdot = 1 #m/s mass flow rate of fuel air mixture
        self.eqRatio = 0.8 #equivalence ratio for fuel air mixture
        self.pressCoeff = 0.01 #kg/s/Pa pressure coefficient for pressure controller

        #Optionally building network from initialization
        if self.build:
            self.buildNetwork()

    def __call__(self):
        """Use this function to call the object and iterate the reactor through time."""
        pass

    def buildNetwork(self):
        """Call this function to build the network."""
        self.createNonExhaustReactors()
        self.createExhaustReactors()
        self.connectExhausts()

    def createExecutableModel(self):
        """Use this function to create an executable binary"""
        pass

    def createNonExhaustReactors(self):
        """Create the reservoir which holds the fuel as a gas which will be fed into the combustor.
        reactors[0] - fuel reservoir
        reactors[1] - combustor
        reactors[2] - exhaust
        reactors[3] - atomsphere (farfield)
        """
        #Creating main reactor network reactors
        self.reactors = ct.Reservoir(self.fuel,name='fuel'),
        self.reactors += ct.ConstPressureReactor(self.fuel,name='combustor'),ct.ConstPressureReactor(self.air,name='exhaust')
        self.reactors += ct.Reservoir(self.air,name='atmosphere'),
        #Creating main controls
        self.controllers = ct.MassFlowController(self.reactors[0],self.reactors[1],mdot=self.mdot), #Fuel Air Mixture MFC
        self.controllers += ct.PressureController(self.reactors[1],self.reactors[2],master=self.controllers[0],K=self.pressCoeff), #Exhaust PFC

    def createExhaustReactors(self):
        """Use this function to create exhaust stream network"""
        columns = np.arange(1,self.ncols+1,1)
        rows = self.efun(columns)
        self.exs = [] #List of lists of exhaust reactors
        for i,number in enumerate(rows):
            self.exs.append([])
            for j in range(number):
                self.exs[i].append(ct.ConstPressureReactor(self.air))

    def connectExhausts(self):
        """Use this function to connect exhaust reactors."""
        #Connect main exhaust to first reactor/reactors
        for ereact in self.exs[0]:
            self.controllers+=ct.PressureController(self.reactors[2],ereact,master=None,K=self.pressCoeff)

        for i in range(len(self.exs)):
            clen = len(self.exs[i])
            if clen-1:
                print("if {} {}".format(i,clen))
            else:
                self.controllers+=ct.PressureController(self.exs)

    def setMassFlow(self,mdot):
        """Use this function to set mass flow function or value."""
        self.mdot = mdot

if __name__ == "__main__":
    # pm = PlumeModel(3,"gri30.cti","air.cti",build=True)
    for i in range(9):
        if i:
            print(i)
