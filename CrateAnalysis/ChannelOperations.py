"""
@author: Sadman Ahmed Shanto
@date: 2020-09-18
"""

from LC3377 import *
from UtilityModules import DummyModule


class ChannelOperations(DummyModule):
    # In the constructor, provide whatever arguments
    # you intend to play with
    def __init__(self, name):
        DummyModule.__init__(self, name)

    def beginRun(self, runNumber, runRecord):
        runConfiguration = runRecord[(runNumber, "runConfiguration")]
        self.tdc_slots = runConfiguration["tdc_slots_3377"]

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
        tdcData = eventRecord["unpacked3377Data"]
        lenTDCData = eventRecord["len_unpacked_3377Data"]
        # print(tdcData)
        # for i in
        # print(50 * "=")
        channelOp1 = dict()  #keys: (layer_num, add_TDC, sub_TDC)
        channelOp2 = dict()  #keys: (layer_num, add_TDC, sub_TDC)

        if (2, 0) in tdcData and (2, 1) in tdcData and lenTDCData >= 2:
            layer_num = 1
            add_TDC = tdcData[(2, 0)] + tdcData[(2, 1)]
            sub_TDC = tdcData[(2, 0)] - tdcData[(2, 1)]
            channelOp1.update({"add_TDC": add_TDC})
            channelOp1.update({"sub_TDC": sub_TDC})

        if (2, 3) in tdcData and (2, 4) in tdcData and lenTDCData >= 2:
            layer_num = 2
            add_TDC = tdcData[(2, 3)] + tdcData[(2, 4)]
            sub_TDC = tdcData[(2, 3)] - tdcData[(2, 4)]
            channelOp2.update({"add_TDC": add_TDC})
            channelOp2.update({"sub_TDC": sub_TDC})

        eventRecord["Layer_1"] = channelOp1
        eventRecord["Layer_2"] = channelOp2
        # self.printRawDataOutput(eventNumber, eventRecord)
        # self.printSpecificData('TDCAnalyzer', eventNumber, eventRecord)
