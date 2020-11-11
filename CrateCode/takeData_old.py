#!/usr/bin/env python3
"""
Usage: takeData.py configModule maxEvents maxTimeSec runNumber outputFile

Set "configModule" to "None" if the default DAQ configuration is acceptable.
Set "maxEvents" to 0 if the code should run until maxTimeSec seconds elapse.
Set "maxTimeSec" to 0 if the code should run until maxEvents events are taken.
Set "outputFile" to "None" if you just want to plot some events.
"""

import sys
from runCAMAC import runCAMAC
from ADCHisto import ADCHisto, TDCHisto
from MultipleUpdater import *

def main(argv):
    # Parse command line options
    argc = len(argv)
    if (argc == 0):
        # Convention used here: command invoked without any arguments
        # prints its usage instruction and exits successfully
        print(__doc__)
        return 0
    elif (argc == 5):
        # We have the correct number of arguments.
        # Check argument types.
        i = 0
        configModule = argv[i]; i+=1
        maxEvents = int(argv[i]); i+=1
        maxTimeSec = int(argv[i]); i+=1
        runNumber = int(argv[i]); i+=1
        outputFile = argv[i]; i+=1

        # Check argument validity
        ok = True
        if maxEvents < 0:
            print("Invalid number of events (can not be negative)")
            ok = False
        if maxTimeSec < 0:
            print("Invalid run time (can not be negative)")
            ok = False
        if not ok:
            print(__doc__)
            return 1
    else:
        # The number of arguments is incorrect
        print(__doc__)
        return 1

    # Configure the histogram plotter.
    # The channels to plot: a tuple of (slot, channel) pairs.
    # "None" will take all channels configured in the DAQ.
    channels_to_plot = None
    nBins = 100
    updateAfterHowManyEvents = 5
    verticalSpaceAdjustment = 0.4
    adcHisto = ADCHisto(nBins, updateAfterHowManyEvents,
                       verticalSpaceAdjustment, channels_to_plot)
    tdcHisto = TDCHisto(nBins, updateAfterHowManyEvents,
                        verticalSpaceAdjustment, channels_to_plot)
    plotUpdater = MultipleUpdater(adcHisto, tdcHisto)

    # To disable the histogram plotter, uncomment the line below
    plotUpdater = None

    # Call the code which actually does the job
    n, t, s, err = runCAMAC(configModule, maxEvents, maxTimeSec,
                            runNumber, outputFile, plotUpdater)

    # Print a mini summary of the run
    print('Processed %d events in %g sec' % (n, t))
    print('Run status is', s)
    if s == "Error":
        print('Error message:', err)
    if not (outputFile == "None" or outputFile == "none"):
        print('Run %d data is stored in the file "%s"' %
              (runNumber, outputFile))
    return 0

if __name__=='__main__':
    sys.exit(main(sys.argv[1:]))
