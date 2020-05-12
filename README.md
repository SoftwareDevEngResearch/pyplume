# PyPlume
This package is intended to build reactor network models for exhaust plumes based on user input and incorporate some methods for analysis of the results.

### Model generation tool
The model generation tool can be implemented with the most functionality in a script but there is also a command line interface. The code works by creating an object which represents a complex reactor network created by Cantera.

#### Creating model object

A model can be generated in multiple ways. The first is by creating an adjacency matrix, specifying mechansims for air, fuel, and exhaust, providing mass flow functions, and setting other configuration options. Forming the adjacency matrix is the most cumbersome part of this so some class methods have been included for this task. These class methods take other parameters used in determination of the adjacency matrix as well as the remaining parameters of the class constructor.

#### Class constructor

```python
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
```

#### Linear Expansion Model
```python
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
```

#### Grid model
```python
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
```




#### Setting Air and Fuel conditions
##### In a script
```python
plumeModel.fuel.TPX = 300.0, 101325, 'CH4:1' #K, Pa, Mole Fractions
plumeModel.air.TPX = 300.0, 101325, 'O2:0.21, N2:0.78, AR:0.01' #K, Pa, Mole Fractions
```

##### On the command line


### Mechanism management

Mechanism files that you want to use with this model generation software can be managed in two ways. The first way is through the command line interface (CLI). The `pyplume.mech` is the command which will be used to invoke the necessary commands to manage the mechanisms.

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

### Statistical methods

---Not implemented yet---

### Plotting

---Not implemented yet---

### Testing
Each python file has an associated test file which contains unit test functions. As the package is developed, more functions will be added and integrated function tests will be added.
