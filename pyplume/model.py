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

    def __init__(self,mechs,mflows,connects,setCanteraPath=None,build=False,bin=False):
        """constructor for plume model.
        Parameters:
        mechs - an array like structure with at least 3 mechanisms, [fuelMech,airMech,eMech1,eMech2,...,eMechN]
        mflows - an array like structure of mass flow functions (or constants) that dictate the mass flow between reactors.
        connects - an 2d adjacency matrix with integer values corresponding to the appropriate mass flow function+1 in the list of mass flow functions.
                    So, the first mass flow function, 0 index, will be represented as 1 in the matrix. This is because these values will be used for conditionals
                    as well. A template matrix can be generated. The matrix should specifically
        setCanteraPath - path variable to cantera mech files
        build -  boolean that builds network strictly from configuration in mechanism files (T,P) if true.
            default: build=false
        bin - boolean that builds

        Notes:
        The mass flow functions
        """
        super(PlumeModel, self).__init__()
        #Saving contents into self of inputs
        self.mechs = mechs
        self.connects = connects
        self.mflows = mflows
        self.build = build
        self.nex = connects.shape[0]-3
        #Building objects for fuel and air
        self.fuel = ct.Solution(self.mechs[0])
        self.air = ct.Solution(self.mechs[1])
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

        # #Optionally building network from initialization
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
        emechCycle = it.cycle(mechs[2:])
        self.exs = [ct.ConstPressureReactor(ct.Solution(next(emechCycle))) for i in range(self.nex)]

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

#End of class methods
def connectionTemplate(n=0):
    """
    Use this function to create a template for the connection matrix.
    Parameters:
    n - number of exhaust reactors in the model
    Returns
    matrix: template connections matrix

    Notes:
    If no n value is entered this is the minimal case (n=0).
    [0, 1, 0 ,0]
    [0, 0, 2, 0]
    [0, 0, 0, 0]
    [0, 0, 3, 0]
    which means fuel res -> combustor -> exhaust <- farfield (for entrainment)
    this implies 3 mass flow functions, 1 for fuel->combustor, 2 for combustor->exhaust, and 3 for farfield->exhaust.
    """
    n+=4
    matrix = np.zeros((n,n)) #n+2 to include fuel reservoir, combustor,exhaust, and farfield
    matrix[0,1] = 1 #connect fuel res to combustor
    matrix[1,2] = 2
    matrix[-1,2] = 3
    return matrix

def linearExpansionConnects(n=6,fcn=lambda L:4):
    """ Use this function to generate a test connects matrix.
    Parameters:
        n - number of reactors using linear expansion. e.g. at level 1 there is one reactor
            at level two there are two and so on.
        fcn -  a function that takes L (the level) and returns a number which is assigned as the mass flow index
                default: lambda L:4 which implies a fourth mass flow function.

    [fuel res]->[combustor]->[ex1]->[ex2]->[ex4]
                                  ->[ex3]->[ex5]
                                         ->[ex6]
    [farfield]->[ex1,ex2,ex3,ex4,ex6]
    Notes:
        Far field is connected to all exhausts with mass flow function 3
    """
    getsteps = lambda k: int((-1+np.sqrt(1+8*k))/2)
    connects = connectionTemplate(n-1) #Add five extra reactors
    x = 1
    j = 3
    i = 2
    steps = getsteps(n-1)
    #Fill exhaust dependency
    for cn in range(2,2+steps):
        connects[i:i+x,j:j+x+1] = fcn(cn)
        i+=x
        x = x+1
        j+=x
    connects[-1,2:] = 3
    return connects

if __name__ == "__main__":
    connects = linearExpansionConnects()
    mflows = [10,10,0.1,]
    mechs = ["gri30.cti","air.cti","gri30.cti"]
    pm = PlumeModel(mechs,mflows,connects,build=True)
