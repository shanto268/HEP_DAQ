"""
@author: Sadman Ahmed Shanto
@date: 2020-10-02

purpose:
    create and update a dataFrame with all the per event information

2726 Key : version , Value : 2
2726 Key : timeStamp , Value : 2020-08-28 18:33:05.263949
2726 Key : (10, 'LeCroy2228') , Value : [1658 1153 3793 3793 3793 3793 3793 3793]
2726 Key : (2, 'LeCroy3377') , Value : [45058    97  1173  3193  4229]
2726 Key : (17, 'LeCroy2249') , Value : [ 1 33 34 35 31 22 28  7  8 18 18 24]
2726 Key : hw_event_count , Value : 2727
2726 Key : deadtime , Value : 1238
2726 Key : unpacked3377Data , Value : {(2, 0): 97, (2, 1): 149, (2, 3): 121, (2, 4): 133}
2726 Key : len_unpacked_3377Data , Value : 4
2726 Key : TDCAnalyzer , Value : {'Layer1diff': -52, 'Layer1asym': -21.13821138211382, 'Layer2diff': -12, 'Layer2asym': -4.724409448818897}

"""

from LC3377 import *
from UtilityModules import DummyModule
from DataFrame import DataFrame


class EventDataFrame(DummyModule):
    # In the constructor, provide whatever arguments
    # you intend to play with
    def __init__(self, name):
        DummyModule.__init__(self, name)
        self.df = object

    def beginRun(self, runNumber, runRecord):
        self.df = DataFrame(runNumber)

    def printSpecificData(self, item, eventNumber, eventRecord):
        print(eventNumber,
              "Key : {} , Value : {}".format(item, eventRecord[item]))

    def printRawDataOutput(self, eventNumber, eventRecord):
        for item in eventRecord:
            print(eventNumber,
                  "Key : {} , Value : {}".format(item, eventRecord[item]))

    def processEvent(self, runNumber, eventNumber, eventRecord):
        self.df.updateDataFrame(eventRecord, eventNumber)
        # print("Processing the DF....")
        # self.df.showDataFrame()

    def endRun(self, runNumber, runRecord):
        self.df.saveDataFrame()
