"""
A generic event content printing module for the CAMAC data analysis framework
"""

__author__="Igor Volobouev (i.volobouev@ttu.edu)"
__version__="0.1"
__date__ ="June 23 2017"

from AbsAnalysisModule import AbsAnalysisModule

class GenericPrintingModule(AbsAnalysisModule):
    """
    Module constructor arguments are:

    keys       The list of keys in the event record for which corresponding
               values should be printed
    """
    def __init__(self, keys):
        AbsAnalysisModule.__init__(self, "GenericPrintingModule")
        self._keys = keys

    def beginJob(self, allModuleNames):
        pass

    def endJob(self):
        pass

    def beginRun(self, runNumber, runInfo):
        pass

    def endRun(self, runNumber, runInfo):
        pass

    def processEvent(self, runNumber, eventNumber, eventRecord):
        print("Run %d event %d" % (runNumber, eventNumber))
        for k in self._keys:
            if k in eventRecord:
                print("%s is" % k, eventRecord[k])
        print()
