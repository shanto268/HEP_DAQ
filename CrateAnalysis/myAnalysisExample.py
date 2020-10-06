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
from TDCUnpacker import *
from TDCAnalyzer import *
from NoiseCleaner import *
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
    mod9 = ChannelOperations("ChannelOperations")
    mod10 = NoiseCleaner("NoiseCleaner")
    gptr = GenericPrintingModule(("hw_event_count", "deadtime"))

    # Example histogram specifier
    h0 = Histo1DSpec("Dead Time", "Counts", 100, lambda x: x["deadtime"])
    h1 = Histo1DSpec("Number of hits per Event", "Counts", 10,
                     lambda x: x["len_unpacked_3377Data"])
    hMaker = HistoMaker1D((h0, ), "h0")
    hMaker2 = HistoMaker1D((h1, ), "NumHitsPerEvent")

    #adcPlotter = ADCHisto(100, 5, 0.4)
    #tdcPlotter = TDCHisto(100, 5, 0.4)
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
    tdcHAll = modChannelIndividualPlotters(tdcChannelsAll)
    tdcHL1 = modChannelIndividualPlotters(tdcChannelsL1)
    tdcHL2 = modChannelIndividualPlotters(tdcChannelsL2)

    xdefinitionL1 = LC3377Definition(slot1, channel1)
    ydefinitionL1 = LC3377Definition(slot2, channel2)

    xdefinitionL2 = LC3377Definition(slot3, channel3)
    ydefinitionL2 = LC3377Definition(slot4, channel4)

    h1x = Histo1DSpec("Layer1x", "TDC Counts Layer 1x", 200, xdefinitionL1)
    h1y = Histo1DSpec("Layer1y", "TDC Counts Layer 1y", 200, ydefinitionL1)

    h2x = Histo1DSpec("Layer2x", "TDC Counts Layer 2x", 200, xdefinitionL2)
    h2y = Histo1DSpec("Layer2y", "TDC Counts Layer 2y", 200, ydefinitionL2)

    # hMaker1x = HistoMaker1D((h1x, ), "Layer 1 Channel 0")
    # hMaker1y = HistoMaker1D((h1y, ), "Layer 1 Channel 1")

    # hMaker2x = HistoMaker1D((h2x, ), "Layer 2 Channel 2")
    # hMaker2y = HistoMaker1D((h2y, ), "Layer 2 Channel 3")

    histAllChannels = HistoInfo1D((h1x, h1y, h2x, h2y), "Comparative")
    histAllChannelSep = HistoMaker1D((h1x, h1y, h2x, h2y), "All")

    h2dL1 = modChannelVsPlotters(slot1, channel1, slot2, channel2,
                                 xdefinitionL1, ydefinitionL1, "h2dL1")
    h2dL1_rotate = modChannelVsPlotters(slot1,
                                        channel1,
                                        slot2,
                                        channel2,
                                        xdefinitionL1,
                                        ydefinitionL1,
                                        "h2dL1_rotate",
                                        rotate=True)

    h2dL2_rotate = modChannelVsPlotters(slot3,
                                        channel3,
                                        slot4,
                                        channel4,
                                        xdefinitionL2,
                                        ydefinitionL2,
                                        "h2dL2_rotate",
                                        rotate=True)

    h2dL2 = modChannelVsPlotters(slot3, channel3, slot4, channel4,
                                 xdefinitionL2, ydefinitionL2, "h2dL2")

    L1diff = lambda eventRecord: eventRecord["TDCAnalyzer"]["Layer1diff"]
    L2diff = lambda eventRecord: eventRecord["TDCAnalyzer"]["Layer2diff"]
    L1asym = lambda eventRecord: eventRecord["TDCAnalyzer"]["Layer1asym"]
    L2asym = lambda eventRecord: eventRecord["TDCAnalyzer"]["Layer2asym"]

    histo_layer1diff = Histo1DSpec("Layer1", "TDC Counts Diff Layer 1", 200,
                                   L1diff)
    histo_layer2diff = Histo1DSpec("Layer2", "TDC Counts Diff Layer 2", 200,
                                   L2diff)
    histo_layer1asym = Histo1DSpec(
        "Layer1", "Asymmetry Layer 1", 200,
        lambda x: x["TDCAnalyzer"].get("Layer1asym"))

    histo_layer2asym = Histo1DSpec(
        "Layer2", "Asymmetry Layer 2", 200,
        lambda eventRecord: eventRecord["TDCAnalyzer"].get("Layer2asym"))

    global hitMap  #, myLayer1diff, myLayer2diff, myLayer1asym, myLayer2asym

    hitMap = HistoMaker2D("hitMap", "Hit Map", "Asymmetry in X", nbins, -30.0,
                          30.0, L1asym, "Asymmetry in Y", nbins, -30.0, 30.0,
                          L2asym)
    myLayer1diff = HistoMaker1D((histo_layer1diff, ), "histo_layer1diff")
    myLayer2diff = HistoMaker1D((histo_layer2diff, ), "histo_layer2diff")
    myLayer1asym = HistoMaker1D((histo_layer1asym, ), "histo_layer1asym")
    myLayer2asym = HistoMaker1D((histo_layer2asym, ), "histo_layer2asym")

    #channels 0 and 1
    ch0Subch1 = lambda x: x["Layer_1"].get("sub_TDC")
    histo_ch0Subch1 = Histo1DSpec("Layer 1 Ch0 - Ch 1",
                                  "TDC counts diff Ch0 and Ch 1", 200,
                                  ch0Subch1)
    hMaker_ch0Subch1 = HistoMaker1D((histo_ch0Subch1, ), "hmaker_ch0Subch1")

    ch0Addch1 = lambda x: x["Layer_1"].get("add_TDC")
    histo_ch0Addch1 = Histo1DSpec("Layer 1 Ch0 + Ch 1",
                                  "TDC counts add Ch0 and Ch 1", 200,
                                  ch0Addch1)

    hMaker_ch0Addch1 = HistoMaker1D((histo_ch0Addch1, ),
                                    "hmaker_ch0Addch1",
                                    gaussian=True)

    #channels 3 and 4
    ch3Subch4 = lambda x: x["Layer_2"].get("sub_TDC")
    histo_ch3Subch4 = Histo1DSpec("Layer 2 Ch3 - Ch 4",
                                  "TDC counts diff Ch3 and Ch 4", 200,
                                  ch3Subch4)
    hMaker_ch3Subch4 = HistoMaker1D((histo_ch3Subch4, ), "hmaker_ch3Subch4")

    ch3Addch4 = lambda x: x["Layer_2"].get("add_TDC")
    histo_ch3Addch4 = Histo1DSpec("Layer 2 Ch3 + Ch 4",
                                  "TDC counts add Ch3 and Ch 4", 200,
                                  ch3Addch4)
    hMaker_ch3Addch4 = HistoMaker1D((histo_ch3Addch4, ),
                                    "hmaker_ch3Addch4",
                                    gaussian=True)
    hMaker2D_comp_layer_plot = HistoMaker2D("comp layer plot",
                                            "Ch 0 - Ch 1 vs Ch 3 - Ch 4",
                                            "TDC difference in Layer 1", nbins,
                                            -60.0, 60.0, ch0Subch1,
                                            "TDC difference in Layer 2", nbins,
                                            -60.0, 60.0, ch3Subch4)

    # Define the sequence of modules
    #    modules = (mod0, mod1, mod7, mod8, tdcH, hitMap)
    # [hMaker1x, hMaker1y, hMaker2x, hMaker2y])
    modules1 = (mod0, mod1, mod7, mod8, mod9, mod10)
    modules2 = (
        hMaker_ch0Subch1,
        hMaker_ch0Addch1,
        hMaker_ch3Subch4,
        hMaker_ch3Addch4,
        histAllChannels,
        histAllChannelSep,
        myLayer1asym,
        myLayer2asym,
        h2dL1_rotate,
        h2dL2_rotate,
        hMaker2,
        h2dL1,
        h2dL2,
        tdcHAll,
        hitMap,
        # hMaker2D_comp_layer_plot,
    )  #all plots
    modules_og = (mod0, mod1, mod7, mod8, mod9)
    modules_og += modules2

    # working cuts
    # t0 = datetime.now()
    # n, newRunRecord = runAnalysisSequence(modules1, inputFiles)
    # # n, newRunRecord = runAnalysisSequence(modules_og, inputFiles)
    # n = updatedRunAnalysisSequence(newRunRecord, modules2, inputFiles)
    # dt = datetime.now() - t0
    # print('Processed %d events in %g sec' % (n, dt.total_seconds()))

    # processWithCuts(modules1, modules2, inputFiles)
    processDefault(modules_og, inputFiles)
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
    n, newRunRecord = runAnalysisSequence(modules_og, inputFiles)  #no cuts
    dt = datetime.now() - t0
    print('Processed %d events in %g sec' % (n, dt.total_seconds()))


def modChannelIndividualPlotters(tdcChannels):
    tdcH = TDCHisto(400, 1000, 0.4, tdcChannels)
    return tdcH


def modChannelVsPlotters(slot1,
                         channel1,
                         slot2,
                         channel2,
                         xdefinition,
                         ydefinition,
                         hname,
                         rotate=False):

    xlabel = "TDC counts for slot %s ch %s" % (slot1, channel1)
    ylabel = "TDC counts for slot %s ch %s" % (slot2, channel2)
    title = "Slot %s ch %s vs. slot %s ch %s" % (slot2, channel2, slot1,
                                                 channel1)
    histo = HistoMaker2D(hname,
                         title,
                         xlabel,
                         nbins,
                         0.0,
                         200.0,
                         xdefinition,
                         ylabel,
                         nbins,
                         0.0,
                         200.0,
                         ydefinition,
                         rotate=rotate)
    return histo


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
