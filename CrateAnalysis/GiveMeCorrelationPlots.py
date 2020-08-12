import numpy as np, matplotlib.pyplot as plt
from AbsAnalysisModule import AbsAnalysisModule


class GiveMeCorrelationPlots(AbsAnalysisModule):

    def __init__(self, name):
        AbsAnalysisModule.__init__(self, name)

    def beginJob(self, allModuleNames):
        pass

    def beginRun(self, runNumber, runInfo):
        runConfig = runInfo[(runNumber, "runConfiguration")]
        self.tdc_channels = runConfig["tdc_channels"]
        self.tdc_slots = runConfig["tdc_slots"]

    def processEvent(self, runNumber, eventNumber, eventRecord):
        pass

    def endRun(self, runNumber, runRecord):
        plt.plot(tdcValues[0],tdcValues[1])
        return True
        

    def endJob(self):
        pass

