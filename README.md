# CAMAC DAQ CODE REPO

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

