# -*- coding: utf-8 -*-
"""
====================================================
Program : CrateAnalysis/crateAnalysisPlotter.py
====================================================
"""

__author__ = "Sadman Ahmed Shanto"
__date__ = "10/04/2020"
__email__ = "sadman-ahmed.shanto@ttu.edu"

import feather
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.plotting import andrews_curves
import sys
from MuonDataFrame import *
"""
# Query terms
'event_num', 'event_time', 'deadtime', 'TDC_L1_L', 'TDC_L1_R',
'TDC_L2_L', 'TDC_L2_R', 'ADC', 'TDC' , 'numChannelsRead', 'L1_asym',
'L2_asym', 'L1_TDC_sum', 'L2_TDC_sum', 'L1_TDC_diff', 'L2_TDC_diff'
"""

if __name__ == "__main__":
    try:
        ifile = sys.argv[1]
    except:
        print("No File passed / Invalid File")

    mdf = MuonDataFrame(ifile)
    print(mdf.show())
    # print(mdf.summary())

    # function descriptions
    # data filtering
    # mdf.show()
    # mdf.summary()
    # mdf.lookAt("TDC")
    # mdf.removeNoTDCEvents()
    # mdf.removeOutliers()
    # mdf.getStats("deadtime")
    # mdf.getEventInfo([10, 15])
    # mdf.getEventInfo(833)
    # filtered_mdf = mdf.getFilteredEvents(["deadtime > 900"])
    # filtered_mdf = mdf.getFilteredEvents(
    # ["L1_TDC_sum > 250", "deadtime > 900", "&"])
    # filtered_mdf = mdf.getFilteredEvents(
    # ["L1_TDC_sum > 250", "deadtime > 900", "|"])
    # filtered_mdf["L1_TDC_sum"].plot.hist(bins=150)
    # plt.show()

    # plots
    # mdf.getHistogram("deadtime")
    # mdf.getKDE("L1_TDC_sum")
    # mdf.getTrimmedHistogram("L1_TDC_sum", 3)
    # mdf.getComparableHistogram(["L1_TDC_sum", "L2_TDC_sum"])
    # mdf.getTrimmedComparableHistogram(["L1_TDC_sum", "L2_TDC_sum"], 3)
    # mdf.getFilteredHistogram("L1_TDC_sum", "numChannelsRead")
    # mdf.getPlot("deadtime")
    # mdf.getScatterPlot(["L1_asym", "L2_asym"])
    # mdf.get3DScatterPlot(["L1_asym", "L2_asym", "L1_TDC_sum"])
