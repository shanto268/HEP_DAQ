class MultipleUpdater:
    def __init__(self, *args):
        self.modules = args

    def beginRun(self, runNumber, runRecord):
        for m in self.modules:
            m.beginRun(runNumber, runRecord)

    def processEvent(self, runNumber, eventNumber, eventRecord):
        for m in self.modules:
            m.processEvent(runNumber, eventNumber, eventRecord)

    def endRun(self, runNumber, runRecord):
        for m in self.modules:
            m.endRun(runNumber, runRecord)
