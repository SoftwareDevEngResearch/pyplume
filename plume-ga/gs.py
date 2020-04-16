# @Author: Anthony Walker
# @Date:   2020-04-09T12:53:51-07:00
# @Email:  walkanth@oregonstate.edu
# @Filename: gs.py
# @Last modified by:   Anthony Walker
# @Last modified time: 2020-04-10T09:53:34-07:00

#imports
import cantera

gas1 = cantera.Solution('gri30.xml')
gas1.TP = 600,101325 #K,Pa
phi = 0.8
gas1.X = {'CH4':1, 'O2':2/phi, 'N2':2*3.76/phi}
