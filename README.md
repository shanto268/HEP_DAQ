# CAMAC DAQ CODE REPO

A good general introduction to CAMAC is available at
http://prep.fnal.gov/introCamac.php

See also the relevant Wikipedia entry at
https://en.wikipedia.org/wiki/Computer_Automated_Measurement_and_Control

In order to understand how data acquisition works, you should read the
CAEN C111C CAMAC Crate Controller Technical Information Manual, file
name "C111C_user_manual_rev10.pdf". Functional descriptions of various
CAMAC modules are available on the web.

## Tutorial Notebook
This notebook explains the analysis API and usage.
[Notebook](CrateAnalysis/MuonAnalysisDoc.ipynb)

## Using the Notebook
1. Clone the repository.
```
git clone https://github.com/shanto268/HEP_DAQ.git
```
2. Make sure the data files (i.e. the .bin files are in the CrateCode directory) 
3. Make sure the CrateAnalysis directory has the *processed_data* directory containing the all the `.ftr` files
4. Using Anaconda or terminal open the `MuonAnalysisDoc.ipynb` located in the CrateAnalysis directory.
