# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 01:01:42 2021

@author: Dell
"""

from gurobipy import *
import numpy as np
import csv
import os
import matplotlib.pyplot as plt

# Question 2

#Amount of material j required by product i
path = 'Pb1_requirements.csv' # change to y ====our file directory
data = np.genfromtxt(path, dtype=str, delimiter=',', encoding='utf-8-sig')
Requirements = data.astype(np.float) 
print(Requirements) #referred to as a[i,j] in formulation

#Amount of material j available in week t
path = 'Pb1_availability.csv' # change to y ====our file directory
data = np.genfromtxt(path, dtype=str, delimiter=',', encoding='utf-8-sig')
Availability = data.astype(np.float)
print(Availability) #referred to as v[j,t] in formulation

#Profit per unit of product i
path = 'Pb1_unitprofit.csv' # change to y ====our file directory
data = np.genfromtxt(path, dtype=str, delimiter=',', encoding='utf-8-sig')
Profit = data.astype(np.float)
print(Profit) #referred to as pi[i] in formulation

#Holding cost per unit in week t
path = 'Pb1_holdingcost.csv' # change to y ====our file directory
data = np.genfromtxt(path, dtype=str, delimiter=',', encoding='utf-8-sig')
HoldingCosts = data.astype(np.float)
print(HoldingCosts) #referred to as h[t] in formulation

#Demand for product i in week t
path = 'Pb1_demand.csv' # change to y ====our file directory
data = np.genfromtxt(path, dtype=str, delimiter=',', encoding='utf-8-sig')
Demand = data.astype(np.float)
print(Demand) #referred to as d[i,t] in formulation

# Indices for products, materials and weeks
products = range(len(Profit)) 
materials = range(len(Availability)) 
weeks = range(len(HoldingCosts))

# Setting up model object
m = Model()

# Define variables, variable bounds, and objective separately
x = m.addVars(products, weeks) #product i produced in week t
b = m.addVars(products, weeks) #starting inventory of product i in week t 
e = m.addVars(products, weeks) #ending inventory of product i in week t
s = m.addVars(products, weeks) #product i sold in week t

m.setObjective(sum(sum(Profit[i] * s[i,t] - HoldingCosts[t] * e[i,t] for i in products) for t in weeks))
m.modelSense = GRB.MAXIMIZE

for i in products:
    for t in weeks:
        m.addConstr(x[i,t] >= 0.0)
        m.addConstr(b[i,t] >= 0.0)
        m.addConstr(e[i,t] >= 0.0)
        m.addConstr(s[i,t] >= 0.0)
        
### Constraints ###

# Demand 
for i in products:
    for t in weeks:
        m.addConstr(s[i,t] <= Demand[i,t])

# Inventory Dynamics    
for i in products:
    for t in weeks:
        if t == 0:
            m.addConstr(b[i,t] == 0)
        else:
            m.addConstr(b[i,t] == e[i, t-1])
        
for i in products: 
    for t in weeks:
        m.addConstr(e[i,t] == b[i,t] + x[i,t] - s[i,t])
    
# Material Availability 
for j in materials:
    for t in weeks:
        m.addConstr(sum(Requirements[i,j] * x[i,t] for i in products) <= Availability[j,t])

# Solve
m.optimize()

# Print optimal cost
print(m.objVal)

# Print optimal solution
for i in products:
    for t in weeks:
        print(i, t, x[i,t].x)


# Question 3

Total_Sales_Profit = 0
for i in products:
    for t in weeks:
        Total_Sales_Profit += Profit[i] * s[i,t].x

print("Total Sales Profit: ", Total_Sales_Profit)

Holding_Costs = 0
for i in products:
    for t in weeks:
        Holding_Costs += HoldingCosts[t] * e[i,t].x        

print("Holding Costs: ", Holding_Costs)

# Question 4

for i in products:
    d = dict()
    d1 = dict()
    for t in weeks:
        d[t+1] = x[i,t].x
        d1[t+1] = e[i,t].x
    lists_manufactured = sorted(d.items())
    lists_stored = sorted(d1.items())
    x_manufactured, y_manufactured = zip(*lists_manufactured)
    x_stored, y_stored = zip(*lists_stored)
    plt.plot(x_manufactured, y_manufactured, label = "Manufactured")
    plt.plot(x_stored, y_stored, label = "Stored")
    plt.title("Units Stored and Manufactured for Product " + str(i+1))
    plt.xlabel("Weeks")
    plt.ylabel("Number of Units")
    plt.legend()
    plt.show()

# Question 5

# materials fully used in week 30

utilized = 0
for j in materials:
        if round(sum([Requirements[i,j] * x[i,29].x for i in products]),0) == round(Availability[j,29],0):
            utilized += 1
        else:
            pass

print('Number of materials fully used in week 30: ', utilized)

# products with demand fully satisfied in week 30

satisfied = 0
for i in products:
        if s[i,29].x == Demand[i,29]:
            satisfied += 1
        else:
            pass
        
print('Number of products with demand fully met: ', satisfied)
