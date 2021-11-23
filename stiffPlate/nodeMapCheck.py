#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 18:00:03 2021

@author: sengelstad6
"""
from tacs.pytacs import pyTACS

from tacs import functions

import numpy as np

import os

structOptions = {'writeSolution': True, }
        
datFile = "nastran_CAPS.bdf"

# Load BDF file
FEASolver = pyTACS(datFile, options=structOptions)
# Set up TACS Assembler
FEASolver.initialize()
#add functions
evalFuncs = ['wing_mass', 'ks_vmfailure']

# Read in forces from BDF and create tacs struct problems
SPs = FEASolver.createTACSProbsFromBDF()
for caseID in SPs:
       SPs[caseID].addFunction('wing_mass', functions.StructuralMass)
       SPs[caseID].addFunction('ks_vmfailure', functions.KSFailure, safetyFactor=1.5, KSWeight=100.0)
#print("ran pytacs")
# Solve each structural problem and write solutions
funcs = {}; funcsSens = {}
for caseID in SPs:
    SPs[caseID].solve()
    SPs[caseID].evalFunctions(funcs,evalFuncs=evalFuncs)
    SPs[caseID].evalFunctionsSens(funcsSens,evalFuncs=evalFuncs)
    SPs[caseID].writeSolution(outputDir=os.path.dirname(__file__))

funcKeys = funcs.keys()
nfunc = len(funcKeys)

dfdX = funcsSens['load_set_001_wing_mass']['Xpts']


#reorder nodes, start at
TACSnodeMap = FEASolver.meshLoader.getGlobalToLocalNodeIDDict() #error in nodemap, less nodes
print("TACS Node Map:", TACSnodeMap)

nnodes = int(len(dfdX)/3)
dfdX = dfdX.reshape(nnodes,3)

dfdX_bdf = np.zeros((nnodes,3))
print("Length TACS node map: ",len(TACSnodeMap))
print("nnodes in mesh: ",nnodes)

for i in range(nnodes):
    #i is bdf node, tacsNode is globalNode
    tacsNode = TACSnodeMap[i]
    dfdX_bdf[i,:] = dfdX[tacsNode,:]