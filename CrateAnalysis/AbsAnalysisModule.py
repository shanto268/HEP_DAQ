"""
Class which defines the API for CAMAC analysis modules
"""

__author__ = "Igor Volobouev (i.volobouev@ttu.edu)"
__version__ = "0.1"
__date__ = "June 22 2017"


class AbsAnalysisModule:
    def __init__(self, name):
        """
        Constructor requires that you give this module a name.
        Module names must be unique.
        """
        self.moduleName = name
        self.title_string = ""

    def beginJob(self, allModuleNames):
        """
        Method called at the beginning of a job
        """
        raise NotImplementedError()

    def beginRun(self, runNumber, runRecord):
        """
        Method called at the beginning of run processing
        """
        raise NotImplementedError()

    def preProcessEvent(self, runNumber, eventNumber, eventRecord):
        """
        Method called for each event. Return "False" from this function
        to terminate event processing. Return "True" (or None) to invoke
        the next module in the sequence.
        """
        raise NotImplementedError()

    def filterRun(self, runNumber, runRecord):
        """
        Method called at the beginning of run processing
        """
        raise NotImplementedError()

    def processEvent(self, runNumber, eventNumber, eventRecord):
        """
        Method called for each event. Return "False" from this function
        to terminate event processing. Return "True" (or None) to invoke
        the next module in the sequence.
        """
        raise NotImplementedError()

    def endRun(self, runNumber, runRecord):
        """
        Method called at the end of run processing
        """
        raise NotImplementedError()

    def endJob(self):
        """
        Method called at the end of a job
        """
        raise NotImplementedError()
