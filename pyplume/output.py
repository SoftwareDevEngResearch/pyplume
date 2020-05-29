import h5py
import numpy as np

#Printing methods
def sparsePrint(plume):
    """This overloads the print function."""
    statement = 'PyPlume Network Model:\n'
    T,P,X = plume.fuel.TPX

    statement+="\nCombustor: T: {} K, P: {} Pa\n".format(T,P)
    statement+= ", ".join([plume.fuel.species_name(i)+":{:0.1f}".format(x) for i,x in enumerate(X)])

    T,P,X = plume.atmosphere.TPX
    statement+="\n\nAtmosphere: T: {} K, P: {} Pa\n".format(T,P)
    statement+= ", ".join([plume.fuel.species_name(i)+":{:0.1f}".format(x) for i,x in enumerate(X)])

    # for i,exhaust in enumerate(plume.exhausts):
    #     statement+="\n\nAtmosphere: T: {} K, P: {} Pa\n".format(T,P)
    #     statement+= ", ".join([plume.fuel.species_name(i)+":{:0.1f}".format(x) for i,x in enumerate(X)])
    return statement

def densePrint(plume):
    """This overloads the print function."""
    statement = 'PyPlume Network Model:\n'
    T,P,X = plume.fuel.TPX

    statement+="\nCombustor: T: {} K, P: {} Pa\n".format(T,P)
    statement+= ", ".join([plume.fuel.species_name(i)+":{:0.1f}".format(x) for i,x in enumerate(X)])

    T,P,X = plume.atmosphere.TPX
    statement+="\n\nAtmosphere: T: {} K, P: {} Pa\n".format(T,P)
    statement+= ", ".join([plume.fuel.species_name(i)+":{:0.1f}".format(x) for i,x in enumerate(X)])

    for i,exhaust in enumerate(plume.exhausts):
        statement+="\n\nAtmosphere: T: {} K, P: {} Pa\n".format(T,P)
        statement+= ", ".join([plume.fuel.species_name(i)+":{:0.1f}".format(x) for i,x in enumerate(X)])
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

    def __init__(self, fpath, keys, initial, chunk=100):
        super(h5Writer, self).__init__()
        self.fpath = fpath
        self.keys = keys
        self.f = h5py.File(fpath,'w')
        self.chunk = chunk
        self.dshape = [self.chunk,np.shape(initial)[0]]
        self.keys = [key.split(":")[0] for key in self.keys]
        self.createSlices()
        self.createDataSets()
        self.storeData()

    def __call__(self,data):
        """Use the call function to write data to current hdf5 handle."""
        try:
            #Try to add to file
            for key in self.ukeys:
                self.f[key][self.time[key],self.slices[key]] = data[self.slices[key]]
        except Exception as e:
            print(str(e)+': resizing hdf5 dataset')
            #Adding now that is has been resized
            for key in self.ukeys:
                self.f[key].resize(self.dshape[0]+self.chunk,axis=0)
                self.f[key][self.time[key],self.slices[key]] = data[self.slices[key]]
            self.dshape[0]+=self.chunk
        finally:
            #Updating times
            for key in self.ukeys:
                self.time[key]+=1

    def __del__(self):
        """This is the h5Writer destructor."""
        self.f.close() #Close file on destruction

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

    def storeData(self):
        """Use this function to store data used to manage the hdf5 file."""
        #Adding keys
        tkeys=stringToOrd(self.keys)
        self.f.create_dataset('keys', np.shape(tkeys), dtype=int,data=tkeys)
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
        ttime = [ self.time[key] for key in self.time]
        self.f.create_dataset('time',(len(self.time),),dtype=int,data=ttime)
        self.f.create_dataset('dshape',(len(self.dshape),),dtype=int,data=self.dshape)

    def setVars(self,time,chunk,slices,dshape):
        """This function is used by existingFile to set varibales for consistency."""
        self.time = time
        self.chunk = chunk
        self.slices = slices
        self.dshape = dshape

    @classmethod
    def existingFile(cls,fpath):
        """Use this to generate a writer for an existing file."""
        f = h5py.File(fpath,'r+')
        args = fpath,ordToString(list(f['keys'])),np.zeros(f['dshape'])
        vars = f['time'],f['chunk'],f['slices'],f['dshape']
        f.close()
        h5w = cls(*args)
        h5w.setVars(*vars)
        return h5w
if __name__ == "__main__":
    h5Writer.existingFile("simple.hdf5")
