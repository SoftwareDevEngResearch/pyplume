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
import sys,os,traceback


class PlumeModel(object):
    """PlumeModel class is used to generate a reactor network for modeling exhaust plume"""

    def __init__(self, mechs, connects, inflow=lambda t: 10, entrainment=lambda t:0.1,setCanteraPath=None,build=False,bin=False):
        """constructor for plume model.
        Parameters:
        mechs - an array like structure with at least 3 mechanisms, [fuelMech,airMech,eMech1,eMech2,...,eMechN]
        inflow - a function that specifies the inlet mass flow as a function of time.
        entrainment - a function that specifies entrainment mass as a function of time.
        connects - an 2d adjacency matrix with integer values corresponding to the appropriate mass flow function+1 in the list of mass flow functions.
                    So, the first mass flow function, 0 index, will be represented as 1 in the matrix. This is because these values will be used for conditionals
                    as well. A template matrix can be generated. The matrix should specifically
        setCanteraPath - path variable to cantera mech files
        build -  boolean that builds network strictly from configuration in mechanism files (T,P) if true.
            default: build=false
        bin - boolean that builds executable model
        """
        super(PlumeModel, self).__init__()
        #Saving contents into self of inputs
        self.mechs = mechs
        self.connects = connects
        self.inflow = inflow
        self.entrainment = entrainment
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
        self.controllers = ct.MassFlowController(self.reactors[0],self.reactors[1],mdot=self.inflow), #Fuel Air Mixture MFC
        self.controllers += ct.PressureController(self.reactors[1],self.reactors[2],master=self.controllers[0],K=self.pressCoeff), #Exhaust PFC

    def createExhaustReactors(self):
        """Use this function to create exhaust stream network"""
        emechCycle = it.cycle(mechs[2:])
        self.exs = [ct.ConstPressureReactor(ct.Solution(next(emechCycle))) for i in range(self.nex)]

    def connectExhausts(self):
        """Use this function to connect exhaust reactors."""
        #go through adj matrix here and connect with massFlowControllers.
        #will need to figure out communication strategy for continuity in
        #exhaust reactors but linearExpansionModel is made

    def setMassFlow(self,mdot):
        """Use this function to set mass flow function or value."""
        self.mdot = mdot

    #Class methods that implement certain kinds of reactor ideas.
    @classmethod
    def linearExpansionModel(cls,n=10,mechs=["gri30.cti","air.cti","gri30.cti"],inflow=lambda t: 10, entrainment=lambda t:0.1,setCanteraPath=None,build=False,bin=False):
        """ Use this function to generate an instance with linear expansion connects method. It takes all the parameters
            that the class does except connects and replaces connects with n parameter.

        Parameters:
            n - number of reactors using linear expansion. e.g. at level 1 there is one reactor
                at level two there are two and so on. n must result in an integer number of steps
                based on the formula:steps=(-1+np.sqrt(1+8*n))/2

        Linear expansion model:
        [fuel res]->[combustor]->[ex1]->[ex2]->[ex4]
                                      ->[ex3]->[ex5]
                                             ->[ex6]
        [farfield]->[ex1,ex2,ex3,ex4,ex6]

        Notes:
        The farfield is connected as an inlet for each exterior reactor if you were to draw them as 2D blocks.
        """
        connects = np.zeros((n+1,n+1))
        getsteps = lambda k: (-1+np.sqrt(1+8*k))/2
        x = 1
        j = 1
        i = 0
        steps = getsteps(n)
        #Check if is integer
        try:
            if steps.is_integer():
                steps = int(steps)
            else:
                raise TypeError("{}: is not an Integer as required by: steps=(-1+np.sqrt(1+8*n))/2".format(steps))
        except TypeError as e:
            tb = traceback.format_exc()
            print(tb)
            sys.exit()
            pass
        #Fill exhaust dependency
        for cn in range(2,2+steps-1):
            connects[i:i+x,j:j+x+1] = 1
            i+=x
            x = x+1
            j+=x
        #Connecting farfield
        idx = it.cycle(np.arange(0,n,1))
        for i in range(steps):
            if i+1 >= 3:
                connects[-1,next(idx)]=1
                for j in range(1,i):
                    connects[-1,next(idx)]=0
                connects[-1,next(idx)]=1
            else:
                for j in range(i+1):
                    connects[-1,next(idx)]=1
        return cls(mechs,connects)

    @classmethod
    def gridModel(cls,n=5,m=5,mechs=["gri30.cti","air.cti","gri30.cti"],inflow=lambda t: 10, entrainment=lambda t:0.1,setCanteraPath=None,build=False,bin=False):
        """ Use this function to generate an instance with grid connects method. It takes all the parameters
            that the class does except connects and replaces connects with n parameter.

        Parameters:
            n - Integer number of reactor rows
            m - Integer number of reactor columns

        Grid model (3x3):
        [fuel res]->[combustor]->[ex1]->[ex4]->[ex7]
                               ->[ex2]->[ex5]->[ex8]
                               ->[ex3]->[ex6]->[ex9]

        [farfield]->[ex1,ex7,ex4,ex3,ex6,ex9]

        Notes:
        The farfield is connected as an inlet for each exterior reactor if you were to draw them as 2D blocks.
        """
        clen = int(n*m+1)
        connects = np.zeros((clen,clen))


if __name__ == "__main__":
    pm = PlumeModel.linearExpansionModel()
    print(pm.connects)
