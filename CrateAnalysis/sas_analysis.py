"""
Usage: analysisExample.py outputPrefix inputFile0 ...
"""

import sys, ray
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
from TDCUnpacker import *
from TDCAnalyzer import *
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
    mod7 = TDCUnpacker("TDCUnpacker")
    mod8 = TDCAnalyzer("TDCAnalyzer")
    # mod9 = ChannelOperations("ChannelOperations")
    # mod10 = NoiseCleaner("NoiseCleaner")
    mod11 = EventDataFrame("EventDataFrame")
    mod12 = MissingTDCCounter("MissingTDCCounter")
    gptr = GenericPrintingModule(("hw_event_count", "deadtime"))

    global nbins
    nbins = 250

    slot1 = 2
    channel1 = 0
    slot2 = 2
    channel2 = 1

    slot3 = 2
    channel3 = 3
    slot4 = 2
    channel4 = 4

    tdcChannelsAll = ((slot1, 1), (slot1, 2), (slot1, 3), (slot1, 4))
    tdcChannelsL1 = ((slot1, 1), (slot1, 2))
    tdcChannelsL2 = ((slot1, 3), (slot1, 4))

    xdefinitionL1 = LC3377Definition(slot1, channel1)
    ydefinitionL1 = LC3377Definition(slot2, channel2)

    xdefinitionL2 = LC3377Definition(slot3, channel3)
    ydefinitionL2 = LC3377Definition(slot4, channel4)

    # modules = (mod0, mod1, mod7, mod8, mod11)
    # modules = (mod0, mod1, mod7, mod8)
    modules = (mod0, mod1, mod7, mod8, mod11)

    # processWithCuts(modules1, modules2, inputFiles)
    processDefault(modules, inputFiles)
    return 0


def processWithCuts(modules1, modules2, inputFiles):
    t0 = datetime.now()
    n, newRunRecord = runAnalysisSequence(modules1, inputFiles)
    # n, newRunRecord = runAnalysisSequence(modules_og, inputFiles)
    n = updatedRunAnalysisSequence(newRunRecord, modules2, inputFiles)
    dt = datetime.now() - t0
    print('Processed %d events in %g sec' % (n, dt.total_seconds()))


def processDefault(modules_og, inputFiles):
    t0 = datetime.now()
    n, newRunRecord = runAnalysisSequence(modules_og, inputFiles)
    dt = datetime.now() - t0
    print('Processed %d events in %g sec' % (n, dt.total_seconds()))


if __name__ == '__main__':
    ray.init(ignore_reinit_error=True, num_cpus=2)
    sys.exit(main(sys.argv[1:]))
