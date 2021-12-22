# -*- coding: utf-8 -*-
"""
Created on Sat Sep 25 17:18:55 2021

@author: Dell
"""

from gurobipy import *
import numpy as np
import csv
import os
import matplotlib.pyplot as plt

## QUESTION 2 ##

# Areas: containing the number of residents in third column
path = 'Pb2_areas.csv' # change to y ====our file directory
data = np.genfromtxt(path, dtype=str, delimiter=',', encoding='utf-8-sig')
Areas = data.astype(np.float) 
print(Areas) 

# Shelters: containing the capacity in third column 
path = 'Pb2_shelters.csv' # change to y ====our file directory
data = np.genfromtxt(path, dtype=str, delimiter=',', encoding='utf-8-sig')
Shelters = data.astype(np.float) 
print(Shelters) 

# Indices for residential areas and shelter sites
areas = range(len(Areas)) 
shelters = range(len(Shelters)) 

# Creating 200 x 40 array containing distances of for area i to shelter site j
distances = np.empty((200, 40), float)
for i in areas:
    for j in shelters:
        distances[i,j] = abs(Areas[i,0] - Shelters[j,0]) + abs(Areas[i,1] - Shelters[j,1])

# Setting up model object
m = Model()

# Define variables, variable bounds, and objective separately
x = m.addVars(shelters, vtype = GRB.BINARY) #indicator variable if shelter j is built or not
y = m.addVars(areas, shelters, vtype = GRB.BINARY) #indicator variable if area i is assigned to shelter j
r = Areas[:, 2] #number of residents in area i
c = Shelters[:, 2] #maximum capacity of shelter j

m.setObjective(sum(sum(r[i] * distances[i,j] * y[i,j] for i in areas) for j in shelters))
m.modelSense = GRB.MINIMIZE

# Constraints 

# resources constraint (sum of the shelters built should be 10)
m.addConstr(sum(x[j] for j in shelters) <= 10)

# shelter capacity constraint (for each shelter..., # of residents assigned from all areas i.e. sum <= capacity)
# note: this constraint also ensures that an area is assigned to a site only if a shelter is built there
for j in shelters:
        m.addConstr(sum(r[i] * y[i,j] for i in areas) <= c[j] * x[j])

# all residents access constraint (for each area..., they should be assigned to the same/one shelter)
# note: this constraint also ensures that an area is assigned to a shelter actually built
for i in areas:
        m.addConstr(sum(y[i,j] for j in shelters) == 1)
        
# Solve
m.optimize()

# Print optimal cost
print(m.objVal)

# Output Print
for i in areas:
    for j in shelters:
        if y[i,j].x == 1:
            print("Residential Area", i + 1, "is assigned to shelter", j + 1, "at a distance of", round(distances[i,j], 2))

## QUESTION 3 ##

# Setting up model object
m2 = Model()

# Define variables, variable bounds, and objective separately
x2 = m2.addVars(shelters, vtype = GRB.BINARY) #indicator variable if shelter j is built or not
y2 = m2.addVars(areas, shelters, vtype = GRB.BINARY) #indicator variable if area i is assigned to shelter j
D = m2.addVar(vtype = GRB.CONTINUOUS) #maximum distance

m2.setObjective(D)
m2.modelSense = GRB.MINIMIZE

# Constraints 

# reources constraint (sum of the shelters built should be 10)
m2.addConstr(sum(x2[j] for j in shelters) <= 10)

# shelter capacity constraint (for each shelter..., # of residents assigned from all areas i.e. sum <= capacity)
# note: this constraint also ensures that an area is assigned to a site only if a shelter is built there
for j in shelters:
        m2.addConstr(sum(r[i] * y2[i,j] for i in areas) <= c[j] * x2[j])

# all residents access constraint (for each area..., it should be assigned to the same/one shelter)
# note: this constraint also ensures that an area is assigned to a shelter actually built
for i in areas:
        m2.addConstr(sum(y2[i,j] for j in shelters) == 1)

# maximum access distance constraint (for each area..., it's access to the assigned shelter <= objective)
# note: objective function forces the RHS down which pushes down the LHS of this constraint   
for i in areas:
    m2.addConstr(sum(distances[i,j] * y2[i,j] for j in shelters) <= D)
        
# Solve
m2.optimize()

# Print optimal cost
print(m2.objVal)

# Output Print
for i in areas:
    for j in shelters:
        if y2[i,j].x == 1:
            print("Residential Area", i + 1, "is assigned to shelter", j + 1, "at a distance of", round(distances[i,j], 2))

## QUESTION 5 ##

# Model 1
plt.figure(1)
plt.title("Model 1")
model_1 = []
for i in areas:
    for j in shelters:
        if y[i,j].x == 1:
            model_1.extend([distances[i,j]] * int(r[i]))
            
plt.hist(model_1, bins = 20)
plt.xlabel("Distance in miles between areas and shelters")
plt.ylabel("Number of residents")

# Model 2
plt.figure(2)
plt.title("Model 2")
model_2 = []
for i in areas:
    for j in shelters:
        if y2[i,j].x == 1:
            model_2.extend([distances[i,j]] * int(r[i]))
            
plt.hist(model_2, bins = 20)
plt.xlabel("Distance in miles between areas and shelters")
plt.ylabel("Number of residents")
