# -*- coding: utf-8 -*-
"""
====================================================
Program : CrateAnalysis/crateAnalysisPlotter.py
====================================================

NEED TO DO:
    1. create .pdf report
    2. create .csv file
    3. upload .csv to OneDrive
        3.a analyze matlab script on .csv
    4. send email with pdf (python and matlab) and onedrive upload update
"""

__author__ = "Sadman Ahmed Shanto"
__date__ = "10/04/2020"
__email__ = "sadman-ahmed.shanto@ttu.edu"

from MuonDataFrame import *

if __name__ == "__main__":
    try:
        ifile = sys.argv[1]
        iisNew = sys.argv[2]
    except:
        print("No File passed / Invalid File")
        iisNew = False
        print("\nAssuming the file has been analyzed before.")

    mdfo = MuonDataFrame(ifile, isNew=iisNew, d1="last")
    mdfo.getCSVOutputFile(10000)
    #mdfo.sendReportEmail()
    #mdfo.generateAnaReport()
