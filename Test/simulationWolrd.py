# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

Ceci est un script temporaire.
"""

import networkx as nx
import random 
from math import sqrt
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import imageio
import seaborn
import forceatlas

themeColors = {"alive": "blue", "infected": "orange", "dead": "red", "recovered": "green"}
drawgif = 1;

class Person:
    idct = 1;
    def __init__(self, world):
        #When infected, first check if disease is already in diseases, if not, check resistances
        self.infections = {}
        self.id = Person.idct;
        Person.idct+=1;
        self.resistances = {}
        self.world = world;
        self.alive = 1;
        self.color = themeColors["alive"]
        self.recoveryRate = random.uniform(.9, .99)
        self.age = random.uniform(1,90)
        self.resistanceCoeff = random.uniform(.5, 1)*((self.age-40)**2)*(1/1600) #test d'ajout d'un coefficient de resistance en fonction de l'age
        self.resistance = .9 - self.resistanceCoeff
    def infect(self, disease, wasResistant):
        self.infections[disease.id] = Infection(self, disease,disease.pathogenicity, self.recoveryRate);
        disease.infected+=1;
        if wasResistant:
            disease.resistant-=1;
        else:
            disease.susceptible-=1;
        self.color = themeColors["infected"]
        return(self.infections[disease.id])
    def recover(self, infection):
        try:
            self.infections[infection.disease.id] = 0
            infection.disease.infected-=1;
            infection.disease.resistant+=1;
        except:
            print("Infection not on list. Is this vaccination?");
        self.color = themeColors["recovered"]
        self.resistances[infection.disease.id] = self.resistance
    def checkDisease(a, b):
        newInfections = []
        for diseaseid, infection in a.infections.items():
            if b.infections.get(diseaseid, 0)==0 and infection!=0:
                resistance = b.resistances.get(diseaseid, -1); #si la disease n'est pas dans les resistances,  on l'y ajoute avec une resistance de -1
#                if resistance!=-1: #la disease est dans la liste des resistances, la resistance est de 0.9
#                    test = random.uniform(0, 1)
#                    test2 = random.uniform(0, 1)
#                    if(test2>resistance) and (test<infection.disease.virulence): 
#                        b.infect(infection.disease, 1);
#                        newInfections.append(infection.disease.id)
                    #else:
                        #print("individual resisted infection!")
                #else: #la disease n'est pas dans la liste des resistances
                if resistance == -1:
                    test = random.uniform(0, 1)
                    if(test<infection.disease.virulence):
                        b.infect(infection.disease, 0);
                        newInfections.append(infection.disease.id)
        return newInfections
    def interact(self, otherActor):
        if(self.alive==1 and otherActor.alive==1):
            a = Person.checkDisease(self, otherActor);
            b = Person.checkDisease(otherActor, self);
            '''if(len(a)>0):
                print("Infections from A to B:", a)
            if(len(b)>0):
                print("Infections from B to A:", b)'''
    def die(self, disease):
        if(self.alive==1):
            self.alive = 0;
            disease.infected-=1;
            disease.dead+=1;
            self.color = themeColors["dead"]
    def tick(self, age):
        if(self.alive==1):
            for diseaseid, infection in self.infections.items():
                #print (self.infections)
                if(infection!=0):
                    infection.tick()
            if not bool(self.infections) and age > 1:#self.state == "susceptible" and age>1:
                test = random.uniform(0,1)
                thedisease = self.world.diseaseList[0]
                if test < thedisease.vaccinationRate : 
                    infection = self.infect(thedisease,False)
                    self.recover(infection)

class Infection:
    def __init__(self, host, disease, timeToDeath, recoveryRate):
        self.host = host;
        self.disease = disease;
        self.timeToDeath = timeToDeath;
        self.recoveryRate = recoveryRate;
        self.id = disease.id;
        self.recovered = 0;
    def tick(self):
        if not self.recovered:
            self.timeToDeath-=1;
            if self.timeToDeath<1 and self.disease.deadly == True :
                self.host.die(self.disease)
            else:
                test = random.uniform(0, 1)
                if(test>self.recoveryRate):
                    self.host.recover(self)
                    self.recovered = 1;
        
class Disease:
    idct = 1;
    def __init__(self, name, world, virulence, pathogenicity, deadly, vaccins, vaccinationRate):
        self.name = name;
        self.id = Disease.idct;
        Disease.idct+=1;
        self.virulence = virulence; #Determines how likely the pathogen is to spread from one host to the next
        self.pathogenicity = pathogenicity; #Determines how much disease the pathogen creates in the host (aka number of days w/o recovery until death)
        self.susceptible = world.popsize;
        self.infected = 0;
        self.resistant = 0;
        self.dead = 0;
        self.world = world;
        self.historyS = {};
        self.historyI = {};
        self.historyR = {};
        self.historyD = {};
        self.deadly = deadly;
        self.vaccins = vaccins;
        self.vaccinationRate = vaccinationRate;
        world.diseaseList.append(self);
    #These two functions are not currently in use. They don't fit into the current model
    '''def mutateVirulence(self, virulenceJitter = .05):
        self.virulence = self.virulence + random.uniform(-virulenceJitter, virulenceJitter)
    def mutatePathogenicity(self, pathoJitter = .1):
        self.pathogenicity = self.pathogenicity + random.uniform(-pathoJitter, pathoJitter)'''
    def tick(self, age):
        for vaccin in self.vaccins :
            if (vaccin[0] == age and vaccin[1] <= self.infected):
                print ('ok')
                nb = vaccin[1]
                vaccined = random.sample(range(1, self.infected), nb)
                print(len(vaccined))
                nb_eff_vaccined = 0
#                while nb_eff_vaccined < nb :
#                    print(nb)
                for person in self.world.population :
                    for diseaseid, infection in person.infections.items():
                        if(infection!=0):
                            lastInfection = person.infections.get(diseaseid)
                            lastInfection.recovered = 1;
                            person.recover(lastInfection);
                            print("individu vacciné")
                            nb_eff_vaccined += 1;
                    if nb_eff_vaccined > nb :
                        break;
                print (nb_eff_vaccined)
        
        self.historyS[age] = self.susceptible;
        self.historyI[age] = self.infected;
        self.historyR[age] = self.resistant;
        print (self.susceptible,self.infected,self.resistant,self.dead)
        if self.deadly == True :
            self.historyD[age] = self.dead;
    def summary(self):
        historyFrame = pd.DataFrame({"1-S": self.historyS, "2-I": self.historyI, "3-R": self.historyR, "4-D": self.historyD});
        historyFrame["time"] = historyFrame.index
        return historyFrame;

class World:
    def __init__(self, initPopulation):
        self.popsize = initPopulation;
        self.population = []
        self.diseaseList = [];
        self.age = 0;
        for indv in range(initPopulation):
            person = Person(self)
            self.population.append(person);
        self.worldgraph = nx.watts_strogatz_graph(initPopulation, 4,  .1); #small world graph
        mappin = {num: per for (num, per) in enumerate(self.population)}
        nx.relabel_nodes(self.worldgraph, mappin, copy=False)
        self.nodeLayout = nx.spring_layout(self.worldgraph, scale=200, k=1/(50*sqrt(self.popsize)))
        #self.nodeLayout = forceatlas.forceatlas2_layout(self.worldgraph, iterations=100,linlog=True)
        nx.set_node_attributes(self.worldgraph, 'color', themeColors["alive"])
    def draw(self):
        if(drawgif):
            nodeColors = [x.color for x in nx.nodes_iter(self.worldgraph)]
            plt.figure(figsize=(8,6))
            plt.title("Network at Age "+str(self.age))
            nx.draw(self.worldgraph, pos=self.nodeLayout, node_color=nodeColors, node_size=30, hold=1)
            plt.savefig("graphseries/graph"+str(self.age).zfill(4)+".png", dpi=250)
            plt.close()
    def tick(self):
        self.age+=1;
        if(self.age%4 == 0):
            print("Drawing network; Age is "+str(self.age))
            self.draw();
        interactions = random.sample(self.worldgraph.edges(), self.popsize)
        for edge in interactions:
            edge[0].interact(edge[1])
        for person in self.population:
            person.tick(self.age);
        for disease in self.diseaseList:
            disease.tick(self.age)
    def runSim(self, nsteps):
        for i in range(nsteps):
            self.tick();
    def summary(self):
        histories = {}
        for disease in self.diseaseList:
            histories[disease.name] = disease.summary();
        return histories;

def main():
    os.system("rm graphseries/*.png")
    earth = World(1000)
    earth.tick()
    flu = Disease("1918 Flu", earth, 0.3, 50, True, [], 0.2);
    earth.population[0].infect(flu, 0)
    earth.population[1].infect(flu, 0)
    earth.runSim(120)
    if(drawgif):
        png_dir = "graphseries"
        images = []
        for subdir, dirs, files in os.walk(png_dir):
            for file in files:
                file_path = os.path.join(subdir, file)
                if file_path.endswith(".png"):
                    images.append(imageio.imread(file_path))
        imageio.mimsave('graphseries/movie.gif', images, duration =0.3)
    return(earth)

earth = main()
history = earth.summary()
for name, x in history.items():
    y = pd.melt(x, id_vars="time")
    fg = seaborn.FacetGrid(data=y, hue='variable', hue_order=['1-S','2-I','3-R','4-D'], aspect=1.61)
    fg.map(plt.plot, 'time', 'value').add_legend()
    


