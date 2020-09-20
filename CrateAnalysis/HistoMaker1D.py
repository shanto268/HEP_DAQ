"""
A module for plotting 1-d histograms of various numeric quantities
"""

__author__ = "Igor Volobouev (i.volobouev@ttu.edu)"
__version__ = "0.1"
__date__ = "June 23 2017"

import matplotlib.pyplot as plt
import numpy as np
from AbsAnalysisModule import AbsAnalysisModule
from statistics import NormalDist
import scipy.stats


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
    def __init__(self, specs, name, gaussian=False):
        #AbsAnalysisModule.__init__(self, "HistoMaker1D")
        AbsAnalysisModule.__init__(self, name)
        self._specs = specs
        self._data = [list() for i in range(len(specs))]
        self.otol = 10  #outlier tolerance multiple
        self.isGaussian = gaussian

    def beginJob(self, allModuleNames):
        pass

    def endJob(self):
        plt.ioff()
        for i, spec in enumerate(self._specs):
            fig = plt.figure()
            ax = fig.add_subplot(111)
            #print(self._data[i])
            self._data[i].sort()
            diff_last_two = self._data[i][-1] - self._data[i][-2]
            diff_compare = self._data[i][-2] - self._data[i][-3]
            diff_v = np.diff(self._data[i])
            ave_diff = sum(diff_v) / len(diff_v)
            # print("diff_last_two : {}".format(diff_last_two))
            # print("diff_compare : {}".format(diff_compare))
            # print("ave_diff : {}".format(ave_diff))
            self._data[i].pop()
            self._data[i].pop(0)
            if self.isGaussian:
                norm = NormalDist.from_samples(self._data[i])
                print(norm)
            plot = ax.hist(self._data[i], spec.nbins)
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
            # if (spec.calculator(eventRecord) != None
            # and spec.calculator(eventRecord) > 0):
            if (spec.calculator(eventRecord) != None):
                self._data[i].append(spec.calculator(eventRecord))


class HistoInfo1D(AbsAnalysisModule):
    """
    Module constructor arguments are:

    specs      A collection of Histo1DSpec objects
    """
    def __init__(self, specs, name):
        #AbsAnalysisModule.__init__(self, "HistoMaker1D")
        AbsAnalysisModule.__init__(self, name)
        self._specs = specs
        self.SIZE = len(specs)
        self._data = [list() for i in range(len(specs))]

    def beginJob(self, allModuleNames):
        pass

    def endJob(self):
        all_data = []
        all_titles = []
        for i, spec in enumerate(self._specs):
            all_data.append([self._data[i]])
            all_titles.append(spec.title)
        plt.hist(all_data[0], spec.nbins, alpha=0.5, label='Layer 1 Channel 0')
        plt.hist(all_data[1], spec.nbins, alpha=0.5, label='Layer 1 Channel 1')
        plt.xlabel("TDC Counts")
        plt.ylabel("Frequency")
        plt.title("TDC Values Layer 1")
        plt.legend(loc='upper right')
        plt.show()

        plt.hist(all_data[2], spec.nbins, alpha=0.5, label='Layer 2 Channel 0')
        plt.hist(all_data[3], spec.nbins, alpha=0.5, label='Layer 2 Channel 1')
        plt.xlabel("TDC Counts")
        plt.ylabel("Frequency")
        plt.title("TDC Values Layer 2")
        plt.legend(loc='upper right')
        plt.show()

    def beginRun(self, runNumber, runInfo):
        pass

    def endRun(self, runNumber, runInfo):
        pass

    def processEvent(self, runNumber, eventNumber, eventRecord):
        for i, spec in enumerate(self._specs):
            if (spec.calculator(eventRecord) != None
                    and spec.calculator(eventRecord) > 0):
                self._data[i].append(spec.calculator(eventRecord))
