"""
A very simple CAMAC data acquisition sequence. For use as an example.
"""

__author__ = "Igor Volobouev (i.volobouev@ttu.edu)"
__version__ = "0.2"
__date__ = "July 3 2020"

from CAEN_C111C import CAEN_C111C
import importlib
import pickle
import sys
from datetime import datetime, timedelta
import time
from LC3377 import *

# def enableDataTaking(h, enable):
#    h.NOSOS(1, not enable)


def enableDataTaking(h, enable):
    if enable:
        h.stdCMDSR("nim_cack 1")
    else:
        # In this mode, data taking is disabled by hardware busy signal
        pass


# def enableDataTaking(h, enable):
#     pass


def waitForBusy(h):
    while not int(h.stdCMDSR("nim_testcombo 1")):
        pass


def clearModules(h, adc_slots, tdc_slots_3377, scaler_slots_2552):
    h.stdCMDSR("nim_resetcev 1")
    for slot in adc_slots:
        h.CFSA(9, slot, 0, 0)
    for slot in tdc_slots_3377:
        h.CSSA(9, slot, 0, 0)
    for slot in scaler_slots_2552:
        h.CFSA(9, slot, 0, 0)


def initLeCroy3377(h, slot, moduleId=None):
    if moduleId is None:
        moduleId = slot
    assert 0 <= moduleId < 256

    # Fill control registers
    h.CSSA(17, slot, 0, int('1000', 16) + moduleId)
    h.CSSA(17, slot, 1, int('0000', 16))
    h.CSSA(17, slot, 2, int('03F0', 16))
    h.CSSA(17, slot, 3, int('0000', 16))

    # Disable LAM
    h.CSSA(24, slot, 0, 0)

    # Enable Acquisition mode
    h.CSSA(26, slot, 1, 0)


def printLeCroy3377Hex(slot, data):
    sys.stdout.write("Slot %d FIFO contents are" % slot)
    for u in data:
        sys.stdout.write(" %s" % hex(u))
    sys.stdout.write('\n')


def configureDAQDefaults(h):
    runConfiguration = dict()
    lam_slot = 17
    result = h.CFSA(26, lam_slot, 0, 0)
    print("Enabling LAM for slot %d: result is" % lam_slot, result)
    runConfiguration["lam_slot"] = lam_slot
    runConfiguration["adc_slots"] = (17, )
    runConfiguration["adc_channels"] = 12
    runConfiguration["tdc_slots_2228"] = (10, )
    runConfiguration["tdc_channels_2228"] = 8
    runConfiguration["tdc_slots_3377"] = (2, )
    runConfiguration["tdc_channels_3377"] = 32
    runConfiguration["scaler_slots_2552"] = (5, )  # new
    runConfiguration["scaler_channels"] = 12  # new

    # Enable busy signal on the controller combo channel 1
    h.stdCMDSR("nim_enablecombo 1 0")
    return runConfiguration


