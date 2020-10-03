"""
__author__ = Sadman Ahmed Shanto
__date__ = 2020-09-19

## TODO:
    1) recreate TDCUnpacker and TDCAnalyzer logic
"""
from UtilityModules import DummyModule
import numpy as np


class NoiseCleaner(DummyModule):
    def __init__(self, name):
        DummyModule.__init__(self, name)
        self.updateRunRecord = True
        self.l1_TDC = []
        self.l2_TDC = []
        self.l1_mean = 0
        self.l2_mean = 0
        self.l1_std = 0
        self.l2_std = 0
        self.runRecord = {}

    def beginRun(self, runNumber, runRecord):
        # print("Initial Key Size: {}".format(len(runRecord.keys())))
        # runConfiguration = runRecord[(runNumber, "runConfiguration")]

        # self.tdc_slots = runConfiguration["tdc_slots_3377"]
        # for key in runRecord.keys():
        # if isinstance(key[1], int):
        # print(runRecord.get(key))  # .get("Layer_1").get("add_TDC"))
        # l1_TDC_val = runRecord.get(key).get("Layer_1").get("add_TDC")
        # l2_TDC_val = runRecord.get(key).get("Layer_2").get("add_TDC")
        # if l1_TDC_val is not None:
        # self.l1_TDC.append(l1_TDC_val)
        # if l2_TDC_val is not None:
        # self.l2_TDC.append(l2_TDC_val)

        # self.getAddedTDCValues(runNumber, runRecord)
        # self.computeStats()
        # self.filterRunRecord(runRecord)
        # print("Final Key Size: {}".format(len(runRecord.keys())))
        pass

    def TDCUnpackerLogic(self, runNumber, eventNumber, eventRecord):
        tdcData = dict()
        for slot in self.tdc_slots:
            fifoData = eventRecord[(slot, "LeCroy3377")]
            unpacked = LC3377Readout(fifoData)
            if len(unpacked.events) > 0:
                lastevent = unpacked.events[-1]
                firstevent = unpacked.events[0]
                for datum in lastevent.data:
                    #for datum in firstevent.data:
                    tdcData[(slot, datum.channel)] = datum.tdc
        eventRecord["unpacked3377Data"] = tdcData
        eventRecord["len_unpacked_3377Data"] = len(tdcData)

    def processEvent(self, runNumber, eventNumber, eventRecord):
        # layer_1_added_TDC = eventRecord["Layer_1"].get("add_TDC")
        # layer_2_added_TDC = eventRecord["Layer_2"].get("add_TDC")
        # print("layer_1_added_TDC : {}".format(layer_1_added_TDC))
        pass

    def endRun(self, runNumber, runRecord):
        print("Initial Key Size: {}".format(len(runRecord.keys())))
        self.getAddedTDCValues(runNumber, runRecord)
        self.computeStats()
        self.filterRunRecord(runRecord)
        print("Final Key Size: {}".format(len(runRecord.keys())))
        self.runRecord = runRecord

    def getAddedTDCValues(self, runNumber, runRecord):
        for key in runRecord.keys():
            if isinstance(key[1], int):
                l1_TDC_val = runRecord.get(key).get("Layer_1").get("add_TDC")
                l2_TDC_val = runRecord.get(key).get("Layer_2").get("add_TDC")
                if l1_TDC_val is not None:
                    self.l1_TDC.append(l1_TDC_val)
                if l2_TDC_val is not None:
                    self.l2_TDC.append(l2_TDC_val)

    def computeStats(self):
        self.l1_mean = sum(self.l1_TDC) / len(self.l1_TDC)
        self.l2_mean = sum(self.l2_TDC) / len(self.l2_TDC)
        self.l1_std = np.std(np.array(self.l1_TDC))
        self.l2_std = np.std(np.array(self.l2_TDC))
        print("self.l1_mean : {}".format(self.l1_mean))
        print("self.l2_mean : {}".format(self.l2_mean))
        print("self.l1_std : {}".format(self.l1_std))
        print("self.l2_std : {}".format(self.l2_std))

    def filterRunRecord(self, runRecord):
        ul_l1 = self.l1_mean + self.l1_std
        ul_l2 = self.l2_mean + self.l2_std
        ll_l1 = self.l1_mean - self.l1_std
        ll_l2 = self.l2_mean - self.l2_std
        for key in runRecord.copy().keys():
            if isinstance(key[1], int):
                l1_TDC_val = runRecord.get(key).get("Layer_1").get("add_TDC")
                l2_TDC_val = runRecord.get(key).get("Layer_2").get("add_TDC")
                # eliminating non 4/4 hits
                if runRecord.get(key).get("len_unpacked_3377Data") == 4:
                    # keeping events that satisfy cut 1 and cut 2
                    if l1_TDC_val is not None:
                        if (l1_TDC_val < ll_l1) or (l1_TDC_val > ul_l1):
                            runRecord.pop(key)
                    if l2_TDC_val is not None:
                        if (l2_TDC_val < ll_l2) or (l2_TDC_val > ul_l2):
                            try:
                                runRecord.pop(key)
                            except:
                                pass
                else:
                    runRecord.pop(key)
