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
import sys,os,traceback,types


class PlumeModel(object):
    """PlumeModel class is used to generate a reactor network for modeling exhaust plume"""

    def __init__(self, mechs, connects, inflow=lambda t: 10, entrainment=lambda t:0.1,setCanteraPath=None,build=False,bin=False):
        """constructor for plume model.
        Parameters:
        mechs - an array like structure with at least 3 mechanisms, [fuelMech,atmMech,eMech1,eMech2,...,eMechN]
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
        self.mechs = mechs #mechanisms used in gas creation
        self.connects = connects #Adjacency matrix of connections
        self.inflow = inflow #A function that specifies mass flow in
        self.entrainment = entrainment #a function that specifies mass entrainment
        self.build = build #This is a bool that says to build on construction
        self.bin=bin #This is a bool that says to create executable model or not
        self.nex = connects.shape[0]-1 #This is the number of exhaust reactors

        # Add cantera or mechanisms path
        if setCanteraPath is not None:
            ct.add_directory(setCanteraPath)
        else:
            self.mechPath = os.path.dirname(os.path.abspath(__file__))
            self.mechPath = os.path.join(self.mechPath,"mechanisms")
            sys.path.append(self.mechPath)

        #Setting values for parameters constant at the moment but will need updated
        self.eqRatio = 0.8 #equivalence ratio for fuel air mixture
        self.pressCoeff = 0.01 #kg/s/Pa pressure coefficient for pressure controller

        #Creation of gas objects for reactors
        self.createGases()

        #Optionally building network from initialization
        if self.build:
            self.buildNetwork()

        #Optionally create executable model
        if self.bin:
            self.createExecutableModel()

    def __call__(self):
        """Use this function to call the object and iterate the reactor through time."""
        pass

    def buildNetwork(self):
        """Call this function to build the network."""
        self.createReactors()
        self.createMassFlowFunctions()
        self.connectReactors()
        for mfcn in self.massFlowFunctions:
            print(mfcn(0))


        # print(dir(selfreactors[2]))
        # print(self.massFlowFunctions[0])
        # self.massFlowFunctions[0](1)
        # for mfc in self.massFlowFunctions:
        #     mfc(0)
        # print(self.reactors[2].mass)

    def createGases(self):
        """This function creates gases to be used in building the reactor network.
        """
        #Building objects for fuel and air
        self.fuel = ct.Solution(self.mechs[0])
        self.atmosphere = ct.Solution(self.mechs[1])
        self.exhausts = [ct.Solution(mech) for mech in self.mechs[2:]]

    def createReactors(self):
        """Use this function to create exhaust stream network"""
        #Creating fuel reservoir
        self.reactors = ct.Reservoir(contents=self.fuel,name='fuel'),
        #Creating combustor
        self.reactors += ct.ConstPressureReactor(contents=self.fuel,name='combustor',energy='on'),
        #Creating exhaust reactors
        exCycle = it.cycle(self.exhausts)
        self.reactors += tuple([ct.ConstPressureReactor(contents=next(exCycle),name='exhaust{}'.format(i),energy='on') for i in range(self.nex)])
        #Creating atomspheric reactor
        self.reactors += ct.Reservoir(contents=self.atmosphere,name='atmosphere'),

    def createMassFlowFunctions(self):
        """This function uses a closure to generate mass flow controller functions for exhaust plume network"""
        self.massFlowFunctions = []
        name = 'mdot'
        for i in range(self.nex):
            def mdot(t,self=None):
                # mass = self.reactors[i].mass
                return self.x
            mdot.__defaults__ = (mdot,)
            self.massFlowFunctions.append(mdot)

    def connectReactors(self):
        """Use this function to connect exhaust reactors."""
        #Connecting fuel res -> combustor
        self.controllers = ct.MassFlowController(self.reactors[0],self.reactors[1],mdot=self.inflow), #Fuel Air Mixture MFC
        #Connecting combustor -> exhaust
        self.controllers += ct.PressureController(self.reactors[1],self.reactors[2],master=self.controllers[0],K=self.pressCoeff), #Exhaust PFC
        #Creating source/sink attributes with lambdas for reactors
        self.rCons = [lambda:0 for react in self.reactors ]
        for react in self.rCons:
            react.sink = 0
            react.source = 0
        #Connecting exhausts -> adj exhaust
        for f, row in enumerate(self.connects[:-1],2):
            self.rCons[f].source += np.sum(row)
            for t,value in enumerate(row[:-1],start=2):
                if value:
                    self.controllers = ct.MassFlowController(self.reactors[f],self.reactors[t]), #Exhaust MFCS
                    self.rCons[t].sink += 1
        #entrainment controllers
        for t, value in enumerate(self.connects[-1],2):
            if value:
                self.controllers = ct.MassFlowController(self.reactors[-1],self.reactors[t],mdot=self.entrainment), #Exhaust MFCS
                self.rCons[t].sink += 1

    def createExecutableModel(self):
        """Use this function to create an executable binary"""
        pass

    def __str__(self):
        """This overloads the print function."""
        statement = 'PyPlume Network Model:\n'
        T,P,X = self.fuel.TPX

        statement+="\nCombustor: T: {} K, P: {} Pa\n".format(T,P)
        statement+= ", ".join([self.fuel.species_name(i)+":{:0.1f}".format(x) for i,x in enumerate(X)])

        T,P,X = self.atmosphere.TPX
        statement+="\n\nAtmosphere: T: {} K, P: {} Pa\n".format(T,P)
        statement+= ", ".join([self.fuel.species_name(i)+":{:0.1f}".format(x) for i,x in enumerate(X)])

        # for i,exhaust in enumerate(self.exhausts):
        #     statement+="\n\nAtmosphere: T: {} K, P: {} Pa\n".format(T,P)
        #     statement+= ", ".join([self.fuel.species_name(i)+":{:0.1f}".format(x) for i,x in enumerate(X)])

        return statement

    def densePrint(self):
        """This overloads the print function."""
        statement = 'PyPlume Network Model:\n'
        T,P,X = self.fuel.TPX

        statement+="\nCombustor: T: {} K, P: {} Pa\n".format(T,P)
        statement+= ", ".join([self.fuel.species_name(i)+":{:0.1f}".format(x) for i,x in enumerate(X)])

        T,P,X = self.atmosphere.TPX
        statement+="\n\nAtmosphere: T: {} K, P: {} Pa\n".format(T,P)
        statement+= ", ".join([self.fuel.species_name(i)+":{:0.1f}".format(x) for i,x in enumerate(X)])

        for i,exhaust in enumerate(self.exhausts):
            statement+="\n\nAtmosphere: T: {} K, P: {} Pa\n".format(T,P)
            statement+= ", ".join([self.fuel.species_name(i)+":{:0.1f}".format(x) for i,x in enumerate(X)])

        return statement

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
        return cls(mechs,connects,inflow=inflow,entrainment=entrainment,setCanteraPath=setCanteraPath,build=build,bin=bin)

    @classmethod
    def gridModel(cls,n=3,m=3,mechs=["gri30.cti","air.cti","gri30.cti"],inflow=lambda t: 10, entrainment=lambda t:0.1,setCanteraPath=None,build=False,bin=False):
        """ Use this function to generate an instance with grid connects method. It takes all the parameters
            that the class does except connects and replaces connects with n parameter.

        Parameters:
            n - Integer number of reactor rows
            m - Integer number of reactor columns

        Grid model (3x3):
        [fuel res]->[combustor]->[ex0]->[ex1]->[ex4]->[ex7]
                                      ->[ex2]->[ex5]->[ex8]
                                      ->[ex3]->[ex6]->[ex9]

        [farfield]->[ex0,ex1,ex7,ex4,ex3,ex6,ex9]

        Notes:
        The farfield is connected as an inlet for each exterior reactor if you were to draw them as 2D blocks.
        """
        clen = int(n*m+2)
        connects = np.zeros((clen,clen))
        #Fill reactor 0
        for i in range(n):
            connects[0,i+1] = 1
        #Fill remaining
        for i in range(1,clen-n):
            connects[i,i+n] = 1
        #Connect farfield
        connects[-1,0] = 1
        for i in range(1,clen-n,n):
            connects[-1,i]=1
            connects[-1,i+n-1]=1
        return cls(mechs,connects,inflow=inflow,entrainment=entrainment,setCanteraPath=setCanteraPath,build=build,bin=bin)

if __name__ == "__main__":
    pm = PlumeModel.linearExpansionModel()
    pm.buildNetwork()
