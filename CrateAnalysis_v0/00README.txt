This directory contains a simple python-based data analysis framework
for the CAMAC runs. You can easily develop your own analysis code by
writing an analysis class which inherits from "AbsAnalysisModule" and
plugging it into the sequence of modules as illustrated in the
"analysisExample.py" script.

The files in this directory are:

00README.txt              This file.

AbsAnalysisModule.py      The base class for all analysis modules.

ADCPrintingModule.py      A simple data printing class derived from
                          AbsAnalysisModule.

analysisExample.py        An example which illustrates how to create
                          a sequence of analysis modules and then analyze
                          the data using these modules.

GenericPrintingModule.py  Another printing class, intended for dumping
                          arbitrary elements of the event record.

HistoMaker1D.py           A module for plotting simple 1-d histograms at
                          the end of the job.

runAnalysisSequence.py    The analysis sequencer which loads the data from
                          disk and invokes the analysis modules.

UtilityModules.py         Simple example analysis modules with some general
                          usefulness.

Example usage which will work in case you took a "normal" run as explained
in the 00README.txt file of the "CrateCode" directory:

./analysisExample.py dump ../CrateCode/run7.bin

This particular example will plot the histograms of some channels and
will dump every 100th event in a text format (with extension .csv)
suitable for subsequent loading into Matlab, etc.


Igor Volobouev
June 23 2017
