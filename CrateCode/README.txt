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

 HistoMaker2D.py           A module for plotting simple 2-d histograms at
                           the end of the job.

 LC3377PrintingModule.py   A module for printing LeCroy 3377 TDC data to the
                           standard output in a human-readable form.

 runAnalysisSequence.py    The analysis sequencer which loads the data from
                           disk and invokes the analysis modules.

 TDCPrintingModule.py      A simple data printing class derived from
                           AbsAnalysisModule. Intended for printing data
                           collected by LeCroy 2228A TDCs.

 test_HistoMaker2D.py      A stand-alone testing script for the HistoMaker2D
                           class.

 UtilityModules.py         Simple example analysis modules with some general
                           usefulness.

 Example usage which will work in case you took a "normal" run as explained
 in the 00README.txt file of the "CrateCode" directory:

 ./analysisExample.py dump ../CrateCode/run7.bin

