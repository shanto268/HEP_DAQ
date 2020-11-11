"""
A few simple analysis modules derived from AbsAnalysisModule
"""

__author__ = "Igor Volobouev (i.volobouev@ttu.edu)"
__version__ = "0.1"
__date__ = "June 22 2017"

from AbsAnalysisModule import AbsAnalysisModule


class DummyModule(AbsAnalysisModule):
    """
    This class does nothing useful. It only illustrates which methods
    must be implemented in an analysis module. You can also derive your
    own module from it if you prefer to have your methods not to throw
    "NotImplementedError" by default.
    """
    def __init__(self, name, updateRunRecord=False):
        AbsAnalysisModule.__init__(self, name)
        self.updateRunRecord = updateRunRecord

    def beginJob(self, allModuleNames):
        pass

    def beginRun(self, runNumber, runRecord):
        pass

    def preProcessEvent(self, runNumber, eventNumber, eventRecord):
        pass

    def filterRun(self, runNumber, runRecord):
        pass

    def processEvent(self, runNumber, eventNumber, eventRecord):
        pass

    def endRun(self, runNumber, runRecord):
        pass

    def endJob(self):
        pass


class VerboseModule(AbsAnalysisModule):
    """
    This module prints messages to the standard output when its methods
    are called. This is useful for debugging module sequences. The
    constructor arguments (in addition to the module name) are as follows:

      cry_bj     -- If True, print a message when "beginJob" is called.

      cry_br     -- If True, print a message when "beginRun" is called.

      cry_ev_cnt -- This argument defines how many times to print a message
                    (per run) when "processEvent" method is called.

      cry_er     -- If True, print a message when "endRun" is called.

      cry_ej     -- If True, print a message when "endJob" is called.
    """
    def __init__(self, name, cry_bj, cry_br, cry_ev_cnt, cry_er, cry_ej):
        AbsAnalysisModule.__init__(self, name)
        self.cryBeginJob = cry_bj
        self.cryBeginRun = cry_br
        self.cryEventCount = cry_ev_cnt
        self.cryEndRun = cry_er
        self.cryEndJob = cry_ej

    def _condPrint(self, cond, message):
        if cond:
            print("%s:" % self.moduleName, message)

    def beginJob(self, allModuleNames):
        self._condPrint(self.cryBeginJob, "beginJob called")

    def beginRun(self, runNumber, runRecord):
        self._condPrint(self.cryBeginRun, "beginRun called for run %d" \
                        % runNumber)
        self._eventsProcessed = 0

    def processEvent(self, runNumber, eventNumber, eventRecord):
        self._condPrint(self._eventsProcessed < self.cryEventCount,
                        "processEvent called for event %d" \
                        % eventNumber)
        self._eventsProcessed += 1

    def endRun(self, runNumber, runRecord):
        self._condPrint(self.cryEndRun, "endRun called for run %d" \
                        % runNumber)

    def endJob(self):
        self._condPrint(self.cryEndJob, "endJob called")


class EventCounter(DummyModule):
    """
    A simple event counter. Prints its count to the standard output
    at the end of a job.
    """
    def __init__(self, name):
        AbsAnalysisModule.__init__(self, name)
        self.counter = 0

    def processEvent(self, runNumber, eventNumber, eventInfo):
        self.counter += 1

    def endJob(self):
        print("%s:" % self.moduleName, self.counter)


class DutyCycleModue(EventCounter):
    """
    This module passes only a certain fraction of the events down the event
    processing chain. The constructor arguments are as follows:

    dutyCycle -- The "duty cycle". If, let say, set to 10, every 10th
                 event will be passed down the chain.

    phase     -- Determines the "phase shift" of the cycle. If, let say,
                 this parameter is set to 3 when the duty cycle is 10,
                 events 3, 13, 23, 33, ..., will be passed down the chain.
    """
    def __init__(self, name, dutyCycle, phase=0):
        EventCounter.__init__(self, name)
        self.dutyCycle = int(dutyCycle)
        self.phase = int(phase)

    def processEvent(self, runNumber, eventNumber, eventInfo):
        continueProcessing = True
        if self.dutyCycle > 0:
            if (self.counter - self.phase) % self.dutyCycle:
                continueProcessing = False
        EventCounter.processEvent(self, runNumber, eventNumber, eventInfo)
        return continueProcessing

    def endJob(self):
        pass
