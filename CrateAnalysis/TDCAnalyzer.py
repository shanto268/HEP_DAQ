#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 12:18:43 2020

@author: nuralakchurin
"""

import matplotlib.pyplot as plt
import numpy as np

from UtilityModules import DummyModule


class TDCAnalyzer(DummyModule):
    # In the constructor, provide whatever arguments
    # you intend to play with
    def __init__(self, name):
        DummyModule.__init__(self, name)

    def printSpecificData(self, item, eventNumber, eventRecord):
        print(eventNumber,
              "Key : {} , Value : {}".format(item, eventRecord[item]))
        #print(eventNumber,"Value : {}, Len: {}".format(eventRecord.get(item), len(eventRecord.get(item))))

    def printRawDataOutput(self, eventNumber, eventRecord):
        for item in eventRecord:
            #print(item)
            print(eventNumber,
                  "Key : {} , Value : {}".format(item, eventRecord[item]))

    def processEvent_NA(self, runNumber, eventNumber, eventRecord):
        tdcData = eventRecord["unpacked3377Data"]
        tdcCalc = dict()

        if (2, 0) in tdcData and (2, 1) in tdcData:
            L1d = tdcData[(2, 0)] - tdcData[(2, 1)]
            L1a = 100 * (tdcData[(2, 0)] -
                         tdcData[(2, 1)]) / (tdcData[(2, 0)] + tdcData[(2, 1)])
            tdcCalc.update({"Layer1diff": L1d})
            tdcCalc.update({"Layer1asym": L1a})

        if (2, 3) in tdcData and (2, 4) in tdcData:
            L2d = tdcData[(2, 3)] - tdcData[(2, 4)]
            L2a = 100 * (tdcData[(2, 3)] -
                         tdcData[(2, 4)]) / (tdcData[(2, 3)] + tdcData[(2, 4)])
            tdcCalc.update({"Layer2diff": L2d})
            tdcCalc.update({"Layer2asym": L2a})

        if (2, 0) not in tdcData or (2, 1) not in tdcData:
            tdcCalc.update({"Layer1diff": 0})
            tdcCalc.update({"Layer1asym": 0})

        if (2, 3) not in tdcData or (2, 4) not in tdcData:
            tdcCalc.update({"Layer2diff": 0})
            tdcCalc.update({"Layer2asym": 0})

        eventRecord["TDCAnalyzer"] = tdcCalc

    def processEvent(self, runNumber, eventNumber, eventRecord):
        tdcData = eventRecord["unpacked3377Data"]
        lenTDCData = eventRecord["len_unpacked_3377Data"]
        #        print(tdcData)
        #        print(40 * "=")
        tdcCalc = dict()

        if (2, 0) in tdcData and (2, 1) in tdcData and lenTDCData >= 2:
            L1d = tdcData[(2, 0)] - tdcData[(2, 1)]
            L1a = 100 * (tdcData[(2, 0)] -
                         tdcData[(2, 1)]) / (tdcData[(2, 0)] + tdcData[(2, 1)])
            tdcCalc.update({"Layer1diff": L1d})
            tdcCalc.update({"Layer1asym": L1a})

        if (2, 3) in tdcData and (2, 4) in tdcData and lenTDCData >= 2:
            L2d = tdcData[(2, 3)] - tdcData[(2, 4)]
            L2a = 100 * (tdcData[(2, 3)] -
                         tdcData[(2, 4)]) / (tdcData[(2, 3)] + tdcData[(2, 4)])
            tdcCalc.update({"Layer2diff": L2d})
            tdcCalc.update({"Layer2asym": L2a})

        eventRecord["TDCAnalyzer"] = tdcCalc
        # self.printRawDataOutput(eventNumber, eventRecord)
        # self.printSpecificData('TDC', eventNumber, eventRecord)

    def processEvent_SAS(self, runNumber, eventNumber, eventRecord):
        tdcData = eventRecord["unpacked3377Data"]
        lenTDCData = eventRecord["len_unpacked_3377Data"]
        tdcCalc = dict()

        if (2, 1) in tdcData and (2, 2) in tdcData and lenTDCData >= 2:
            L1d = tdcData[(2, 1)] - tdcData[(2, 2)]
            L1a = 100 * (tdcData[(2, 1)] -
                         tdcData[(2, 2)]) / (tdcData[(2, 1)] + tdcData[(2, 2)])
            tdcCalc.update({"Layer1diff": L1d})
            tdcCalc.update({"Layer1asym": L1a})

        if (2, 3) in tdcData and (2, 4) in tdcData and lenTDCData >= 2:
            L2d = tdcData[(2, 3)] - tdcData[(2, 4)]
            L2a = 100 * (tdcData[(2, 3)] -
                         tdcData[(2, 4)]) / (tdcData[(2, 3)] + tdcData[(2, 4)])
            tdcCalc.update({"Layer2diff": L2d})
            tdcCalc.update({"Layer2asym": L2a})

        eventRecord["TDCAnalyzer"] = tdcCalc


#        self.printRawDataOutput(eventNumber, eventRecord)
#        self.printSpecificData('TDCAnalyzer', eventNumber, eventRecord)
