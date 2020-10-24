# -*- coding: utf-8 -*-
"""
====================================================
Program : CrateAnalysis/gui_ana.py
====================================================
"""

__author__ = "Sadman Ahmed Shanto"
__date__ = "10/04/2020"
__email__ = "sadman-ahmed.shanto@ttu.edu"

import feather
import sys
from MuonDataFrame import *
"""
# Query terms
'event_num', 'event_time', 'deadtime', 'TDC_L1_L', 'TDC_L1_R',
'TDC_L2_L', 'TDC_L2_R', 'ADC', 'TDC' , 'numChannelsRead', 'L1_asym',
'L2_asym', 'L1_TDC_sum', 'L2_TDC_sum', 'L1_TDC_diff', 'L2_TDC_diff'
"""
"""
Access data from HDF5
# Access data store
data_store = pd.HDFStore('processed_data.h5')

# Retrieve data using key
preprocessed_df = data_store['preprocessed_df']
data_store.close()
"""

if __name__ == "__main__":
    try:
        ifile = sys.argv[1]
        iisNew = sys.argv[2]
    except:
        print("No File passed / Invalid File")
        iisNew = False
        print("\nAssuming the file has been analyzed before.")

    os.environ["MODIN_ENGINE"] = "ray"
    mdfo = MuonDataFrame(ifile, isNew=iisNew, d1="last")
    mdf = mdfo.events_df
    print(mdfo.show())
    mdfo.gui()
    # mdfo.getAnaReport()
    # mdfo.generateAnaReport()
    # mdfo.computeAssymetries()
    # mdfo.get2DHistogram()
    # mdfo.getScatterPlot(["L1_asym", "L2_asym"])
    # mdfo.getScatterPlot(["L3_asym", "L4_asym"])
    # mdfo.getScatterPlot(["L1_asym", "L3_asym"])
    # mdfo.getScatterPlot(["L2_asym", "L4_asym"])
    # # mdfo.getAssymetry1DPlots()

    # mdf = mdfo.events_df
    # goodEv = (mdf['TR12'] == True)
    # print(mdf[goodEv])

    # function descriptions
    # data filtering
    # mdfo.show()
    # mdfo.summary()
    # mdfo.lookAt("TDC")
    # mdfo.removeNoTDCEvents()
    # mdfo.removeOutliers()
    # mdfo.getStats("deadtime")
    # mdfo.getEventInfo([10, 15])
    # mdfo.getEventInfo(833)
    # filtered_mdf = mdfo.getFilteredEvents(["deadtime > 900"])
    # filtered_mdf = mdfo.getFilteredEvents(
    # ["L1_TDC_sum > 250", "deadtime > 900", "&"])
    # filtered_mdf = mdfo.getFilteredEvents(
    # ["L1_TDC_sum > 250", "deadtime > 900", "|"])
    # filtered_mdf["L1_TDC_sum"].plot.hist(bins=150)
    # plt.show()

    # # plots
    # mdfo.getHistogram("deadtime")
    # mdfo.getKDE("L1_TDC_sum")
    # mdfo.getTrimmedHistogram("L1_TDC_sum", 3)
    # mdfo.getComparableHistogram(["L1_TDC_sum", "L2_TDC_sum"])
    # mdfo.getTrimmedComparableHistogram(["L1_TDC_sum", "L2_TDC_sum"], 3)
    # mdfo.getFilteredHistogram("L1_TDC_sum", "numChannelsRead")
    # mdfo.getPlot("deadtime")
    # mdfo.getScatterPlot(["L1_asym", "L2_asym"])
    # mdfo.get3DScatterPlot(["L1_asym", "L2_asym", "L1_TDC_sum"])
