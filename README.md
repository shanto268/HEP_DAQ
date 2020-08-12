# CAMAC DAQ CODE REPO

A good general introduction to CAMAC is available at
http://prep.fnal.gov/introCamac.php

See also the relevant Wikipedia entry at
https://en.wikipedia.org/wiki/Computer_Automated_Measurement_and_Control

In order to understand how data acquisition works, you should read the
CAEN C111C CAMAC Crate Controller Technical Information Manual, file
name "C111C_user_manual_rev10.pdf". Functional descriptions of various
CAMAC modules are available on the web.


## Directory and Important Files
The *CrateCode/* directory contains all the data files (*.bin). The *CrateAnalysis/* contains the analysis code (myAnalysisExample.py).

## Example Usage
The arguments are fileToStoreRunTimeData dataFileGeneratedByCAMAC

```bash
python myAnalysisExample.py junk ../CrateCode/run318.bin
```
If running in SpyDer/ipython:

```python
%run ./myAnalysisExample.py junk ../CrateCode/run318.bin
hitMap.redraw(0,15) #code to fix the z-axis limit
```

