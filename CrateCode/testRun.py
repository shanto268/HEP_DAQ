#!/usr/bin/env python3
import os, sys, csv, time
from runCAMAC import runCAMAC
from ADCHisto import ADCHisto, TDCHisto, ScalerHisto
from MultipleUpdater import *
"""
Arguments: 
    i) number of events
    ii) boolean for plotting
"""


def main(totalEvents, test_num, doPlot):
    configModule = "NuralTest"
    maxEvents = totalEvents
    maxTimeSec = 0
    runNumber = test_num
    outputFile = "test/test{}_{}.bin".format(test_num, totalEvents)
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
    # global MUONRATE
    # wtime = round(totalEvents * float(MUONRATE))
    if doPlot:
        print("Starting DAQ system with diagnostic plots...")
    else:
        print("Starting DAQ system....")
    # if wtime == 0:
    # print("Process will take roughly {} min".format(1))
    # else:
    # print("Process will take roughly {} mins".format(wtime))

    # Configure the histogram plotter.
    # The channels to plot: a tuple of (slot, channel) pairs.
    # "None" will take all channels configured in the DAQ.
    channels_to_plot = ((2, 0), (2, 1), (2, 2), (2, 3), (2, 6), (2, 7), (2, 8),
                        (2, 9))
    scaler_channels = ((5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9), (5, 10),
                       (5, 11))
    nBins = 2
    updateAfterHowManyEvents = 10
    verticalSpaceAdjustment = 0.4
    #adcHisto = ADCHisto(nBins, updateAfterHowManyEvents,
    #                    verticalSpaceAdjustment, channels_to_plot)

    tdcHisto = TDCHisto(100 * nBins, updateAfterHowManyEvents,
                        verticalSpaceAdjustment, channels_to_plot)
    scalerHisto = ScalerHisto(nBins, updateAfterHowManyEvents,
                              verticalSpaceAdjustment, scaler_channels)

    plotUpdater = plotDiagnostics(doPlot, scalerHisto, tdcHisto)
    n, t, s, err = runCAMAC(configModule, maxEvents, maxTimeSec, runNumber,
                            outputFile, plotUpdater)

    print('Processed %d events in %g sec' % (n, t))
    print('Run status is', s)
    if s == "Error":
        print('Error message:', err)
    if not (outputFile == "None" or outputFile == "none"):
        print('Run %d data is stored in the file "%s"' %
              (runNumber, outputFile))
    return 0
    # return outputFile


def updateEnvVar():
    r = csv.reader(open('daq_env_var.csv'))  # Here your csv file
    lines = list(r)
    test_num = int(lines[0][1])
    lines[0][1] = test_num + 1
    writer = csv.writer(open('daq_env_var.csv', 'w'))
    writer.writerows(lines)
    return test_num


def plotDiagnostics(doPlot, histo, histo2):
    if doPlot:
        return None
        # return MultipleUpdater(histo, histo2)
    else:
        return None


def analyzeData(test_num, totalEvents):
    outputFile = "test/test{}_{}.bin".format(test_num, totalEvents)
    os.system(
        'python /home/daq/CAMAC/CrateAnalysis_sas/test_analysis.py junk {}'.
        format(outputFile))


if __name__ == "__main__":
    MUONRATE = 0.003298866666666666
    totalEvents = int(sys.argv[1])
    doPlot = sys.argv[2]
    if doPlot == "True":
        doPlot = True
        testNum = updateEnvVar()
        main(totalEvents, testNum, doPlot)
        analyzeData(testNum, totalEvents)

    elif doPlot == "False":
        doPlot = False
        testNum = updateEnvVar()
        main(totalEvents, testNum, doPlot)
    else:
        print("Diagnostic Plot Option Not Specified.\nTerminating Program.")
