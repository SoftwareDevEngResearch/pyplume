import h5py
import numpy as np
import time

def statementTVM(pReact):
    """Use this funciton to produce the TVM statemet"""
    T,V,mass = pReact.T,pReact.volume,pReact.mass
    statement="\n{}: T: {:0.2f} K, V: {:0.2f} m^3, mass: {:0.2f} kg".format(pReact.name,T,V,mass)
    return statement
#Printing methods
def sparsePrint(plume):
    """This overloads the print function."""
    statement = 'PyPlume Network Model Summary:'
    statement += statementTVM(plume.fuelReservoir)
    statement += statementTVM(plume.atmosReservoir)
    for react in plume.reactors:
        statement += statementTVM(react)
    statement += statementTVM(plume.exhaustReservoir)
    return statement

def densePrint(plume):
    """This overloads the print function."""
    statement = 'PyPlume Network Model Summary:'
    statement += statementTVM(plume.fuelReservoir)
    statement += statementTVM(plume.atmosReservoir)

    for react in plume.reactors:
        statement += statementTVM(react)
    statement += statementTVM(plume.exhaustReservoir)
    statement += '\nReactor Network Mass Fractions:'
    keys = []
    added = []
    state=plume.network.get_state()

    for i in range(len(state)):
        name = plume.network.component_name(i)
        keys.append(name)

    for i,key in enumerate(keys):
        keyname,element = key.split(":")
        if keyname not in added:
            added.append(keyname)
            statement+="\n{}\n".format(keyname)
        statement+="{}: {:0.2e}, ".format(element,state[i])
    return statement
#External methods to writer class

def stringToOrd(strList):
    """Use this function to convert a string to an ord value."""
    keyOrds = []
    for cstr in strList:
        for ch in cstr:
            keyOrds.append(ord(ch))
        keyOrds.append(ord(','))
    return keyOrds

def ordToString(ordList):
    """Use this function to convert ord values to strings."""
    newStrList = []
    cstr = ""
    for cint in ordList:
        cstr += chr(cint)
        if cint == 44:
            newStrList.append(cstr[:-1])
            cstr = ""
    return newStrList

#Writer class
class h5Writer(object):
    """docstring for h5Writer."""

    def __init__(self, fpath, keys, initial, chunk=100,nonexistant=True):
        super(h5Writer, self).__init__()
        self.fpath = fpath
        self.keys = keys
        if nonexistant:
            self.f = h5py.File(fpath,'w')
            self.chunk = chunk
            self.dshape = [self.chunk,np.shape(initial)[0]]
            self.elements = [key.split(":")[1][1:] for key in self.keys]
            self.keys = [key.split(":")[0] for key in self.keys]
            self.itimes = []
            self.createSlices()
            self.createDataSets()
            self.storeData()
        else:
            self.f = h5py.File(fpath,'r+')


    def __call__(self,data,t):
        """Use the call function to write data to current hdf5 handle."""
        try:
            #Try to add to file
            for key in self.ukeys:
                self.f[key][self.time[key],self.slices[key]] = data[self.slices[key]]
                self.f['times'][self.time[key]] = t
        except Exception as e:
            print(str(e)+': resizing hdf5 dataset')
            #Adding now that is has been resized
            for key in self.ukeys:
                self.f[key].resize(self.dshape[0]+self.chunk,axis=0)
                self.f[key][self.time[key],self.slices[key]] = data[self.slices[key]]
            self.f['times'].resize(len(self.f['times'])+self.chunk,axis=0)
            self.f['times'][self.time[key]] = t
            self.dshape[0]+=self.chunk
        finally:
            #Updating times
            for key in self.ukeys:
                self.time[key]+=1
            self.itimes.append(t)
            self.updateTime()

    def updateTime(self):
        """Use this function to update time in hdf5."""
        self.f['time'][:] = [self.time[key] for key in self.time][:]

    def createSlices(self):
        """Use this function to create index slices."""
        #Creating unique keys
        self.ukeys = []
        for key in self.keys:
            if key not in self.ukeys:
                self.ukeys.append(key)
        #Creating slices
        self.slices = {key:0 for key in self.ukeys}
        prev = 0
        for key in self.ukeys:
            ct = self.keys.count(key)
            self.slices[key] = slice(prev,prev+ct,1)
            prev = ct

    def createDataSets(self):
        """This functions creates data sets in the file."""
        self.time = {}
        for key in self.ukeys:
            self.f.create_dataset(key, self.dshape, dtype=np.float64,chunks=tuple(self.dshape),maxshape=(None,None))
            self.time[key]=0 #Store current time
        self.f.create_dataset('times', (self.chunk,), dtype=np.float64,chunks=(self.chunk,),maxshape=(None,))


    def storeData(self):
        """Use this function to store data used to manage the hdf5 file."""
        #Adding keys
        tkeys=stringToOrd(self.keys)
        self.f.create_dataset('keys', np.shape(tkeys), dtype=int,data=tkeys)
        #Adding elements
        tkeys=stringToOrd(self.elements)
        self.f.create_dataset('elements', np.shape(tkeys), dtype=int,data=tkeys)
        #Adding ukeys
        tkeys=stringToOrd(self.ukeys)
        self.f.create_dataset('ukeys', np.shape(tkeys), dtype=int,data=tkeys)
        #Adding slices
        slNums = []
        for key in self.ukeys:
            sl = self.slices[key]
            slNums.append(sl.start)
            slNums.append(sl.stop)
        self.f.create_dataset('slices', np.shape(slNums), dtype=int, data=slNums)
        self.f.create_dataset('chunk' ,(1,) ,dtype=int, data=self.chunk)
        ttime = [self.time[key] for key in self.time]

        self.f.create_dataset('time',(len(ttime),),dtype=int,data=ttime)
        self.f.create_dataset('dshape',(len(self.dshape),),dtype=int,data=self.dshape)

    def setVars(self,time,chunk,slices,dshape,elements,ukeys):
        """This function is used by existingFile to set varibales for consistency."""
        self.time = {key:time[i] for i,key in enumerate(ukeys)}
        self.chunk = chunk
        self.slices = slices
        self.dshape = dshape
        self.elements = elements
        self.ukeys = ukeys

    def retrieve(self,i,key):
        """Use this function to retrieve data from the hdf5 file."""
        idx = self.elements.index(key)+self.slices[i].start
        k = self.ukeys[i]
        data = np.asarray(self.f[k])
        return np.copy(self.f['times'][:self.time[k]]),np.copy(data[:self.time[k],idx])

    @classmethod
    def existingFile(cls,fpath):
        """Use this to generate a writer for an existing file.
        Parameters:
        fpath - path to existing hdf5 file.
        """
        f = h5py.File(fpath,'r+')
        args = fpath,ordToString(list(f['keys'])),np.zeros(f['dshape'])
        nums = [n for n in f['slices']]
        slices = tuple()
        for i in range(0,len(nums),2):
            slices+=slice(nums[i],nums[i+1],1),
        vars = list(f['time']),f['chunk'],slices,f['dshape'],ordToString(f['elements']),ordToString(list(f['ukeys']))
        f.close()
        h5w = cls(*args,nonexistant=False)
        h5w.setVars(*vars)
        return h5w

if __name__ == "__main__":
    writer = h5Writer.existingFile("simple.hdf5")
    d,t = writer.retrieve(1,'CH4')
    print(t)
