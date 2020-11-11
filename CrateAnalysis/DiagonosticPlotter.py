import matplotlib.pyplot as plt
import numpy as np

from UtilityModules import DummyModule
from collections import Counter

from HistoMaker1D import *
from HistoMaker2D import *


class DiagosticPlotter(DummyModule):
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

    def processEvent(self, runNumber, eventNumber, eventRecord):
        pass

    def endJob(self):
        h0 = Histo1DSpec("Dead Time", "Counts", 100, lambda x: x["deadtime"])
        h1 = Histo1DSpec("Number of hits per Event", "Counts", 10,
                         lambda x: x["len_unpacked_3377Data"])
        deadtime = HistoMaker1D((h0, ), "deadtime_")
        numHit = HistoMaker1D((h1, ), "NumHitsPerEvent_")
