# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 18:24:27 2018

@author: Peter
"""

#Elite TSP

import numpy as np
from random import shuffle
import csv

#use_stored = False
#
#if use_stored==True:
#    destinations = np.array(["Eta Carina Nebula",
#                             "Eta Carinae",
#                             "Trumpler Cluster",
#                             "The Spiderweb",
#                             "Statue of Liberty Nebula",
#                             "Ble Planetary Nebula",
#                             "NGC 3699",
#                             "Six Rings 'o Silver",
#                             "Vela Pulsar",
#                             "Spiral Planetary Nebula",
#                             "Phi Velorum",
#                             "Cubeo"])
#
#    locations = np.array([[8579.9688,-138.96875,2701.375],
#                          [7339.25,-84.625,2327.6875],
#                          [7824.1563,-100.3125,2481.96875],
#                          [7433.875,12.90625,2111.625],
#                          [5588.7188,-70.71875,2183.75],
#                          [4527.25,409.6875,2082.28125],
#                          [4150.3438,102.0625,1736.125],
#                          [1494.125,404.71875,1347.59375],
#                          [905.9375,-44.40625,-102.40625],
#                          [1415.3125,-105.59375,1075.28125],
#                          [1568.3125,1.96875,267.90625],
#                          [128.28125,-155.625,84.21875]])
#
#    order_best = np.array([11,8,10,6,4,1,2,0,3,5,7,9])
#
#else:
    
destinations_l = []
locations_xl = []
locations_yl = []
locations_zl = []

with open("DestinationList.csv") as csv_dest:
    reader = csv.reader(csv_dest)
    csv_dest.seek(0)
    for row in reader:
        destinations_l.append(str(row[0]))
        locations_xl.append(float(row[1]))
        locations_yl.append(float(row[2]))
        locations_zl.append(float(row[3]))

destinations = np.asarray(destinations_l)        
destination_count = len(destinations)

locations = np.zeros((destination_count,3))

for i in range(destination_count):
    locations[i,0] = locations_xl[i]
    locations[i,1] = locations_yl[i]
    locations[i,2] = locations_zl[i]

order_best = np.arange(destination_count,dtype=int)

kA = 100.0

start_type = "random"

def length_find(order_current):
    length = 0.0
    for i in range(destination_count):
        length += distances[order_current[i-1],order_current[i]]
    return length

def swap_random(order_current):
    order_new = np.zeros(destination_count,dtype=int)
    element_1 = np.random.randint(destination_count)
    element_2 = (element_1 + np.random.randint(1,destination_count))%destination_count
    if element_2 < element_1:
        element_1, element_2 = element_2, element_1
    if np.random.rand()<0.5:
        if (element_2-element_1==1)or(element_2-element_1==2):
            return order_current
        else:
            element_1 += 1
            element_2 -= 1
    else:
        if element_2-element_1==destination_count-1:
            return order_current
    for i in range(0,element_1):
        order_new[i] = order_current[i]
    for i in range(0,element_2-element_1+1):
        order_new[element_1+i] = order_current[element_2-i]
    for i in range(element_2+1,destination_count):
        order_new[i] = order_current[i]
    return order_new

def temperature_find(length_new,entropy_change):
    if (entropy_change == 0.0) or (length_new >= length_start):
        temperature_new = temperature_initial
    else:
        temperature_new = kA*(length_new-length_start)/(entropy_change)
    return temperature_new

def iterate(order_current,length_current,temperature_current,entropy_change):
    order_new = swap_random(order_current)
    length_new = length_find(order_new)
    length_change = length_new - length_current
    if length_change <= 0.0:
        temperature_new = temperature_find(length_new,entropy_change)
        return order_new,length_new,temperature_new,entropy_change
    else:
        probability = np.exp(-length_change/temperature_current)
        entropy_change -= length_change/temperature_current
        trial = np.random.rand()
        if trial < probability:
            temperature_new = temperature_find(length_new,entropy_change)
            return order_new,length_new,temperature_new,entropy_change
        else:
            temperature_new = temperature_find(length_current,entropy_change)
            return order_current,length_current,temperature_new,entropy_change

def sim_run(order_start,length_start,temperature_initial,its_max,temperature_min):
    order_current = np.zeros(destination_count,dtype=int)
    np.copyto(order_current,order_start)
    length_current = length_start
    temperature_current = temperature_initial
    entropy_change = 0.0
    done=False
    its=0

    while done==False:
        order_current,length_current,temperature_current,entropy_change = iterate(order_current,length_current,temperature_current,entropy_change)
        its+=1
        if its>=its_max:
            done=True
            print("max iterations reached")
        if temperature_current<temperature_min:
            done=True
            print("minimum temperature reached")
            
    return order_current,length_current

def order_print(order_current):
    for i in range(destination_count):
        print(str(order_current[i]) + ": " + destinations[order_current[i]])

destination_count = len(destinations)

distances = np.zeros((destination_count,destination_count))

for i in range(destination_count):
    for j in range(i+1,destination_count):
        distances[i,j] = np.linalg.norm(locations[i]-locations[j])
        distances[j,i] = distances[i,j]
 
if start_type=="order":
    order_start = np.arange(destination_count)
elif start_type=="random":
    order_start = np.arange(destination_count)
    shuffle(order_start)
elif start_type=="best":
    order_start = order_best
else:
    print("No vaild starting order given, defaulting to given order")
    order_start = np.arange(destination_count)

length_start = length_find(order_start)

test_runs = 100
test_average = 0.0

for i in range(test_runs):
    test_order = swap_random(order_start)
    test_average += abs(length_find(test_order)-length_start)/float(test_runs)

temperature_initial = -test_average/np.log(0.999)

sims=1
its_max = 1000000
temperature_min = pow(10.0,-100.0)

order_best = np.zeros(destination_count,dtype=int)
length_best = length_start
np.copyto(order_best,order_start)

for i in range(sims):
    order_current,length_current = sim_run(order_start,length_start,temperature_initial,its_max,temperature_min)
    if length_current<length_best:
        np.copyto(order_best,order_current)
        length_best = length_current
    print("Simulation " + str(i+1) + " complete, length was " + str(length_current)) 
    print("Current best length = " + str(length_best))

print("Final order:")
for i in range(len(locations)):
    print("{:4d} ".format(i+1) + destinations[order_best[i]])
