
import output, argparse, pytest
import matplotlib.pyplot as plt
import pyplume.tests.testFigs

class figureGenerationKit(object):
    """docstring for figGenKit."""

    def __init__(self, fpath, save=True, show=False):
        """
        This is the constructor for the figureGenerationKit.
        Parameters:
        fpath -  path to existing hdf5 file written with h5Writer.
        save - a boolean specifying functions to save figures.
        show -  a boolean specifying functions to show figures.
        """
        super(figureGenerationKit, self).__init__()
        self.writer = output.h5Writer.existingFile(fpath)
        self.save = save
        self.show = show

    def saveShow(self,sstr=None):
        """This is a general function to call show and save"""
        if self.save:
            plt.savefig(sstr)
        if self.show:
            plt.show()

    def plotProperty(self,property,save=None,reactors=None):
        """Use this to plot a specific property for all reactors or a specified set."""
        for prop in property:
            rset = range(len(self.writer.ukeys)) if reactors is None else reactors
            data = [self.writer.retrieve(i,prop) for i in rset]
            lines = []
            lgdStrs = ['combustor']
            tstr = 'exhaust{}'
            ct=1
            for x,y in data:
                lines.append(plt.plot(x,y,linewidth=2))
                lgdStrs.append(tstr.format(ct))
            lgdStrs.pop()
            plt.title('{} of reactors'.format(prop))
            plt.xlabel('t [s]')
            plt.ylabel('{} [SI]'.format(prop))
            plt.legend(lgdStrs)
            sstr = prop+".pdf" if save is None else save
            self.saveShow(sstr)
            plt.close()

def figsCLI():
    """This function is used for the command line interface option of mech"""
    parser = argparse.ArgumentParser(description="""This is the commandline interface for
    plotting results from the exhaust network.
    """)

    parser.add_argument('filename', type=str,help="filename used for plotting.")
    parser.add_argument("-t","--test",action='store_true',help="""set this flag to run test functions.""")
    parser.add_argument("-v","--verbose",action='store_true',help="""Save plots as they are being generated.""")
    parser.add_argument("-w","--write",action='store_true',help="""Display plots as they are being generated""")
    parser.add_argument("-d","--display",action='store_true',help="""set this flag to run print statements during the process.""")
    parser.add_argument("-p","--property",nargs="+",default=['CH4','O2'],help="Plot a specific property")
    parser.add_argument("-r","--reactors",nargs="+",default=None,help="Specify reactors integer indices to plot property for a subset of reactors")

    args = parser.parse_args()

    if args.verbose:
        print("Creating figure generation kit.")
        tstr = "Plotting properties: "
        for prop in args.property:
            tstr+=prop
        print(tstr)
        if args.write:
            print("Writing data.")
        if args.display:
            print("Displaying data.")
    fgk = figureGenerationKit(args.filename,save=args.write,show=args.display)
    fgk.plotProperty(args.property,reactors=args.reactors)

    if args.test:
        if args.verbose:
            print("Running model test suite.")
        pyplume.tests.testFigs.runTests()

if __name__ == "__main__":
    fgk = figureGenerationKit("./simple.hdf5")
