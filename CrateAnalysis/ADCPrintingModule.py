"""
A simple data printing module for the CAMAC data analysis framework
"""

__author__="Igor Volobouev (i.volobouev@ttu.edu)"
__version__="0.1"
__date__ ="June 22 2017"

from AbsAnalysisModule import AbsAnalysisModule

class ADCPrintingModule(AbsAnalysisModule):
    """
    Module constructor arguments are:

    prefix              Defines the base name for the output files. The files
                        will be named {prefix}_NN_XX.csv, where NN is the run
                        number and XX is the event number.

    printRowLabels      If True, print row labels.

    printColumnLabels   If True, print column labels.
    """
    def __init__(self, prefix, printRowLabels=True,
                 printColumnLabels=False):
        AbsAnalysisModule.__init__(self, "ADCPrintingModule")
        self.prefix = prefix
        self.printColumnLabels = bool(printColumnLabels)
        self.printRowLabels = bool(printRowLabels)

    def beginJob(self, allModuleNames):
        pass

    def endJob(self):
        pass

    def beginRun(self, runNumber, runInfo):
        runConfig = runInfo[(runNumber, "runConfiguration")]
        self.adc_channels = runConfig["adc_channels"]
        self.adc_slots = runConfig["adc_slots"]

    def endRun(self, runNumber, runInfo):
        pass

    def processEvent(self, runNumber, eventNumber, eventRecord):
        filename = "%s_%d_%d.csv" % (self.prefix, runNumber, eventNumber)
        with open(filename, 'w') as f:
            # Write out the column labels, if requested
            if self.printColumnLabels:
                if self.printRowLabels:
                    f.write("Row Label,")
                f.write(','.join(["ch%d" % i for i in range(self.adc_channels)]))
                f.write('\n')

            # Write out the ADC values
            for slot in self.adc_slots:
                if self.printRowLabels:
                    f.write("Slot %d," % slot)
                adcValues = eventRecord[(slot,"LeCroy2249")]
                f.write(','.join("%d" % adc for adc in adcValues))
                f.write('\n')
