#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 08:51:39 2020

@author: nuralakchurin
"""

from LC3377 import *
from UtilityModules import DummyModule

class MyCalculator(DummyModule):
    # In the constructor, provide whatever arguments
    # you intend to play with
    def __init__(self, name, slot, channel, tdc):
        DummyModule.__init__(self, name)
        self.slot = slot
        self.channel = channel
        self.tdc = tdc

    def processEvent(self, runNumber, eventNumber, eventRecord):
        fifoData = eventRecord[(self.slot,"LeCroy3377")]
        unpacked = LC3377Readout(fifoData)
        # Do some calculations here. You can save
        # your results in a dictionary or write a separate
        # class to hold them. Here, a dictionary is used.
        
 
        
        if self.channel == 0:
            tdc0 = self.tdc
        elif self.channel == 1:
            tdc1 = self.tdc
        elif self.channel == 3:
            tdc3 = self.tdc
        elif self.channel == 4:
            tdc4 = self.tdc
            
        print(tdc0,tdc1,tdc3,tdc4)
        Layer1diff = (tdc0-tdc1)
        Layer2diff = (tdc3-tdc4)
        

        
        myResults = dict()
        myResults["Layer1diff"] = Layer1diff
        myResults["Layer2diff"] = Layer2diff
        eventRecord["myResults"] = myResults

# Create an object of this class inside analysisExample.py
# and put it into the list of modules before histogramming.
# Then you should be able to do something like this:

# xdefinition = lambda eventRecord: eventRecord["myResults"]["Layer1diff"]

