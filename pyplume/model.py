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
import sys,os,traceback,output,argparse
import pyplume.tests.testModel

class PlumeModel(object):
    """PlumeModel class is used to generate a reactor network for modeling exhaust plume"""

    def __init__(self, mechs, connects, residenceTime=lambda t: 0.1, entrainment=lambda t:0.1,fpath=None,setCanteraPath=None,build=False):
        """constructor for plume model.
        Parameters:
        mechs - an array like structure with at least 3 mechanisms, [fuelMech,atmMech,eMech1,eMech2,...,eMechN]
        residenceTime - a function that specifies the residence time as a function of time---this is used to determine combustor and system mass flow rates.
        entrainment - a function that specifies entrainment mass as a function of time.
        connects - an 2d adjacency matrix with integer values corresponding to the appropriate mass flow function+1 in the list of mass flow functions.
                    So, the first mass flow function, 0 index, will be represented as 1 in the matrix. This is because these values will be used for conditionals
                    as well. A template matrix can be generated. The matrix should specifically
        setCanteraPath - path variable to cantera mech files
        build -  boolean that builds network strictly from configuration in mechanism files (T,P) if true.
            default: build=false
        """
        super(PlumeModel, self).__init__()
        #Saving contents into self of inputs
        self.mechs = mechs #mechanisms used in gas creation
        self.connects = connects #Adjacency matrix of connections
        self.residenceTime = residenceTime #RTF a function that controlls mass flow
        self.entrainment = entrainment #a function that specifies mass entrainment
        self.build = build #This is a bool that says to build on construction
        self.nex = connects.shape[0]-1 #This is the number of exhaust reactors
        self.fpath=fpath
        self.ptype=True #True for sparse printing
        # Add cantera or mechanisms path
        if setCanteraPath is not None:
            ct.add_directory(setCanteraPath)
        else:
            self.mechPath = os.path.dirname(os.path.abspath(__file__))
            self.mechPath = os.path.join(self.mechPath,"mechanisms")
            sys.path.append(self.mechPath)
        #Creation of gas objects for reactors
        self.createGases()
        #Optionally building network from initialization
        if self.build:
            self.buildNetwork()

    def __call__(self,time,fname=None):
        """Use this function to call the object and iterate the reactor through time."""
        self.network.advance(time)
        self.state = self.network.get_state()
        self.writer(self.state) #Write if file path is provided
        return self.state

    def __str__(self):
        """This overloads the print function."""
        if self.ptype:
            return output.sparsePrint(self)
        else:
            return output.densePrint(self)

    def steadyState(self):
        self.network.advance_to_steady_state()
        self.state = self.network.get_state()
        self.writer(self.state) #Write if file path is provided
        return self.state

    def buildNetwork(self):
        """Call this function to build the network."""
        self.createReactors() #This function creates reactors
        self.connectReactors()  #This function connects reactors with Adj matrxi
        self.network = ct.ReactorNet(self.reactors) #Create reactor network
        self.network.set_initial_time(0) #Set initial reactor time to zero
        self.network.reinitialize() #Initialize reactor network
        self.initialState = self.network.get_state()
        self.keys = [self.network.component_name(i) for i in range(len(self.initialState))]
        #Added h5writer if a file path is specified
        self.writer = (lambda x:0) if self.fpath is None else output.h5Writer(self.fpath,self.keys,self.initialState)

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
        self.fuel.equilibrate('HP')
        self.fuelReservoir = ct.Reservoir(contents=self.fuel,name='fuel')
        #Creating combustor
        self.reactors = ct.ConstPressureReactor(contents=self.fuel,name='combustor',energy='on'),
        #Creating exhaust reactors
        exCycle = it.cycle(self.exhausts)
        self.reactors += tuple([ct.ConstPressureReactor(contents=next(exCycle),name='exhaust{}'.format(i),energy='on') for i in range(self.nex)])
        #Creating atomspheric reactor
        self.atmosReservoir = ct.Reservoir(contents=self.atmosphere,name='atmosphere')
        self.exhaustReservoir = ct.Reservoir(contents=self.atmosphere,name='exhaust')

    def connectReactors(self):
        """Use this function to connect exhaust reactors."""
        #Connecting fuel res -> combustor
        def inflow(t): # inflow is a variable mass flow rate base on residence time
            return self.reactors[0].mass / self.residenceTime(t)
        self.inflow = inflow
        self.controllers = ct.MassFlowController(self.fuelReservoir,self.reactors[0],mdot=self.inflow), #Fuel Air Mixture MFC
        #Connecting combustor -> exhaust
        self.controllers += ct.MassFlowController(self.reactors[0],self.reactors[1],mdot=self.inflow), #Exhaust MFC
        #Connecting exhausts -> adj exhaust
        exStart = 1 #starting index of exhaust reactors
        for f, row in enumerate(self.connects[:-1],exStart):
            sink = np.sum(row) #number of places the mass flow goes from one reactor to another
            if sink != 0: #Connects non-terminal exhaust reactors
                for t,value in enumerate(row[:-1],start=exStart):
                    if value:
                        #Using a closure to create mass flow function
                        def mdot(t,fcn=None):
                            return (self.reactors[fcn.ridx].mass / self.residenceTime(t)) / fcn.sink
                        mdot.__defaults__ = (mdot,)
                        mdot.sink = sink #number of places the mass flow goes from one reactor to another
                        mdot.ridx = np.copy(f)
                        #Create controller
                        self.controllers += ct.MassFlowController(self.reactors[f],self.reactors[t],mdot=mdot), #Exhaust MFCS
            else: #This else statement connects all terminal exhaust reactors to exhaust reservoir
                #Using a closure to create mass flow function
                def mdot(t,fcn=None):
                    return (self.reactors[fcn.ridx].mass / self.residenceTime(t))
                mdot.__defaults__ = (mdot,)
                mdot.sink = sink #number of places the mass flow goes from one reactor to another
                mdot.ridx = np.copy(f)
                #Create controller
                self.controllers += ct.MassFlowController(self.reactors[f],self.exhaustReservoir,mdot=mdot), #Exhaust MFCS

        #entrainment controllers
        for t, value in enumerate(self.connects[-1],exStart):
            if value:
                self.controllers += ct.MassFlowController(self.atmosReservoir,self.reactors[t],mdot=self.entrainment), #Exhaust MFCS

    #Class methods that implement certain kinds of reactor ideas.
    @classmethod
    def simpleModel(cls,mechs=["gri30.cti","air.cti","gri30.cti"],residenceTime=lambda t: 0.1, entrainment=lambda t:0.1,fpath="simple.hdf5",setCanteraPath=None,build=False):
        """This classmethod build a 1 reactor exhaust model. It has extra parameters than the class
        Linear expansion model:
        [fuel res]->[combustor]->[ex1]->[exRes]
        [farfield]->[ex1]
        """
        n = 1
        connects = np.zeros((n+1,n+1))
        connects[1,0] = 1
        return cls(mechs,connects,residenceTime=residenceTime,entrainment=entrainment,fpath=fpath,setCanteraPath=setCanteraPath,build=build)

    @classmethod
    def linearExpansionModel(cls,n=10,mechs=["gri30.cti","air.cti","gri30.cti"],residenceTime=lambda t: 0.1, entrainment=lambda t:0.1,fpath="linear.hdf5",setCanteraPath=None,build=False):
        """ Use this function to generate an instance with linear expansion connects method. It takes all the parameters
            that the class does except connects and replaces connects with n parameter.

        Parameters:
            n - number of reactors using linear expansion. e.g. at level 1 there is one reactor
                at level two there are two and so on. n must result in an integer number of steps
                based on the formula:steps=(-1+np.sqrt(1+8*n))/2

        Linear expansion model:
        [fuel res]->[combustor]->[ex1]->[ex2]->[ex4]->[exRes]
                                      ->[ex3]->[ex5]->[exRes]
                                             ->[ex6]->[exRes]
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
        return cls(mechs,connects,residenceTime=residenceTime,entrainment=entrainment,fpath=fpath,setCanteraPath=setCanteraPath,build=build)

    @classmethod
    def gridModel(cls,n=3,m=3,mechs=["gri30.cti","air.cti","gri30.cti"],residenceTime=lambda t: 0.1, entrainment=lambda t:0.1,fpath="grid.hdf5",setCanteraPath=None,build=False):
        """ Use this function to generate an instance with grid connects method. It takes all the parameters
            that the class does except connects and replaces connects with n parameter.

        Parameters:
            n - Integer number of reactor rows
            m - Integer number of reactor columns

        Grid model (3x3):
        [fuel res]->[combustor]->[ex0]->[ex1]->[ex4]->[ex7]->[exRes]
                                      ->[ex2]->[ex5]->[ex8]->[exRes]
                                      ->[ex3]->[ex6]->[ex9]->[exRes]

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
        for i in range(1,clen-n-1):
            connects[i,i+n] = 1
        #Connect farfield
        connects[-1,0] = 1
        for i in range(1,clen-n,n):
            connects[-1,i]=1
            connects[-1,i+n-1]=1
        return cls(mechs,connects,residenceTime=residenceTime,entrainment=entrainment,fpath=fpath,setCanteraPath=setCanteraPath,build=build)

