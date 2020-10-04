# -*- coding: utf-8 -*-
"""
====================================================
Program : CrateAnalysis/crateAnalysisPlotter.py
====================================================
Summary:

To DO:
    - incorporate TDC array into the DataFrame
    - implement Igor 2D histo
    - arbitrary cutting of histo
    - methods for data filtering
    - Bell curve fit of histo
    - Stats display on histo
    - Recreate of all graphs
    - Plots of arrays (Optional)
    - GUI interface?
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


def getHistogram(df, queryName, nbins=100):
    s = df[queryName]
    ax = s.plot.hist(alpha=0.7, bins=nbins)
    ax.set_title("Histogram of {}".format(queryName))
    plt.show()
    # df.hist(column=queryName, bins=nbins)
    # plt.ylabel("Frequency")
    # plt.show()


def getKDE(df, queryName, nbins=100):
    s = df[queryName].to_numpy()
    s = pd.Series(s)
    ax = s.plot.kde()
    ax.set_title("Probability Density of {}".format(queryName))
    plt.show()


def getFilteredHistogram(df, queryName, filter, nbins=100):
    df.hist(column=queryName, bins=nbins, by=filter)
    plt.suptitle("Histograms of {} grouped by {}".format(queryName, filter))
    plt.ylabel("Frequency")
    plt.show()


def getComparableHistogram(df, queries, nbins=100):
    s = pd.DataFrame(columns=queries)
    s = s.fillna(0)  # with 0s rather than NaNs
    for query in queries:
        s[query] = df[query]
    ax = s.plot.hist(alpha=0.7, bins=nbins)
    plt.title("Histogram of {}".format(str(queries)))
    plt.show()


def get2DHistogram(df, queries, nbibs=1000):
    x = df[queries[0]].to_numpy()
    y = df[queries[1]].to_numpy()
    x = dropna(x)
    y = dropna(y)
    while (len(x) != len(y)):
        if (len(x) > len(y)):
            x = x[:-1]
        else:
            y = y[:-1]
    plt.hist2d(x, y)
    plt.title("2D Histogram of {} against {}".format(queries[0], queries[1]))
    plt.show()


def dropna(arr, *args, **kwarg):
    assert isinstance(arr, np.ndarray)
    dropped = pd.DataFrame(arr).dropna(*args, **kwarg).values
    if arr.ndim == 1:
        dropped = dropped.flatten()
    return dropped


def getPlot(df, query):
    df[query].plot()
    plt.xlabel("Event Number")
    plt.ylabel(str(query))
    plt.title("Plot of {} event series".format(query))
    plt.show()


def getScatterPlot(df, queries):
    plt.scatter(df[queries[0]].values, df[queries[1]].values)
    plt.xlabel(str(queries[0]))
    plt.ylabel(str(queries[1]))
    plt.title("Scatter Plot of {} against {}".format(queries[0], queries[1]))
    plt.show()


def get3DScatterPlot(df, queries):
    df.plot.scatter(x=queries[0],
                    y=queries[1],
                    c=queries[2],
                    colormap='viridis')
    plt.show()


"""
# Query terms
'event_num', 'event_time', 'deadtime', 'TDC_L1_L', 'TDC_L1_R',
'TDC_L2_L', 'TDC_L2_R', 'ADC', 'numChannelsRead', 'L1_asym',
'L2_asym', 'L1_TDC_sum', 'L2_TDC_sum', 'L1_TDC_diff', 'L2_TDC_diff'
"""

if __name__ == "__main__":
    try:
        ifile = sys.argv[1]
    except:
        print("No File passed / Invalid File")
        # ifile = "processed_data/events_data_frame_510.ftr"  # needs change later
    events_df = pd.read_feather(ifile, use_threads=True)
    get3DScatterPlot(events_df, ["L1_asym", "L2_asym", "L1_TDC_sum"])
    get3DScatterPlot(events_df, ["L1_asym", "L2_asym", "TDC_L1_L"])
    get3DScatterPlot(events_df, ["L1_asym", "L2_asym", "TDC_L1_R"])
    # get3DScatterPlot(events_df, ["L1_asym", "L2_asym", "L2_TDC_sum"])
    # get3DScatterPlot(events_df, ["L1_asym", "L2_asym", "deadtime"])
    # getScatterPlot(events_df, ["L1_asym", "L2_asym"])
    # getPlot(events_df, "deadtime")
    # getComparableHistogram(events_df, ['TDC_L1_L', 'TDC_L1_R'])
    # getComparableHistogram(events_df, ["L1_TDC_sum", "L2_TDC_sum"])
    # getKDE(events_df, "L1_TDC_sum")
    # getHistogram(events_df, "L1_TDC_sum")
    # getFilteredHistogram(events_df, "L1_asym", "numChannelsRead")
    # getFilteredHistogram(events_df, "L1_TDC_sum", "numChannelsRead")
    # get2DHistogram(events_df, ["L1_asym", "L2_asym"])
