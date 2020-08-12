"""
A simple printing module for LeCroy 3377 TDC data
"""

__author__="Igor Volobouev (i.volobouev@ttu.edu)"
__version__="0.1"
__date__ ="July 4 2020"

from AbsAnalysisModule import AbsAnalysisModule
from LC3377 import *

class LC3377PrintingModule(AbsAnalysisModule):
    def __init__(self):
        AbsAnalysisModule.__init__(self, "LC3377PrintingModule")

    def beginJob(self, allModuleNames):
        pass

    def endJob(self):
        pass

    def beginRun(self, runNumber, runInfo):
        runConfig = runInfo[(runNumber, "runConfiguration")]
        self.tdc_slots_3377 = runConfig["tdc_slots_3377"]

    def endRun(self, runNumber, runInfo):
        pass

    def processEvent(self, runNumber, eventNumber, eventRecord):
        # Dump the LeCroy 3377 TDC readouts
        for slot in self.tdc_slots_3377:
            fifoData = eventRecord[(slot,"LeCroy3377")]
            unpacked = LC3377Readout(fifoData)
            print("Event %d:" % eventNumber, unpacked)
