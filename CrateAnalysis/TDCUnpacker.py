#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 08:51:39 2020

@author: nuralakchurin

report:
    - length of unpacked.events is not the number of TDC hits
"""

from LC3377 import *
from UtilityModules import DummyModule


class TDCUnpacker(DummyModule):
    # In the constructor, provide whatever arguments
    # you intend to play with
    def __init__(self, name):
        DummyModule.__init__(self, name)

    def beginRun(self, runNumber, runRecord):
        runConfiguration = runRecord[(runNumber, "runConfiguration")]
        self.tdc_slots = runConfiguration["tdc_slots_3377"]

    def processEvent(self, runNumber, eventNumber, eventRecord):
        tdcData = dict()
        tdcSData = dict()
        for slot in self.tdc_slots:
            fifoData = eventRecord[(slot, "LeCroy3377")]
            unpacked = LC3377Readout(fifoData)
            if len(unpacked.events[0].data) > 0:
                # print("{} {}".format(eventNumber,
                # len(unpacked.events[0].data)))
                tdc_vals = []
                for i in range(len(unpacked.events[0].data)):
                    # print(unpacked.events[0].data[i].tdc)
                    # print(unpacked.events[0].data[i].channel)
                    tdc_vals.append([
                        unpacked.events[0].data[i].channel,
                        unpacked.events[0].data[i].tdc
                    ])
                    tdcSData["TDC"] = tdc_vals
                    # print("{} {}".format(eventNumber, unpacked.events[0].data.tdc))
            if len(unpacked.events) > 0:
                lastevent = unpacked.events[-1]
                firstevent = unpacked.events[0]
                for datum in lastevent.data:
                    #for datum in firstevent.data:
                    tdcData[(slot, datum.channel)] = datum.tdc
        # eventRecord["unpacked3377Data"] = tdcData
        eventRecord["TDC"] = tdcSData
        # eventRecord["len_unpacked_3377Data"] = len(tdcData)
        # print("eventRecord : {}".format(eventRecord))

    def processEvent_NA(self, runNumber, eventNumber, eventRecord):
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
        # eventRecord["len_unpacked_3377Data"] = len(tdcData)
        # print("eventRecord : {}".format(eventRecord))

    #  print("eventNumber : {}".format(eventNumber))
