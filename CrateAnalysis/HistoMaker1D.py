"""
A module for plotting 1-d histograms of various numeric quantities
"""

__author__="Igor Volobouev (i.volobouev@ttu.edu)"
__version__="0.1"
__date__ ="June 23 2017"

import matplotlib.pyplot as plt
from AbsAnalysisModule import AbsAnalysisModule

class Histo1DSpec:
    def __init__(self, title, xlabel, nbins, calculator):
        self.title = title
        self.xlabel = xlabel
        self.nbins = nbins
        self.calculator = calculator

class HistoMaker1D(AbsAnalysisModule):
    """
    Module constructor arguments are:

    specs      A collection of Histo1DSpec objects
    """
    def __init__(self, specs, name):
        #AbsAnalysisModule.__init__(self, "HistoMaker1D")
        AbsAnalysisModule.__init__(self, name)
        self._specs = specs
        self._data = [list() for i in range(len(specs))]

    def beginJob(self, allModuleNames):
        pass

    def endJob(self):
        plt.ioff()
        for i, spec in enumerate(self._specs):
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.hist(self._data[i], spec.nbins)
            ax.grid(True)
            ax.set_xlabel(spec.xlabel)
            ax.set_ylabel("Events")
            ax.set_title(spec.title)
        plt.show()

    def beginRun(self, runNumber, runInfo):
        pass

    def endRun(self, runNumber, runInfo):
        pass

    def processEvent(self, runNumber, eventNumber, eventRecord):
        for i, spec in enumerate(self._specs):
            self._data[i].append(spec.calculator(eventRecord))
