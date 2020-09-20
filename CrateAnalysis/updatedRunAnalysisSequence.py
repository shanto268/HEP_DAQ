import sys
import pickle


def _eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def _callBeginJobSequence(moduleSequence):
    moduleNames = [mod.moduleName for mod in moduleSequence]
    if not len(set(moduleNames)) == len(moduleNames):
        print(moduleNames)
        raise ValueError("Module names are not unique")
    for mod in moduleSequence:
        mod.beginJob(moduleNames)


def _callEndJobSequence(moduleSequence):
    for mod in moduleSequence:
        mod.endJob()


def _callBeginRunSequence(moduleSequence, runNumber, runInfo):
    for mod in moduleSequence:
        mod.beginRun(runNumber, runInfo)


def _callEndRunSequence(moduleSequence, runNumber, runInfo):
    for mod in moduleSequence:
        mod.endRun(runNumber, runInfo)


def _updateRunRecord(moduleSequence, runNumber, runInfo):
    for mod in moduleSequence:
        try:
            if mod.updateRunRecord:
                return mod.runRecord
        except:
            pass


def _callEventSequence(moduleSequence, runNumber, evNumber, eventInfo):
    for mod in moduleSequence:
        status = mod.processEvent(runNumber, evNumber, eventInfo)
        if not status is None:
            if not status:
                break


def updatedRunAnalysisSequence(run_record,
                               moduleSequence,
                               inputFiles,
                               maxEventsToProcess=0,
                               nSkip=0):
    if nSkip < 0:
        raise ValueError("Number of events to skip can not be negative")
    eventCounter = 0
    eventsProcessed = 0
    if maxEventsToProcess > 0:
        maxEventNum = nSkip + maxEventsToProcess
    else:
        maxEventNum = 2**63 - 1

    _callBeginJobSequence(moduleSequence)
    for fname in inputFiles:
        try:
            f = open(fname, "rb")
        except:
            f = None

        if f is None:
            _eprint('Failed to open file "%s". '
                    'This input file name is ignored.' % fname)
            continue

        try:
            #        print(runRecord)
            #   print("")
            runRecord = run_record
            runRecordVersion = runRecord["version"]
        except:
            runRecord = pickle.load(f, fix_imports=False)
            runRecordVersion = runRecord["version"]
            # runRecord = None
            pass
        finally:
            f.close()

        if runRecord is None:
            _eprint('Failed to load run record from file "%s". '
                    'This input file is ignored.' % fname)
            continue

        if runRecordVersion != 1:
            _eprint('Can not handle record version %d in file "%s". '
                    'This input file is ignored.' % (runRecordVersion, fname))
            continue

        runNumber = runRecord["runNumber"]
        nEvents = runRecord[(runNumber, "nEvents")]
        beginRunCalled = False

        # Find the events which are actually present in this
        # run record. We assume that run records can be filtered.
        idlist = []
        for iev in range(nEvents):
            id = (runNumber, iev)
            if id in runRecord:
                idlist.append(id)
        for id in idlist:
            if eventCounter >= nSkip and eventCounter < maxEventNum:
                if not beginRunCalled:
                    _callBeginRunSequence(moduleSequence, runNumber, runRecord)
                    beginRunCalled = True
                eventInfo = runRecord[id]
                _callEventSequence(moduleSequence, id[0], id[1], eventInfo)
                eventsProcessed += 1
            eventCounter += 1
        if beginRunCalled:
            _callEndRunSequence(moduleSequence, runNumber, runRecord)
            updatedRunRecord = _updateRunRecord(moduleSequence, runNumber,
                                                runRecord)
        if eventCounter >= maxEventNum:
            break
    _callEndJobSequence(moduleSequence)

    return eventsProcessed
