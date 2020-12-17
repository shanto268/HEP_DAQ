"""
Usage: analysisExample.py outputPrefix inputFile0 ...
"""

import sys
from ChannelOperations import *
from runAnalysisSequence import runAnalysisSequence
from updatedRunAnalysisSequence import updatedRunAnalysisSequence
from UtilityModules import *
from ADCPrintingModule import *
from TDCPrintingModule import *
from GenericPrintingModule import *
from HistoMaker1D import *
from HistoMaker2D import *
from ADCHisto import *
from LC3377PrintingModule import *
from LC3377Definition import *
from TDCUnpackerRun import *
from TDCAnalyzerRun import *
from NoiseCleaner import *
from datetime import datetime
from EventDataFrame import *
from PostRunDataFrame import *
from MissingTDCCounter import *


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

    # Create various analysis modules
    mod0 = VerboseModule("VerboseModule", True, True, 10, True, True)
    mod1 = EventCounter("Counter 0")
    mod2 = DutyCycleModue("DC0", 100)
    mod3 = ADCPrintingModule(outputPrefix + "_adc")
    mod4 = EventCounter("Counter 1")
    mod5 = TDCPrintingModule(outputPrefix + "_tdc")
    mod6 = LC3377PrintingModule()
    mod7 = TDCUnpackerRun("TDCUnpacker")
    mod8 = TDCAnalyzerRun("TDCAnalyzer")
    # mod9 = ChannelOperations("ChannelOperations")
    # mod10 = NoiseCleaner("NoiseCleaner")
    # mod11 = EventDataFrame("EventDataFrame")
    mod12 = MissingTDCCounter("MissingTDCCounter")
    gptr = GenericPrintingModule(("hw_event_count", "deadtime"))
    """
    PLOTTING METHODS - START
    """
    h0 = Histo1DSpec("Dead Time", "Counts", 100, lambda x: x["deadtime"])
    h1 = Histo1DSpec("Number of hits per Event", "Counts", 10,
                     lambda x: x["len_unpacked_3377Data"])
    deadtime = HistoMaker1D((h0, ), "deadtime_")
    numHit = HistoMaker1D((h1, ), "NumHitsPerEvent_")
    tdc_comp, tdc_sep = getTDC(nbins=250)
    """
    PLOTTING METHODS - END
    """

    plots = (deadtime, numHit, tdc_comp, tdc_sep)
    modules = (mod1, mod7, mod8, mod12) + plots

    # processWithCuts(modules1, modules2, inputFiles)
    processDefault(modules, inputFiles)
    return 0


def getTDC(nbins=200):
    tdc_slot = 2

    xL1 = LC3377Definition(tdc_slot, 0)
    yL1 = LC3377Definition(tdc_slot, 1)

    xL2 = LC3377Definition(tdc_slot, 2)
    yL2 = LC3377Definition(tdc_slot, 3)

    xL3 = LC3377Definition(tdc_slot, 6)
    yL3 = LC3377Definition(tdc_slot, 7)

    xL4 = LC3377Definition(tdc_slot, 8)
    yL4 = LC3377Definition(tdc_slot, 9)

    h1x = Histo1DSpec("Layer1x", "TDC Counts Layer 1x", nbins, xL1)
    h1y = Histo1DSpec("Layer1y", "TDC Counts Layer 1y", nbins, yL1)

    h2x = Histo1DSpec("Layer2x", "TDC Counts Layer 2x", nbins, xL2)
    h2y = Histo1DSpec("Layer2y", "TDC Counts Layer 2y", nbins, yL2)

    h3x = Histo1DSpec("Layer3x", "TDC Counts Layer 3x", nbins, xL3)
    h3y = Histo1DSpec("Layer3y", "TDC Counts Layer 3y", nbins, yL3)

    h4x = Histo1DSpec("Layer4x", "TDC Counts Layer 4x", nbins, xL4)
    h4y = Histo1DSpec("Layer4y", "TDC Counts Layer 4y", nbins, yL4)

    return HistoInfo1D((h1x, h1y, h2x, h2y, h3x, h3y, h4x, h4y),
                       "Comparative"), HistoMaker1D(
                           (h1x, h1y, h2x, h2y, h3x, h3y, h4x, h4y), "All")


def processWithCuts(modules1, modules2, inputFiles):
    t0 = datetime.now()
    n, newRunRecord = runAnalysisSequence(modules1, inputFiles)
    # n, newRunRecord = runAnalysisSequence(modules_og, inputFiles)
    n = updatedRunAnalysisSequence(newRunRecord, modules2, inputFiles)
    dt = datetime.now() - t0
    print('Processed %d events in %g sec' % (n, dt.total_seconds()))


def processDefault(modules_og, inputFiles):
    t0 = datetime.now()
    n, newRunRecord = runAnalysisSequence(modules_og, inputFiles)  #no cuts
    dt = datetime.now() - t0
    print('Processed %d events in %g sec' % (n, dt.total_seconds()))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
