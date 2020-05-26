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

### Model generation tool
The model generation tool can be implemented with the most functionality in a script but there is also a command line interface. The code works by creating an object which represents a complex reactor network created by Cantera. This reactor network is made up of a two reservoirs, a combustor, and the desired exhaust network. One reservoir is for the fuel/air mixture and another for the atmosphere. The combustor assumes the mechanism of the fuel/air reservoir and the exhaust is the focus of the model which has the most configurable options. The fuel/air reservoir is connected to the combustor via a `MassFlowController` where reaction occurs is fed to the exhaust via a `PressureController`. The exhaust reactors remaining then include entrainment and mass flow via `MassFlowController`. Functions can be specified for inlet mass flow and entrainment mass flow as a function of time. Continuity is then used in a simple manner to control the flow of mass between the exhaust network. This can be controlled to some extent via the adjacency matrix supplied called `connects`.

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

##### Linear Expansion Model
```python
@classmethod
  def linearExpansionModel(cls,n=10,mechs=["gri30.cti","air.cti","gri30.cti"],residenceTime=lambda t: 0.1, entrainment=lambda t:0.1,setCanteraPath=None,build=False):
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

##### Grid model
```python
@classmethod
  def gridModel(cls,n=3,m=3,mechs=["gri30.cti","air.cti","gri30.cti"],residenceTime=lambda t: 0.1, entrainment=lambda t:0.1,setCanteraPath=None,build=False):
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
```

Now that you have created your model object with the constructor or one of the class methods, e.g,
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

##### On the command line

---Not yet Implemented---
<!-- Working on this -->

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
