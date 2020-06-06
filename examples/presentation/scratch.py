import pyplume
import numpy as np

# Mechanism management
cti = 'test.cti'

pyplume.mech.mechFileAdd(cti) #Add mechanism file

pyplume.mech.mechFileDelete(cti) #Delete mechanism file

pyplume.mech.mechFileRestore() #Restore mechanism files

pyplume.mech.mechFileList() #list mechanism files

pyplume.tests.testMechs.runTests() #Run tests for mech management

# Model Use
pm = pyplume.model.PlumeModel.simpleModel()
pm.buildNetwork()
for t in np.arange(0.1,1.1,0.1):
    pm(t)
pm.steadyState()

pyplume.tests.testModel.runTests()
