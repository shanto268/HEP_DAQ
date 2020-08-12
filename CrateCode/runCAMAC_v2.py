"""                                                                             
A very simple CAMAC data acquisition sequence. For use as an example.
"""

__author__="Igor Volobouev (i.volobouev@ttu.edu)"
__version__="0.1"
__date__ ="June 22 2017"

from CAEN_C111C import CAEN_C111C
import importlib
import pickle
from datetime import datetime, timedelta


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


def clearModules(h, adc_slots):
    h.stdCMDSR("nim_resetcev 1")
    for slot in adc_slots:
        h.CFSA(9, slot, 0, 0)


def configureDAQDefaults(h):
    runConfiguration = dict()
    lam_slot = 17
    result = h.CFSA(26, lam_slot, 0, 0)
    print("Enabling LAM for slot %d: result is" % lam_slot, result)
    runConfiguration["lam_slot"] = lam_slot
    # runConfiguration["adc_slots"] = (16, 17, 18, 19)
    runConfiguration["adc_slots"] = (17,)
    runConfiguration["adc_channels"] = 12
    
    runConfiguration["tdc_slots"] = (10,)
    runConfiguration["tdc_channels"] = 8


    # Enable busy signal on the controller combo channel 1
    # h.stdCMDSR("nim_enablecombo 1 0")
    return runConfiguration


def runCAMAC(configModule, maxEvents, maxTimeSec,
             runNumber, outputFile, plotUpdater):
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
    timeDeltaLimit = timeDeltaLimit*1.0

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

    tdc_slots = runConfiguration["tdc_slots"]
    tdc_channels = runConfiguration["tdc_channels"]



    # Initialize various variables
    runStatus = "WaitForBusy"
    runError = ""
    eventCommitKey = (runNumber, "nEvents")

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
        clearModules(h, adc_slots)

        startTime = datetime.now()
        runStatus = "Success"
        runRecord[(runNumber, "startTime")] = startTime
        enableDataTaking(h, True)

        for eventNumber in range(numEventsLimit):
            # Wait for trigger (LAM)
            h.CCLWT(lam_slot)

            # Disable the data taking so that we don't get ADC hits
            # while we are reading the data out
            enableDataTaking(h, False)

            # Time stamp for this event
            timeStamp = datetime.now()

            # Start forming the event record
            eventRecord = dict()
            eventRecord["version"] = 1
            eventRecord["timeStamp"] = timeStamp

            # Read out all TDCs and ADCs
            for slot in tdc_slots:
                tdcValues = []
                for channel in range(tdc_channels):
                    result = h.CFSA(2, slot, channel, 0)
                    tdc = result.datum()
                    tdcValues.append(tdc)
                eventRecord[(slot,"LeCroy2228")] = tdcValues


            for slot in adc_slots:
                adcValues = []
                for channel in range(adc_channels):
                    result = h.CFSA(2, slot, channel, 0)
                    adc = result.datum()
                    adcValues.append(adc)
                eventRecord[(slot,"LeCroy2249")] = adcValues

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
    return runRecord[eventCommitKey], (stopTime - startTime).total_seconds()
