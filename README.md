# PyPlume
This package is intended to build reactor network models for exhaust plumes based on user input and incorporate some methods for analysis of the results.

### Model generation tool
The model generation tool can be implemented with the most functionality in a script but there is also a command line interface. The code works by creating an object which represents a complex reactor network created by Cantera.

#### Creating model object
```python
class PlumeModel(self,ncols,cmech,emech,efun=lambda x:x*x,setCanteraPath=None,build=False,bin=False)
"""
    Parameters:
    ncols - number of columns in the exhaust reactor network.
    cmech - mechanism file for the combustor as a path to file (relative or absolute)
    emech - mechanism file for the exhaust stream.
    efun - a single parameter function e.g. f(n) that returns the number of reactors in a column
        default: efun=lambda x:x*x
    setCanteraPath - path variable to cantera mech files
    build -  boolean that builds network strictly from configuration in mechanism files (T,P) if true.
        default: build=false
    bin - boolean that builds
  """
```

#FIXME
```python
plumeModel = PlumeModel(2,"gri30.cti","air.cti") #Create model object
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
