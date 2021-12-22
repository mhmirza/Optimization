# -*- coding: utf-8 -*-
"""
Created on Sat Oct  9 20:28:07 2021

@author: Dell
"""

from gurobipy import *
import numpy as np
import csv
import os
import matplotlib.pyplot as plt

## QUESTION 2 ##

# Composition: 1007 x 10 (c[i,n] i.e. amount of nutrient n in food item i in mg/ 100g of food)
path = 'Pb1_composition.csv' # change to y ==== our file directory
data = np.genfromtxt(path, dtype=str, delimiter=',', encoding='utf-8-sig')
c = data.astype(np.float) 
print(c) 

# Energy: 1007 x 1 (e[i] i.e. amount of energy in in food item i in Kcal/ 100g of food)
path = 'Pb1_energy.csv' # change to y ==== our file directory
data = np.genfromtxt(path, dtype=str, delimiter=',', encoding='utf-8-sig')
e = data.astype(np.float) 
print(e) 

# Mapping: 1007 x 6 (m[i, j] i.e. indicator variable if food item i belongs to food group j)
path = 'Pb1_mapping.csv' # change to y ==== our file directory
data = np.genfromtxt(path, dtype=str, delimiter=',', encoding='utf-8-sig')
m = data.astype(np.float) 
print(m) 

# Price: 1007 x 1 (p[i] i.e. price of food item i/ 100g of food)
path = 'Pb1_price.csv' # change to y ==== our file directory
data = np.genfromtxt(path, dtype=str, delimiter=',', encoding='utf-8-sig')
p = data.astype(np.float) 
print(p) 

# Nutrient Recommendations (r[n] i.e. requirements for nutrient n)
r = [20, 400, 7, 6.5, 0.57, 20, 0.7, 1.1, 0.050, 0.0005] 

#converting mg requirements to grams
for i in range(1, len(r)):
    r[i] = r[i]/1000

# Energy Lower Bound (l[j] i.e. lower bound for energy from food group j)
l = [1.1, 0.3, 35, 4, 0.9, 0.5]

# Energy Lower Bound (u[j] i.e. upper bound for energy from food group j)
u = [25.1, 8.7, 75, 33, 10.2, 8.5] 

# Indices for food items, food groups, and nutrients
items = range(np.shape(m)[0])
groups = range(np.shape(m)[1])
nutrients = range(np.shape(c)[1])

# Setting up model object
m1 = Model("weighted")

# Define variables, variable bounds, and objective separately
x = m1.addVars(items, lb = 0.0) #daily quantity in grams of each food item i

# Set up two variables to capture the two objectives 
z1 = m1.addVar(lb = 0.0) # for minimizing the daily energy intake by a child
z2 = m1.addVar(lb = 0.0) # for minimizing the total daily cost of the diet

DailyEnergy = LinExpr() # daily energy (can also use DailyEnergy = 0)
for i in items:
    DailyEnergy += x[i] * e[i]/100

DailyCost = LinExpr() # daily cost (can also use DailyCost = 0)
for i in items:
    DailyCost += x[i] * p[i]/100
    
m1.addConstr(z1 == DailyEnergy)
m1.addConstr(z2 == DailyCost)

# Constraints 

# i) #Nutrient Requirements
for n in nutrients:
    m1.addConstr(sum(x[i] * c[i,n]/ 100000 for i in items) >= r[n])
    
# ii) Energy Restrictions
for j in groups:
    m1.addConstr(sum(x[i] * e[i]/100 * m[i, j] for i in items) <= u[j] * DailyEnergy/100)
    m1.addConstr(sum(x[i] * e[i]/100 * m[i, j] for i in items) >= l[j] * DailyEnergy/100)
    
# Weighted Approach #

alpha_values = [0, 0.001, 0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99, 0.999, 1]
weighted_approach = np.zeros([len(alpha_values), 2])

for i in range(len(alpha_values)):
    alpha = alpha_values[i]
    m1.setObjective(alpha * z1 + (1 - alpha) * z2, GRB.MINIMIZE)
    
    # Solve
    m1.optimize()
    
    # Reporting the breakdown of the objective
    print ("total daily energy intake: ", DailyEnergy.getValue())
    print ("total daily cost: ", DailyCost.getValue())
   
    weighted_approach[i, 0] = z1.x
    weighted_approach[i, 1] = z2.x

# Plot Pareto frontier
print(weighted_approach)
plt.title('Daily Energy Intake v/s Diet Cost')
plt.xlabel('Diet Cost')
plt.ylabel('Daily Energy Intake')
plt.scatter(weighted_approach[:, 1], weighted_approach[:, 0])
plt.plot(weighted_approach[:, 1], weighted_approach[:, 0])
plt.show()

for i in items:
        if x[i].x != 0:
            print("Food Item", i + 1, "is required in the diet in the quantity of", x[i].x)

## Question 3 ##

# goal programming #
min_cost = 0.5 #already given, no need to optimize cost first

m1.setObjective(z1, GRB.MINIMIZE)  #minimizing energy intake given cost constraint

# setting the upper bound for z2 i.e. daily cost cost to $0.5
z2.ub = min_cost 
m1.optimize()
    
# Printing Optimal Diet given minimal cost objective
for i in items:
        if x[i].x != 0:
            print("Food Item", i + 1, "is required in the diet in the quantity of", round(x[i].x, 2), "grams")
