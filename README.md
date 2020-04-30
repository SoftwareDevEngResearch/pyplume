# plume-generation-and-analysis
This package is intended to build reactor network models for exhaust plumes based on user input and incorporate some methods for analysis of the results.

### Model generation tool

---Not implemented yet---

### Mechanism management

Mechanism files that you want to use with this model generation software can be managed in two ways. The first way is through the command line interface (CLI). The `pyplume.mech` is the command which will be used to invoke the necessary commands to manage the mechanisms.

To list the functions, invoke the help menu.
```
  pyplume.mech -h
```
```
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
