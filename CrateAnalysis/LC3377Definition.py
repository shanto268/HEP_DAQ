#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 16:19:52 2020

@author: nuralakchurin
"""
from LC3377 import *


class LC3377Definition:
    invalidtdc = -1

    def __init__(self, slot, channel):
        self.slot = slot
        self.channel = channel
        self.tdc_data = []

    def __call__(self, eventRecord):
        fifoData = eventRecord[(self.slot, "LeCroy3377")]
        unpacked = LC3377Readout(fifoData)
        # print(unpacked)

        nevent = len(unpacked.events)
        if nevent == 0:
            return LC3377Definition.invalidtdc
        lastevent = unpacked.events[-1]

        for datum in lastevent.data:
            if datum.channel == self.channel:
                self.tdc_data.append(datum.tdc)
                return datum.tdc
            #print(datum.channel, datum.tdc)
        return LC3377Definition.invalidtdc

    def getTDCData(self):
        return self.tdc_data
