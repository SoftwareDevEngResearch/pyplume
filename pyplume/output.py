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

class h5Writer(object):
    """docstring for h5Writer."""

    def __init__(self, fpath, keys):
        super(h5Writer, self).__init__()
        self.fpath = fpath
        self.keys = keys

    def __call__(self,data):
        """Use the call function to write data to current hdf5 handle."""
        print("write")

def solutionWrite(plume, fname):
    """Use this function to write the solution to an hdf5 file."""
    print("Writing solution")
