#Programmer: Anthony walker
#This file will contain functions for statistical analysis of data generated.
import output, argparse, pytest
import pyplume.tests.testStatistics

def statisticsCLI():
    """This function is used for the command line interface option of mech"""
    parser = argparse.ArgumentParser(description="""This is the commandline interface for statistical analysis.
    """)
    parser.add_argument("-s","--statistical",action='store_true',help="""statistics.""")
    parser.add_argument("-t","--test",action='store_true',help="""set this flag to run test functions.""")
    parser.add_argument("-v","--verbose",action='store_true',help="""set this flag to run print statements during the process.""")
    parser.add_argument("-w","--write",action='store_true',help="""set this flag to write statistics as they are being generated""")
    parser.add_argument("-d","--display",action='store_true',help="""set this flag to display statistics.""")

    args = parser.parse_args()

    if args.statistical:
        print("Not-implemented-yet")

    if args.test:
        if args.verbose:
            print("Running statistics test suite.")
        pyplume.tests.testStatistics.runTests()
