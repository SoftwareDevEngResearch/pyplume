# PyPlume
This package is intended to build reactor network models for exhaust plumes based on user input and incorporate some methods for analysis of the results.

### Installation
This package can be installed via conda and pip. (UPDATEME)

```bash
  conda install -c anthony-walker pyplume
```

```bash
  pip install pyplume
```

### Mechanism management
The model generation two requires chemical mechanisms to run. Some of these mechanisms can be found within Cantera and exploited that way. Otherwise, mechanisms files that you want to use with this model generation software can be managed in two ways. The first way is through the command line interface (CLI). The `pyplume.mech` is the command which will be used to invoke the necessary commands to manage the mechanisms.

To list the functions, invoke the help menu.
```shell
  pyplume.mech -h
```
```shell
usage: pyplume.mech [-h] [-r] [-l] [-a ADD] [-d DELETE] [-t]

This is the commandline interface for managing mechanism files of PyPlume.

optional arguments:

  -h, --help            show this help message and exit
  -r, --restore         set this flag to restore mechanism files.
  -l, --list            set this flag to list mechanism files.
  -a ADD, --add ADD     this can be used to add a mechanism file to the codes internal data.
  -d DELETE, --delete DELETE
                        this can be used to delete a mechanism file to the codes internal data.
  -t, --test            set this flag to run test functions.
```

After that there are only 5 other options: restore, list, add, delete, and test.

`pyplume.mech -r` restores the original mechanisms from a backup folder. This will overwrite any mechanisms with the same name as the original set of mechanisms.

`pyplume.mech -l` lists all the mechanisms currently available to the program.

`pyplume.mech -a mySuperCoolMech.cti` will add `mySuperCoolMech.cti` to the mechanisms available to the program.

`pyplume.mech -d mySuperCoolMech.cti` will delete `mySuperCoolMech.cti` from the mechanisms available to the program.

`pyplume.mech -t` will run a set of test functions designed to test this module.

The second way of managing mechanism files is through a script. This can be done with internal functions as
```python
import pyplume.mech
import pyplume.tests.testMechs

cti = 'mySuperCoolMech.cti'

pyplume.mech.mechFileAdd(cti) #Add mechanism file

pyplume.mech.mechFileDelete(cti) #Delete mechanism file

pyplume.mech.mechFileRestore() #Restore mechanism files

pyplume.mech.mechFileList() #list mechanism files

pyplume.tests.testMechs.CLI() #Run tests for mech management

```

### Model generation tool
The model generation tool can be implemented with the most functionality in a script but there is also a command line interface. The code works by creating an object which represents a complex reactor network created by Cantera. This reactor network is made up of a three reservoirs, a combustor, and the desired exhaust network. One reservoir is for the fuel/air mixture, one is for atmosphere entrainment, and one is for the final exhaust stage. The combustor assumes the mechanism of the fuel/air reservoir and the exhaust is the focus of the model which has the most configurable options. The reactors in the system are connected via multiple `MassFlowController` objects based on an adjacency matrix of connections. The fuel/air reservoir is connected to the combustor with the mass flow function that follows.
```python
  def massFlow(t):
    return combustor.mass/residenceTime
```
The mass flow is then maintained to the first exhaust reactor with the same mass flow function to ensure continuity. Successive reactors then evenly divide their mass amongst their sinks as follows.
```python
  def mdot(t,fcn=None):
    return (self.reactors[fcn.ridx].mass / self.residenceTime(t)) / fcn.sink
```
Terminal exhaust reactors are connected to an exhaust reservoir by the following mass flow function, which acts as the final stage of the process.
```python
  def mdot(t,fcn=None):
    return (self.reactors[fcn.ridx].mass / self.residenceTime(t))
```
Finally, the entrainment functions are connected to the specified reactors via a provided entrainment function. These functions are ultimately controlled by the residence time function provided. The goal of this connection method was to implement and maintain a simple form of continuity that provided a less well mixed scenario.

#### Creating model object

A model can be generated in multiple ways. The first is by creating an adjacency matrix, specifying mechansims for air, fuel, and exhaust, providing mass flow functions, and setting other configuration options. Forming the adjacency matrix is the most cumbersome part of this so some class methods have been included for this task. These class methods take other parameters used in determination of the adjacency matrix as well as the remaining parameters of the class constructor.

##### Class constructor

```python
class PlumeModel(object):
    """PlumeModel class is used to generate a reactor network for modeling exhaust plume"""

    def __init__(self, mechs, connects, residenceTime=lambda t: 0.1, entrainment=lambda t:0.1,setCanteraPath=None,build=False):
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
```

##### Simple model
```python
@classmethod
  def simpleModel(cls,mechs=["gri30.cti","air.cti","gri30.cti"],residenceTime=lambda t: 0.1, entrainment=lambda t:0.1,fpath="simple.hdf5",setCanteraPath=None,build=False):
      """This classmethod build a 1 reactor exhaust model. It has extra parameters than the class
      Linear expansion model:
      [fuel res]->[combustor]->[ex1]->[exRes]
      [farfield]->[ex1]
      """
```
##### Linear Expansion Model
```python
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
```