def modelCLI():
    """This function is used for the command line interface option of mech"""
    parser = argparse.ArgumentParser(description="""This is the commandline interface for
    running an exhuast network.
    """)

    fmap = {'simple' : PlumeModel.simpleModel,
                    'grid' : PlumeModel.gridModel,
                    "linear":PlumeModel.linearExpansionModel}
    parser.add_argument('network', choices=fmap.keys(),help="This is a required arguement that specifies the model which will be used. Currently implemented choices are simple, grid, and linear.")
    parser.add_argument("-ss","--steady",action='store_true',help="""set this flag run to steady state after integration""")
    parser.add_argument("-t0",nargs="?",default=0,type=float,help="Initial integration time")
    parser.add_argument("-tf",nargs="?",default=1,type=float,help="Final integration time")
    parser.add_argument("-dt",nargs="?",default=0.1,type=float,help="Integration time interval")
    parser.add_argument("-t","--test",action='store_true',help="""set this flag to run test functions.""")
    parser.add_argument("-v","--verbose",action='store_true',help="""set this flag to run print statements during the process.""")

    args = parser.parse_args()
    if args.verbose:
        print("Creating {} model and building network.".format(args.network))
    pm = fmap[args.network]()
    pm.buildNetwork()

    for t in np.arange(args.t0,args.tf+args.dt,args.dt):
        if args.verbose:
            print("Advancing to time: {:0.3f}.".format(t))
        pm(t)

    if args.steady:
        if args.verbose:
            print("Advancing to steady state.")
        pm.steadyState()

    if args.test:
        if args.verbose:
            print("Running model test suite.")
        pyplume.tests.testModel.runTests()

if __name__ == "__main__":
    # modelCLI()
    pm = PlumeModel.simpleModel()
    pm.buildNetwork()
    for t in np.arange(0,1,0.1):
        pm(t)
    
