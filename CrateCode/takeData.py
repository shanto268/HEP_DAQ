#!/usr/bin/env python3
import os, sys, csv, time
from runCAMAC import runCAMAC
from ADCHisto import ADCHisto, TDCHisto
from MultipleUpdater import *
from Notify import Notify
"""
Arguments: 
    i) number of events
"""


def main(totalEvents, test_num):
    doPlot = False
    configModule = "NuralTest"
    maxEvents = totalEvents
    maxTimeSec = 0
    runNumber = test_num
    outputFile = "data_sets/run{}_{}.bin".format(test_num, totalEvents)
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
    global MUONRATE
    wtime = round(totalEvents * float(MUONRATE))
    print(25 * "=")
    print("\nRun {} for {} Events \n".format(test_num, totalEvents))
    print("Starting DAQ system....")
    # if wtime == 0:
    # print("Process will take roughly {} min".format(1))
    # else:
    # print("Process will take roughly {} mins".format(wtime))
    # Configure the histogram plotter.
    # The channels to plot: a tuple of (slot, channel) pairs.
    # "None" will take all channels configured in the DAQ.
    channels_to_plot = ((2, 0), (2, 1), (2, 3), (2, 4), (2, 6), (2, 7), (2, 9),
                        (2, 10))
    nBins = 100
    updateAfterHowManyEvents = 10
    verticalSpaceAdjustment = 0.4
    adcHisto = ADCHisto(nBins, updateAfterHowManyEvents,
                        verticalSpaceAdjustment, channels_to_plot)
    tdcHisto = TDCHisto(nBins, updateAfterHowManyEvents,
                        verticalSpaceAdjustment, channels_to_plot)

    plotUpdater = plotDiagnostics(doPlot, adcHisto, tdcHisto)
    n, t, s, err = runCAMAC(configModule, maxEvents, maxTimeSec, runNumber,
                            outputFile, plotUpdater)

    print('Processed %d events in %g sec' % (n, t))
    print('Run status is', s)
    if s == "Error":
        print('Error message:', err)
    if not (outputFile == "None" or outputFile == "none"):
        print('Run %d data is stored in the file "%s"' %
              (runNumber, outputFile))
    print("Uploading File to Quanah.....\n")
    os.system("upload.sh {}".format(outputFile))
    print("File {} has been successfully uploaded to Quanah\n".format(
        outputFile))
    print(25 * "=")
    print()
    fileName = outputFile.split("/")[1]
    Notify(fileName)
    return 0


def updateEnvVar():
    r = csv.reader(open('daq_env_var.csv'))  # Here your csv file
    lines = list(r)
    test_num = int(lines[1][1])
    lines[1][1] = test_num + 1
    writer = csv.writer(open('daq_env_var.csv', 'w'))
    writer.writerows(lines)
    return test_num


def plotDiagnostics(doPlot, adcHisto, tdcHisto):
    if doPlot:
        return MultipleUpdater(adcHisto, tdcHisto)
    else:
        return None


if __name__ == "__main__":
    MUONRATE = 0.003298866666666666
    totalEvents = int(sys.argv[1])
    testNum = updateEnvVar()
    main(totalEvents, testNum)
