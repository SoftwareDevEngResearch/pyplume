## Plume-Generation-and-Analysis
#### Funcitonality:
The goal of this project is to create a package that generates models for exhaust plumes based on user input, and provides some analysis tooling for the results.
I would like to focus more heavily on the analysis tooling so that this project does not fall to the wayside after this class.

The reactor model generation portion could be used by anyone interested in analyzing exhaust plumes with the reactor network approach. This could include students, professionals, and academics interested in combustion science of exhaust plumes. The some of the known inputs at this point will be the number of reactors and a mechanism cti file. The outputs will be state variables and species concentrations in some compact file format (probably hdf5).

The analysis portion of the package could be used by anyone generating similar output content. This may include some statistical analysis and figure generation but the specifics are still unknown at this point. This portion will utilize previous output or supplied similar data as input and generate figures and data based on incorporated methods and user preference.

#### Existing Methodology
The methods and software for this project already exist; my goal is to combine them into a complete package that can be installed directly and run with ease. Cantera exists for the kinetics and transport that will be used, Matplotlib has substantial plotting capabilities, and SciPy has statistical analysis tools. This does not build on my work at all but provides a tool that I can use to build from and analyze future results. This will be different from other work because it will generate models with a specific approach for a specific application. Tools like Cantera do not generate models but provide the tools to build them. It will also provide a complete interface to analyze the results and generate some useful output.

#### Dependencies
Currently I can say with certainty that this package will depend on:
  1. [Cantera](https://cantera.org/)
  2. [Matplotlib](https://matplotlib.org/)
  3. [Scipy](https://www.scipy.org/)

#### Interface
I do not intend to develop a GUI but have a CLI interface and provide usable script functions.

#### Overview
Ideally, the program will work overall in this manner:
  1. Use a script or the command-line to generate an executable model with variable inputs.
  2. Execute the model and store specified output in an appropriate format.
  3. Perform a set of basic statistical analysis methods on the data and generate figures and data from the results. e.g. uncertainty in the simulation.

I believe this is sufficient content for the term but the scope is likely to change slightly depending on time constraints.
