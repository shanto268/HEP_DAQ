import numpy as np, matplotlib.pyplot as plt
from AbsAnalysisModule import AbsAnalysisModule


class FilterOneModule(AbsAnalysisModule):

    def __init__(self, name):
        AbsAnalysisModule.__init__(self, name)

    def beginJob(self, allModuleNames):
        pass

    def beginRun(self, runNumber, runInfo):
        runConfig = runInfo[(runNumber, "runConfiguration")]
        self.tdc_channels = runConfig["tdc_channels"]
        self.tdc_slots = runConfig["tdc_slots"]

    def processEvent(self, runNumber, eventNumber, eventRecord):
        for slot in self.tdc_slots:
            tdcValues = eventRecord[(slot,"LeCroy2228")]
            if slot==10:
                if tdcValues[1]>2000 or tdcValues[0]>2000:
                    return False

        return True

    def endRun(self, runNumber, runRecord):
        pass

    def endJob(self):
        pass

