#!/usr/bin/env python3
"""
Usage: analysisExample.py outputPrefix inputFile0 ...
"""

import sys
import numpy as np, matplotlib.pyplot as plt
from runAnalysisSequence import runAnalysisSequence
from UtilityModules import *
from ADCPrintingModule import *
from TDCPrintingModule import *
from GenericPrintingModule import *
from HistoMaker1D import *
from HistoMaker2D import *
from ADCHisto import *
from datetime import datetime
from FilterOneModule import *
from GiveMeCorrelationPlots import *

def main(argv):
    # Parse command line options
    argc = len(argv)
    if (argc < 2):
        # Convention used here: command invoked without any arguments
        # prints its usage instruction and exits successfully
        print(__doc__)
        return 0

    outputPrefix = argv[0]
    inputFiles = argv[1:]
    

    # Example histogram specifier
    h0 = Histo1DSpec("Dead Time", "Counts", 100, lambda x: x["deadtime"])


    slot1 = 10
    channel1 = 0
    slot2 = 10
    channel2 = 1
    nbins = 400
    xdefinition = lambda eventRecord: eventRecord[(slot1,"LeCroy2228")][channel1]
    ydefinition = lambda eventRecord: eventRecord[(slot2,"LeCroy2228")][channel2]
    xlabel = "TDC counts for slot %s ch %s" % (slot1, channel1)
    ylabel = "TDC counts for slot %s ch %s" % (slot2, channel2)
    title = "Slot %s ch %s vs. slot %s ch %s" % (slot2, channel2, slot1, channel1)
    h2d = HistoMaker2D("h2d", title,
                       xlabel, nbins, 0.0, 2000.0, xdefinition,
                       ylabel, nbins, 0.0, 2000.0, ydefinition)



    # Create various analysis modules
    mod0 = VerboseModule("VerboseModule", True, True, 50, True, True)
    mod1 = EventCounter("Counter 0")
    mod2 = DutyCycleModue("DC0", 100)
    mod3 = ADCPrintingModule(outputPrefix + "_adc")
    mod4 = EventCounter("Counter 1")
    mod5 = TDCPrintingModule(outputPrefix + "_tdc")
    Filter1 = FilterOneModule("so_what")
    CorrPlots = GiveMeCorrelationPlots("talking_to_me")
    gptr = GenericPrintingModule(("hw_event_count",  "deadtime"))

    hMaker = HistoMaker1D((h0,))
    adcChannels = ((17,0),(17,1),(17,2),(17,3))
    tdcChannels = ((10,0),(10,1),(10,2),(10,3))
    adcPlotter = ADCHisto(400, 1000, 0.4, adcChannels)
    tdcPlotter = TDCHisto(400, 1000, 0.4, tdcChannels)

    # Define the sequence of modules
    # modules = (mod0, mod1, hMaker, plotUpdater, mod2, mod3, gptr, mod4)
    # modules = (mod0, mod1, mod3, mod5)
    modules = (mod0, mod1, Filter1, mod4, tdcPlotter, h2d)

    # Call the code which actually does the job
    t0 = datetime.now()
    n = runAnalysisSequence(modules, inputFiles)
    dt = datetime.now() - t0

    # Print a mini summary of event processing
    print('Processed %d events in %g sec' % (n, dt.total_seconds()))
    return 0

if __name__=='__main__':
    sys.exit(main(sys.argv[1:]))
