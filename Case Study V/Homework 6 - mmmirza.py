# -*- coding: utf-8 -*-
"""
Created on Thu Oct 21 13:39:01 2021

@author: Dell
"""

import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

## PART A ##

# Read in probabilities vector for each of 1000 scenarios i.e. q[s] in the formulation 
# Question: What's the difference in reading file as np or pd as in homework 4
path = 'Pb1_prob.csv' # change to y ====our file directory
data = np.genfromtxt(path, dtype=str, delimiter=',', encoding='utf-8-sig')
q = data.astype(np.float) 
print(q) 

# Read in the demand matrix for each of the 4 classes under each of the 1000 scenarios i.e. #d[i,s] in the formulation
path = 'Pb1_D_stochastic.csv' # change to y ====our file directory
data = np.genfromtxt(path, dtype=str, delimiter=',', encoding='utf-8-sig')
d = data.astype(np.float) 
print(d) 

# price of class i seat
p = [400, 500, 800, 1000] # p[i] in the formulation

# space required by class i seat with respect to economy
α = [1, 1.2, 1.5, 2] # α[i] in the formulation

# Capacity of the aircraft in terms of economy seats
C = 190

# Indices for scenarios and classes
scenarios = range(len(q))
classes = range(len(d))

# Initialize Gurobi model
m = gp.Model('Flight')

# Add variables 
x = m.addVars(classes, vtype = GRB.INTEGER, lb = 0.0) # first stage i.e. x[i]
y = m.addVars(classes, scenarios, vtype = GRB.INTEGER, lb = 0.0) # second stage i.e. y[i,s]

# Set objective function to minimize the total tour length
m.setObjective(sum(sum(q[s] * p[i] * y[i,s] for i in classes) for s in scenarios))
m.modelSense = GRB.MAXIMIZE

# Add Constraints 

for s in scenarios:
    for i in classes:
        m.addConstr(y[i,s] <= d[i,s])
        
for s in scenarios:
    for i in classes:
        m.addConstr(y[i,s] <= x[i])
        
m.addConstr(sum(α[i] * x[i] for i in classes) <= C)

# Solve
m.optimize()

## PART B ##

# Print optimal distance
print(m.objVal)

display = ['Economy', 'Economy+', 'Business', 'First Class']

# Output Print
for i in classes:
    print(display[i], "class is allocated", x[i].x, "seats")

## PART C ##

#scenarios where y[i,s] <= d[i] i.e. number of scenarios where we sold less than the demand
no_of_scenarios_1 = [0, 0, 0, 0]

for i in classes:
    for s in scenarios:
        if y[i,s].x < d[i,s]:
            no_of_scenarios_1[i] += 1
        else:
            None

for i in classes:
    print("\nFor", display[i], "Class", "there were", no_of_scenarios_1[i]/10, "% scenarios where seats configured to the class were lower than the demand")
            
#scenarios where y[i,s] <= d[i] i.e. number of scenarios where we sold less than the class capacity
no_of_scenarios_2 = [0, 0, 0, 0]

for i in classes:
    for s in scenarios:
        if y[i,s].x < x[i].x:
            no_of_scenarios_2[i] += 1
        else:
            None

for i in classes:
    print("\nFor", display[i], "Class", "there were", no_of_scenarios_2[i]/10, "% scenarios where seats configured to the class were higher than the demand")

## PART D ##

# The basic idea is to understand that 3 price scenarios with 1000 demand scenarios will give us a total of
# 3000 scenarios, each with a probability that is a product of that specific demand and price scenario
# since price and demand scenarios are independent and a product of the two would make sense!

# The probabilities in file q will be updated such that the length of the file is now 3000, which is achieved
# by multiplying the probability of each price with the probability of all demand scenario probabilities

# The scenarios in file d will be updated such that the number of existing columns is repeated thrice
# Giving us a total of 3000 demand scenarios

# The list p will have 2 additional set of 4 prices added, each of which will be repeated 1000 times to give
# a total of 3000 price scenarios