"""
Usage: analysisExample.py outputPrefix inputFile0 ...
Questions: how to look at data, data format and meaning
"""

import sys
from runAnalysisSequence import runAnalysisSequence
from UtilityModules import *
from ADCPrintingModule import *
from TDCPrintingModule import *
from GenericPrintingModule import *
from HistoMaker1D import *
from HistoMaker2D import *
from ADCHisto import *
from LC3377PrintingModule import *
from LC3377Definition import *
from TDCUnpacker import *
from TDCAnalyzer import *
from datetime import datetime

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

    # Create various analysis modules
    mod0 = VerboseModule("VerboseModule", True, True, 10, True, True)
    mod1 = EventCounter("Counter 0")
    mod2 = DutyCycleModue("DC0", 100)
    mod3 = ADCPrintingModule(outputPrefix + "_adc")
    mod4 = EventCounter("Counter 1")
    mod5 = TDCPrintingModule(outputPrefix + "_tdc")
    mod6 = LC3377PrintingModule()
    mod7 = TDCUnpacker("TDCUnpacker")
    mod8 = TDCAnalyzer("TDCAnalyzer")
    gptr = GenericPrintingModule(("hw_event_count", "deadtime"))

    hMaker = HistoMaker1D((h0,))

    adcPlotter = ADCHisto(100, 5, 0.4)
    tdcPlotter = TDCHisto(100, 5, 0.4)

    slot1 = 2
    channel1 = 0
    slot2 = 2
    channel2 = 1

    slot3 = 2
    channel3 = 3
    slot4 = 2
    channel4 = 4

    nbins = 200
    #xdefinition = lambda eventRecord: eventRecord[(slot1,"LeCroy3377")][channel1]
    #ydefinition = lambda eventRecord: eventRecord[(slot2,"LeCroy3377")][channel2]

    xdefinitionL1 = LC3377Definition(slot1, channel1)
    ydefinitionL1 = LC3377Definition(slot2, channel2)

    xdefinitionL2 = LC3377Definition(slot3, channel3)
    ydefinitionL2 = LC3377Definition(slot4, channel4)

    h1x = Histo1DSpec("Layer1x", "TDC Counts Layer 1x", 100, xdefinitionL1)
    h1y = Histo1DSpec("Layer1y", "TDC Counts Layer 1y", 100, ydefinitionL1)

    h2x = Histo1DSpec("Layer2x", "TDC Counts Layer 2x", 100, xdefinitionL2)
    h2y = Histo1DSpec("Layer2y", "TDC Counts Layer 2y", 100, ydefinitionL2)

    hMaker1x = HistoMaker1D((h1x,))
    hMaker1y = HistoMaker1D((h1y,))

    hMaker2x = HistoMaker1D((h2x,))
    hMaker2y = HistoMaker1D((h2y,))


    xlabelL1 = "TDC counts for slot %s ch %s" % (slot1, channel1)
    ylabelL1 = "TDC counts for slot %s ch %s" % (slot2, channel2)
    titleL1 = "Slot %s ch %s vs. slot %s ch %s" % (slot2, channel2, slot1, channel1)

    xlabelL2 = "TDC counts for slot %s ch %s" % (slot3, channel3)
    ylabelL2 = "TDC counts for slot %s ch %s" % (slot4, channel4)
    titleL2 = "Slot %s ch %s vs. slot %s ch %s" % (slot4, channel4, slot3, channel3)

    h2dL1 = HistoMaker2D("h2dL1", titleL1,
                       xlabelL1, nbins, 0.0, 200.0, xdefinitionL1,
                       ylabelL1, nbins, 0.0, 200.0, ydefinitionL1)

    h2dL2 = HistoMaker2D("h2dL2", titleL2,
                       xlabelL2, nbins, 0.0, 200.0, xdefinitionL2,
                       ylabelL2, nbins, 0.0, 200.0, ydefinitionL2)


    L1diff = lambda eventRecord: eventRecord["TDCAnalyzer"]["Layer1diff"]
    L2diff = lambda eventRecord: eventRecord["TDCAnalyzer"]["Layer2diff"]
    L1asym = lambda eventRecord: eventRecord["TDCAnalyzer"]["Layer1asym"]
    L2asym = lambda eventRecord: eventRecord["TDCAnalyzer"]["Layer2asym"]


    global hitMap, hitMap2, myLayer1diff, myLayer2asym

    histo_layer1diff = Histo1DSpec("Layer1", "TDC Counts Diff Layer 1", 200, L1diff)
    histo_layer2diff = Histo1DSpec("Layer2", "TDC Counts Diff Layer 2", 200, L2diff)
    histo_layer1asym = Histo1DSpec("Layer1", "Asymmetry Layer 1", 200, L1asym)
    histo_layer2asym = Histo1DSpec("Layer2", "Asymmetry Layer 2", 200, L2asym)

    myLayer1diff = HistoMaker1D((histo_layer1diff,))
    myLayer2diff = HistoMaker1D((histo_layer2diff,))
    myLayer1asym = HistoMaker1D((histo_layer1asym,))
    myLayer2asym = HistoMaker1D((histo_layer2asym,))
#
#

    hitMap = HistoMaker2D("hitMap", "Hit Map",
                       "Asymmetry in X", nbins, -100, 100.0, L1asym,
                       "Asymmetry in Y", nbins, -100, 100.0, L2asym)

    hitMap2 = HistoMaker2D("hitMap2", "Hit Map",
                       "Difference in X", nbins, -100, 100.0, L1diff,
                       "Difference in Y", nbins, -100, 100.0, L2diff)

    # Define the sequence of modules
    # modules = (mod0, mod1, hMaker, plotUpdater, mod2, mod3, gptr, mod4)
    # modules = (mod0, mod1, mod3, mod5)
    # modules = (mod0, mod1, mod6, h2d, tdcPlotter, adcPlotter)
    # modules = (mod0, mod1, mod7, mod8, h2dL1, h2dL2, myLayer2asym)
    
    modules = (mod0, mod1, mod7, mod8, hitMap)
    
    # Call the code which actually does the job
    t0 = datetime.now()
    n = runAnalysisSequence(modules, inputFiles)
    dt = datetime.now() - t0

    # Print a mini summary of event processing
    print('Processed %d events in %g sec' % (n, dt.total_seconds()))
    hitMap.redraw(0,15)
    return 0

if __name__=='__main__':
    sys.exit(main(sys.argv[1:]))

