# -*- coding: utf-8 -*-
"""
====================================================
Program : CrateAnalysis/crateAnalysisPlotter.py
====================================================
Summary:

To DO:
    - make Object Oriented
    - Stats display on histo
    - count number of events with multiple TDC
    - incorporate TDC array into the DataFrame
        - make sure TDC histo is correct
    - implement Igor 2D histo
    - methods for data filtering
    - Bell curve fit of histo
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


def getStats(df, queryName):
    s = df[queryName]
    print(s.describe())


def removeOutliers(df, queryName):
    q_low = df[queryName].quantile(0.01)
    q_hi = df[queryName].quantile(0.99)
    df_filtered = df[(df[queryName] < q_hi) & (df[queryName] > q_low)]
    return df_filtered


def scrubbedDataFrame(df, queryName, numStd):
    s = df[queryName]
    s_mean = s.mean()
    s_std = s.std()
    v_low = s.mean() - numStd * s_std
    v_hi = s.mean() + numStd * s_std
    df_filtered = df[(df[queryName] < v_hi) & (df[queryName] > v_low)]
    return df_filtered


def getTrimmedHistogram(df, queryName, numStd, nbins=100):
    df_filtered = scrubbedDataFrame(df, queryName, numStd)
    getHistogram(df_filtered,
                 queryName,
                 nbins,
                 title="(Events within {} std dev)".format(numStd))


def getTrimmed2DHistogram(df, queryName, numStd, nbins=100):
    pass


def getTrimmedFilteredHistogram(df, queryName, numStd, nbins=100):
    df_filtered = scrubbedDataFrame(df, queryName, numStd)
    getFilteredHistogram(df_filtered,
                         queryName,
                         nbins,
                         title="(Events within {} std dev)".format(numStd))


def getTrimmedComparableHistogram(df, queries, numStd, nbins=100):
    s = pd.DataFrame(columns=queries)
    s = s.fillna(0)  # with 0s rather than NaNs
    for query in queries:
        print(scrubbedDataFrame(df, query, numStd))
        s[query] = scrubbedDataFrame(df, query, numStd)[query]
    ax = s.plot.hist(alpha=0.7, bins=nbins)
    plt.title("Histogram of {} (Events within {} std dev)".format(
        str(queries), numStd))
    plt.show()


def getHistogram(df, queryName, nbins=100, title=""):
    s = df[queryName]
    ax = s.plot.hist(alpha=0.7, bins=nbins)
    ax.set_title("Histogram of {} {}".format(queryName, title))
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


def getFilteredHistogram(df, queryName, filter, nbins=100, title=""):
    df.hist(column=queryName, bins=nbins, by=filter)
    plt.suptitle("Histograms of {} grouped by {} {}".format(
        queryName, filter, title))
    plt.ylabel("Frequency")
    plt.show()


def getComparableHistogram(df, queries, nbins=100, title=""):
    s = pd.DataFrame(columns=queries)
    s = s.fillna(0)  # with 0s rather than NaNs
    for query in queries:
        s[query] = df[query]
    ax = s.plot.hist(alpha=0.7, bins=nbins)
    plt.title("Histogram of {} {}".format(str(queries), title))
    plt.show()


def get2DHistogram(df, queries, nbibs=1000, title=""):
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
    plt.title("2D Histogram of {} against {} {}".format(
        queries[0], queries[1], title))
    plt.show()


def dropna(arr, *args, **kwarg):
    assert isinstance(arr, np.ndarray)
    dropped = pd.DataFrame(arr).dropna(*args, **kwarg).values
    if arr.ndim == 1:
        dropped = dropped.flatten()
    return dropped


def getPlot(df, query, title=""):
    df[query].plot()
    plt.xlabel("Event Number")
    plt.ylabel(str(query))
    plt.title("Plot of {} event series {}".format(query, title))
    plt.show()


def getScatterPlot(df, queries, title=""):
    plt.scatter(df[queries[0]].values, df[queries[1]].values)
    plt.xlabel(str(queries[0]))
    plt.ylabel(str(queries[1]))
    plt.title("Scatter Plot of {} against {} {}".format(
        queries[0], queries[1], title))
    plt.show()


def get3DScatterPlot(df, queries, title=""):
    df.plot.scatter(x=queries[0],
                    y=queries[1],
                    c=queries[2],
                    colormap='viridis')
    plt.title(title)
    plt.show()


def getEventInfo(df, eventNum):
    if isinstance(eventNum, int):
        print(df.loc[df["event_num"] == eventNum])
    elif isinstance(eventNum, list):
        df = df[df['event_num'].between(eventNum[0], eventNum[1])]
        print(df)


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
    # getComparableHistogram(events_df, ["L1_TDC_sum", "L2_TDC_sum"])
    getTrimmedComparableHistogram(events_df, ["L1_TDC_sum", "L2_TDC_sum"], 3)

    # getEventInfo(events_df, [10, 15])
    # get3DScatterPlot(events_df, ["L1_asym", "L2_asym", "L1_TDC_sum"])
    # get3DScatterPlot(events_df, ["L1_asym", "L2_asym", "TDC_L1_L"])
    # get3DScatterPlot(events_df, ["L1_asym", "L2_asym", "TDC_L1_R"])
    # get3DScatterPlot(events_df, ["L1_asym", "L2_asym", "L2_TDC_sum"])
    # get3DScatterPlot(events_df, ["L1_asym", "L2_asym", "deadtime"])
    # getScatterPlot(events_df, ["L1_asym", "L2_asym"])
    # getPlot(events_df, "deadtime")
    # getComparableHistogram(events_df, ['TDC_L1_L', 'TDC_L1_R'])
    # getComparableHistogram(events_df, ["L1_TDC_sum", "L2_TDC_sum"])
    # getKDE(events_df, "L1_TDC_sum")
    # getHistogram(events_df, "L1_TDC_sum")
    # getTrimmedHistogram(events_df, "L1_TDC_sum", 3)
    # getFilteredHistogram(events_df, "L1_asym", "numChannelsRead")
    # getFilteredHistogram(events_df, "L1_TDC_sum", "numChannelsRead")
    # get2DHistogram(events_df, ["L1_asym", "L2_asym"])
