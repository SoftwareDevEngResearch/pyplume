#!/bin/bash

#Uninstall package
pip uninstall pyplume -y

#Build
python setup.py sdist

#Re install
pip install ./dist/pyplume-0.0.1.tar.gz