def runCAMAC(configModule, maxEvents, maxTimeSec, runNumber, outputFile,
             plotUpdater):
    """
    This function runs a simple data acquisition sequence. The arguments are:

    configModule        A user-defined DAQ configuration module that will
                        be applied in addition to the default configuration.
                        Should normally reside in the "Configs" sudirectory.
                        Can be None in case additional configuration is not
                        needed. The module should define the "configureDAQ"
                        function which takes the CAMAC controller handle
                        as its argument. This function should return
                        a dictionary of configuration parameters and their
                        values.

    maxEvents           Maximum number of events for the run. Set to 0
                        for unlimited.

    maxTimeSec          Maximum run duration in seconds. Set to 0 for
                        unlimited.

    runNumber           The run number.

    outputFile          The name of file into which collected data will be
                        written. Specify as None if the data should be
                        discarded.

    plotUpdater         An arbitrary object with methods "beginRun",
                        "processEvent", and "endRun" (read the code to
                        see the method arguments). Can be None if it is
                        not necessary to call such an object.
    """
    # Set "numEventsLimit" and "timeDeltaLimit" to something
    # large if they are specified as zeros
    numEventsLimit = maxEvents
    if numEventsLimit <= 0:
        numEventsLimit = 2**63 - 1
    timeDeltaLimit = maxTimeSec
    if timeDeltaLimit <= 0:
        timeDeltaLimit = 2**32 - 1
    timeDeltaLimit = timeDeltaLimit * 1.0

    # Import "configModule" if requested.
    if configModule == "None" or configModule == "none":
        configMod = None
        configModule = "None"
    else:
        configMod = importlib.import_module(configModule)

    # Open the connection to the crate controller
    # print("Connecting")
    h = CAEN_C111C()

    # Initialize and clear the crate
    # print("Initializing")
    h.CCCZ()
    # print("Clearing")
    enableDataTaking(h, False)
    h.CCCC()

    # Configure the DAQ
    # print("Configuring the DAQ")
    runConfiguration = configureDAQDefaults(h)

    # Extra DAQ configuration
    if not (configMod is None):
        moreConfigs = configMod.configureDAQ(h)
        runConfiguration.update(moreConfigs)

    # Extract run configuration parameters needed for data taking
    lam_slot = runConfiguration["lam_slot"]
    adc_slots = runConfiguration["adc_slots"]
    adc_channels = runConfiguration["adc_channels"]
    tdc_slots_2228 = runConfiguration["tdc_slots_2228"]
    tdc_channels_2228 = runConfiguration["tdc_channels_2228"]
    tdc_slots_3377 = runConfiguration["tdc_slots_3377"]
    tdc_channels_3377 = runConfiguration["tdc_channels_3377"]
    scaler_slots_2552 = runConfiguration["scaler_slots_2552"]  # new
    scaler_channels = runConfiguration["scaler_channels"]  # new
    fiber_test_slot = runConfiguration["fiber_test_slot"]  # new

    # Initialize various variables
    runStatus = "WaitForBusy"
    runError = ""
    eventCommitKey = (runNumber, "nEvents")
    tdc_nodata = [-1, -1, -1, -1, -1, -1, -1, -1]

    runRecord = dict()
    runRecord["version"] = 1
    runRecord["runNumber"] = runNumber
    runRecord[(runNumber, "configModule")] = configModule
    runRecord[(runNumber, "runConfiguration")] = runConfiguration
    runRecord[(runNumber, "runStatus")] = "In Progress"
    runRecord[eventCommitKey] = 0

    # Call the "beginRun" method of the plotter (or whatever that
    # class is actually doing)
    if not (plotUpdater is None):
        plotUpdater.beginRun(runNumber, runRecord)

    # Make sure we can open the output file
    pickleFile = None
    if not (outputFile == "None" or outputFile == "none"):
        pickleFile = open(outputFile, "wb")

    # Start collecting the data
    # print("Start collecting data")
    try:
        # Need to define startTime here in case we Ctrl-C during "waitForBusy"
        startTime = datetime.now()

        # waitForBusy(h)
        clearModules(h, adc_slots, tdc_slots_3377, scaler_slots_2552)
        for slot in tdc_slots_3377:
            initLeCroy3377(h, slot)

        startTime = datetime.now()
        runStatus = "Success"
        runRecord[(runNumber, "startTime")] = startTime
        enableDataTaking(h, True)

        for eventNumber in range(numEventsLimit):
            # Wait for trigger (LAM)
            h.CCLWT(lam_slot)
            if (eventNumber == 1):
                start_time = time.time()

            if (eventNumber == 100):
                end_time = (time.time() - start_time)
                wtime = round(((end_time / 100) * maxEvents) / 60)
                print("Process will take roughly {} mins".format(wtime))

            if (eventNumber % (0.1 * numEventsLimit) == 0):
                print("{} events have been recorded.".format(eventNumber))

            # Disable the data taking so that we don't get ADC hits
            # while we are reading the data out
            enableDataTaking(h, False)

            # Time stamp for this event
            timeStamp = datetime.now()

            # Start forming the event record
            eventRecord = dict()
            eventRecord["version"] = 2
            eventRecord["timeStamp"] = timeStamp

            # Read out all Scaler values
            for slot in scaler_slots_2552:
                scalerValues = h.read24Scan(2, slot, 0, scaler_channels)
                eventRecord[(slot, "LeCroy2552")] = scalerValues

            # Read out all LeCroy2228A TDCs
            for slot in tdc_slots_2228:
                tdcValues = h.read24Scan(2, slot, 0, tdc_channels_2228)
                eventRecord[(slot, "LeCroy2228")] = tdcValues

            # Read out all LeCroy3377 TDCs
            for slot in tdc_slots_3377:
                fifoData = h.read16UntilQ0Q0(0, slot, 0)
                eventRecord[(slot, "LeCroy3377")] = fifoData
                # printLeCroy3377Hex(slot, fifoData)
                # print("LeCroy3377 slot %d: %s" %
                #      (slot, LC3377Readout(fifoData)))

            # Read out all ADCs
            for slot in adc_slots:
                adcValues = h.read24Scan(2, slot, 0, adc_channels)
                eventRecord[(slot, "LeCroy2249")] = adcValues

            eventRecord["hw_event_count"] = int(h.CMDSR("nim_getcev 1"))
            eventRecord["deadtime"] = int(h.stdCMDSR("nim_getcdtc 1"))

            # Enable data taking again after reading back all data
            enableDataTaking(h, True)

            # Include the event record into the run record
            runRecord[(runNumber, eventNumber)] = eventRecord
            runRecord[eventCommitKey] = eventNumber + 1

            # Run the plot updater
            if not (plotUpdater is None):
                plotUpdater.processEvent(runNumber, eventNumber, eventRecord)

            # Stop if we are exceeding the requested run time
            if (timeStamp - startTime).total_seconds() >= timeDeltaLimit:
                break

    except RuntimeError as e:
        runStatus = "Error"
        runError = str(e)

    except KeyboardInterrupt:
        if not runStatus == "WaitForBusy":
            runStatus = "SIGINT"

    finally:
        stopTime = datetime.now()
        runRecord[(runNumber, "runStatus")] = runStatus
        runRecord[(runNumber, "runError")] = runError
        runRecord[(runNumber, "stopTime")] = stopTime

        # Write out the run data
        if not (pickleFile is None):
            pickle.dump(runRecord, pickleFile, fix_imports=False)
            pickleFile.close()

    # Disable the trigger veto by the "busy" signal
    h.stdCMDSR("nim_enablecombo 1 1")

    # Call "endRun" for the plot updater
    if not (plotUpdater is None):
        plotUpdater.endRun(runNumber, runRecord)
    # Return the number of events collected and the elapsed time
    return runRecord[eventCommitKey], (
        stopTime - startTime).total_seconds(), runStatus, runError