##### Grid model
```python
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
```

This looks something like

```python
  import pyplume.model.PlumeModel
  plumeModel = PlumeModel.linearExpansionModel()
```

#### Setting Atmophere and Fuel conditions
Configuration can be important to any simulation, this can be skipped if you want to use the configuration inside the supplied mechanism files.
Otherwise, `PlumeModel` has 3 attributes that it uses to maintain the conditions of the model.
`fuel` which is a Cantera Solution object for the fuel,
`atmosphere` which is a Cantera Solution object for the atmosphereic conditions, and `exhausts` which is a list of Cantera Solution object(s). The fuel an atmosphere conditions can be configured for each reactor as you would configure them for any other Cantera solution object. Note, that fuel is considered to be the fuel air mixture for the combustor. Since the focus on this project is the exhaust, the exhaust is produced by a single reactor which is fed into the exhaust system. The atmosphere is for entrainment purposes.

##### In a script
```python
plumeModel.fuel.TPX = 300.0, 101325, 'CH4:1, O2:0.5' #K, Pa, Mole Fractions
plumeModel.atmosphere.TPX = 300.0, 101325, 'O2:0.21, N2:0.78, AR:0.01' #K, Pa, Mole Fractions
plumeModel.exhausts[3].TPX= 300.0, 101325, 'O2:0.21, N2:0.78, AR:0.01' #Set conditions for exhaust 3
```

Now that the `plumeModel`'s conditions are set, it can be advanced to a specific time or to steady state as

```python
plumeModel(0.1) #advance to time=0.1 s
plumeModel.steadyState()
```

The data for the `plumeModel` can be viewed in one of two ways. If `fpath` is specified in the constructor or class methods then an `hdf5` file is produced which contains the data generated. The `plumeModel` can also be called with the `print` function.
```python
  plumeModel.ptype=True #True for sparse print, False for dense print
  print(plumeModel)
```
The sparse print produces the following. Dense printing adds mass fractions of each reactor.
```
PyPlume Network Model Summary:
fuel: T: 300.00 K, V: 1.00 m^3, mass: 0.08 kg
atmosphere: T: 300.00 K, V: 1.00 m^3, mass: 1.18 kg
combustor: T: 300.00 K, V: 1.00 m^3, mass: 0.08 kg
exhaust0: T: 300.00 K, V: 1.01 m^3, mass: 0.09 kg
exhaust: T: 300.00 K, V: 1.00 m^3, mass: 1.18 kg
Reactor Network Mass Fractions:
```
If you want to generate the file then manage it separately, the `h5Writer` class can be used for this purpose.
```python
  import output,numpy
  h5w=output.h5Writer.existingFile('simple.hdf5')
  file = h5w.f #this gets file object
  h5w(numpy.ones(h5w.dshape[1])) #This appends a vector of ones to the hdf5 file.
```

##### On the command line

The command line is currently only set up to run class method models. This can be with `pyplume.model chosenModel`.

```shell
usage: pyplume.model [-h] [-ss] [-t0 [T0]] [-tf [TF]] [-dt [DT]] [-t] [-v]
                     {simple,grid,linear}

This is the commandline interface for running an exhuast network.


positional arguments:
  {simple,grid,linear}  This is a required arguement that specifies the model
                        which will be used. Currently implemented choices are
                        simple, grid, and linear.

optional arguments:
  -h, --help            show this help message and exit
  -ss, --steady         set this flag run to steady state after integration
  -t0 [T0]              Initial integration time
  -tf [TF]              Final integration time
  -dt [DT]              Integration time interval
  -t, --test            set this flag to run test functions.
  -v, --verbose         set this flag to run print statements during the process.
```

An example of this is
```shell
  pyplume.model simple -v -ss -t
```
which runs the `simple` model with the `--verbose, --steady, and --test` options.
This produces
```
Creating simple model and building network.
Advancing to time: 0.000.
Advancing to time: 0.100.
.
.
Advancing to time: 0.900.
Advancing to time: 1.000.
Advancing to steady state.
Running model test suite.
========================================================= test session starts ==========================================================
platform linux -- Python 3.6.10, pytest-5.4.1, py-1.8.1, pluggy-0.13.1 -- /home/sokato/miniconda3/envs/pyplume/bin/python
cachedir: .pytest_cache
rootdir: /home/sokato
collected 5 items

../../miniconda3/envs/pyplume/lib/python3.6/site-packages/pyplume/tests/testModel.py::test_linearExpansionModel PASSED           [ 20%]
.
.
```

### Plotting
The methods for plotting the generated data are contained in the an `hdf5` or in script are found in `pyplume.figs`

### Statistical methods
The methods for plotting the generated data are contained in the an `hdf5` or in script are found in `pyplume.stats`

### Testing
Each python file has an associated test file which contains unit test functions. As the package is developed, more functions will be added and integrated function tests will be added. Likewise, more information will be included here when possible.
