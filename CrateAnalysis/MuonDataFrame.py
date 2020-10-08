# -*- coding: utf-8 -*-
"""
=============================================
Program : CrateAnalysis/MuonDataFrame.py
=============================================
Summary:
"""
__author__ = "Sadman Ahmed Shanto"
__date__ = "10/06/2020"
__email__ = "sadman-ahmed.shanto@ttu.edu"
""""
To DO:
    - implement methods that updates all TDC columns using some TDC value
        - first TDC
        - max TDC
        - min TDC
    - generate report method
    - data filtering method
    - implement Igor 2D histo
    - Bell curve fit of histo
    - Recreate of all graphs
    - Plots of arrays
    - GUI make
"""

import feather
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
from pandas.plotting import andrews_curves
from collections import Counter
"""
# Query terms
'event_num', 'event_time', 'deadtime', 'TDC_L1_L', 'TDC_L1_R',
'TDC_L2_L', 'TDC_L2_R', 'ADC', 'numChannelsRead', 'L1_asym',
'L2_asym', 'L1_TDC_sum', 'L2_TDC_sum', 'L1_TDC_diff', 'L2_TDC_diff'
"""


def conditionParser_multiple(df, conditions):
    qt, op, val = conditions.split(" ")
    if op == "==":
        df = df[df[qt] == float(val)]
        print(df[df[qt] == float(val)])
    elif op == ">":
        df = df[df[qt] > float(val)]
        # print(df[df[qt] > float(val)])
    elif op == "<":
        df = df[df[qt] < float(val)]
        print(df[df[qt] < float(val)])
    elif op == ">=":
        df = df[df[qt] >= float(val)]
        print(df[df[qt] >= float(val)])
    elif op == "<=":
        df = df[df[qt] <= float(val)]
        print(df[df[qt] <= float(val)])
    elif op == "!=":
        df = df[df[qt] != float(val)]
        print(df[df[qt] != float(val)])
    return df


def conditionParser_single(df, conditions):
    qt, op, val = conditions[0].split(" ")
    if op == "==":
        df = df[df[qt] == float(val)]
        print(df[df[qt] == float(val)])
    elif op == ">":
        df = df[df[qt] > float(val)]
        # print(df[df[qt] > float(val)])
    elif op == "<":
        df = df[df[qt] < float(val)]
        print(df[df[qt] < float(val)])
    elif op == ">=":
        df = df[df[qt] >= float(val)]
        print(df[df[qt] >= float(val)])
    elif op == "<=":
        df = df[df[qt] <= float(val)]
        print(df[df[qt] <= float(val)])
    elif op == "!=":
        df = df[df[qt] != float(val)]
        print(df[df[qt] != float(val)])
    return df


def getFilteredEvents(self, df, conditions):
    numConditions = len(conditions)
    if numConditions == 1:
        qt, op, val = conditions[0].split(" ")
        if op == "==":
            print(df[df[qt] == float(val)])
        elif op == ">":
            print(df[df[qt] > float(val)])
        elif op == "<":
            print(df[df[qt] < float(val)])
        elif op == ">=":
            print(df[df[qt] >= float(val)])
        elif op == "<=":
            print(df[df[qt] <= float(val)])
        elif op == "!=":
            print(df[df[qt] != float(val)])


def scrubbedDataFrame(df, queryName, numStd):
    s = df[queryName]
    s_mean = s.mean()
    s_std = s.std()
    v_low = s.mean() - numStd * s_std
    v_hi = s.mean() + numStd * s_std
    df_filtered = df[(df[queryName] < v_hi) & (df[queryName] > v_low)]
    return df_filtered


def getHistogram(df, queryName, nbins=100, title=""):
    s = df[queryName]
    ax = s.plot.hist(alpha=0.7, bins=nbins)
    mean, std, count = s.describe().values[1], s.describe(
    ).values[2], s.describe().values[0]
    textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}".format(mean, std, count)
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.7)
    ax.text(0.80,
            0.95,
            textstr,
            transform=ax.transAxes,
            fontsize=12,
            verticalalignment='top',
            bbox=props)
    ax.set_title("Histogram of {} {}".format(queryName, title))
    plt.show()


def getFilteredHistogram(df, queryName, filter, nbins=100, title=""):
    df.hist(column=queryName, bins=nbins, by=filter)
    plt.suptitle("Histograms of {} grouped by {} {}".format(
        queryName, filter, title))
    plt.ylabel("Frequency")
    plt.show()


class MuonDataFrame:
    def __init__(self, path):
        self.events_df = pd.read_feather(path, use_threads=True)
        self.nbins = 150
        self.quant_query_terms = [
            'deadtime', 'TDC_L1_L', 'TDC_L1_R', 'TDC_L2_L', 'TDC_L2_R',
            'L1_asym', 'L2_asym', 'L1_TDC_sum', 'L2_TDC_sum', 'L1_TDC_diff',
            'L2_TDC_diff'
        ]
        self.query_terms = [
            'event_num', 'event_time', 'ADC', 'TDC', 'numChannelsRead'
        ] + self.quant_query_terms
        self.generateMultipleTDCHitData()

    def show(self):
        return self.events_df
        # print(self.events_df)

    def lookAt(self, query_term):
        return self.events_df[query_term]
        # print(self.events_df[query_term])

    def removeNoTDCEvents(self):
        self.events_df = self.events_df[~self.events_df["TDC"].isnull()]

    def summary(self):
        return self.events_df.info()
        # print(self.events_df.info())

    def generateMultipleTDCHitData(self):
        # self.events_df[""]
        num_tdc_read = self.events_df["TDC"].values
        # tdc_hits = dict()  # key = hits , value = [0_hit, 1_hit, 3_hit, 4_hit]
        tdc_hits = []
        for event in num_tdc_read:
            if event == None:
                tdc_hits.append([0, 0, 0, 0])
            else:
                tdc_hits.append(self.calculateTDCHits(event))
        self.events_df["TDC_hit_num"] = tdc_hits

    def getMultipleTDCHitReport(self):
        # print(self.events_df["TDC_hit_num"].describe())
        # print(self.events_df["TDC_hit_num"].values.tolist())
        val = self.events_df["TDC_hit_num"].values.tolist()
        df1 = pd.DataFrame(val,
                           index=self.events_df.index,
                           columns=["Ch0", "Ch1", "Ch3", "Ch4"])
        fig = plt.figure(figsize=(9, 7))

        plt.suptitle("Multihit TDC Event Breakdown")
        plt.subplot(2, 2, 1)
        df1["Ch0"].plot.hist(bins=10)
        plt.title("Channel 0")
        plt.ylabel("Number of Events")

        plt.subplot(2, 2, 2)
        df1["Ch1"].plot.hist(bins=10)
        plt.title("Channel 1")

        plt.subplot(2, 2, 3)
        df1["Ch3"].plot.hist(bins=10)
        plt.title("Channel 3")

        plt.subplot(2, 2, 4)
        df1["Ch4"].plot.hist(bins=10)
        plt.title("Channel 4")
        plt.xlabel("Number of TDC Hit Per Event")
        plt.show()
        # df1["Ch0"].plot.hist(bins=10)
        # df1["Ch1"].plot.hist(bins=10)
        # df1["Ch3"].plot.hist(bins=10)
        # df1["Ch4"].plot.hist(bins=10)
        # plt.show()

    def calculateTDCHits(self, event):
        zero_c = 0
        one_c = 0
        three_c = 0
        four_c = 0
        for i in event:
            if i[0] == 0:
                zero_c += 1
            elif i[0] == 1:
                one_c += 1
            elif i[0] == 3:
                three_c += 1
            elif i[0] == 4:
                four_c += 1

        return [zero_c, one_c, three_c, four_c]

    """
    # conditions : ("query_term operation value","query_term operation value","and/or operator")
    """

    def getHistogram(self, queryName, nbins=100, title=""):
        s = self.events_df[queryName]
        ax = s.plot.hist(alpha=0.7, bins=nbins)
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}".format(
            mean, std, count)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.7)
        ax.text(0.80,
                0.95,
                textstr,
                transform=ax.transAxes,
                fontsize=12,
                verticalalignment='top',
                bbox=props)
        ax.set_title("Histogram of {} {}".format(queryName, title))
        plt.show()

    def getKDE(self, queryName, nbins=100):
        s = self.events_df[queryName].to_numpy()
        s = pd.Series(s)
        ax = s.plot.kde()
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}".format(
            mean, std, count)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax.text(0.80,
                0.95,
                textstr,
                transform=ax.transAxes,
                fontsize=14,
                verticalalignment='top',
                bbox=props)
        ax.set_title("Probability Density of {}".format(queryName))
        plt.show()

    def getFilteredHistogram(self, queryName, filter, nbins=100, title=""):
        self.events_df.hist(column=queryName, bins=nbins, by=filter)
        plt.suptitle("Histograms of {} grouped by {} {}".format(
            queryName, filter, title))
        plt.ylabel("Frequency")
        plt.show()

    def getComparableHistogram(self, queries, nbins=100, title=""):
        s = pd.DataFrame(columns=queries)
        s = s.fillna(0)  # with 0s rather than NaNs
        for query in queries:
            s[query] = self.events_df[query]
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

    def getFilteredEvents(self, conditions):
        df = self.events_df
        numConditions = len(conditions)
        if numConditions == 1:
            return conditionParser_single(self.events_df, conditions)
        else:
            df1 = conditionParser_multiple(self.events_df, conditions[0])
            df2 = conditionParser_multiple(self.events_df, conditions[1])
            main_op = conditions[2]
            if main_op == "&":
                intersection = df1[['event_num'
                                    ]].merge(df2[['event_num'
                                                  ]]).drop_duplicates()
                res = pd.concat(
                    [df1.merge(intersection),
                     df2.merge(intersection)])
                # print(res)
            else:
                res = pd.concat([df1, df2])
                # print(res)
            return res

    def dropna(arr, *args, **kwarg):
        assert isinstance(arr, np.ndarray)
        dropped = pd.DataFrame(arr).dropna(*args, **kwarg).values
        if arr.ndim == 1:
            dropped = dropped.flatten()
        return dropped

    def getPlot(self, query, title=""):
        self.events_df[query].plot()
        plt.xlabel("Event Number")
        plt.ylabel(str(query))
        plt.title("Plot of {} event series {}".format(query, title))
        plt.show()

    def getScatterPlot(self, queries, title=""):
        plt.scatter(self.events_df[queries[0]].values,
                    self.events_df[queries[1]].values)
        plt.xlabel(str(queries[0]))
        plt.ylabel(str(queries[1]))
        plt.title("Scatter Plot of {} against {} {}".format(
            queries[0], queries[1], title))
        plt.show()

    def get3DScatterPlot(self, queries, title=""):
        self.events_df.plot.scatter(x=queries[0],
                                    y=queries[1],
                                    c=queries[2],
                                    colormap='viridis')
        plt.title(title)
        plt.show()

    def getEventInfo(self, eventNum):
        if isinstance(eventNum, int):
            df = self.events_df.loc[self.events_df["event_num"] == eventNum]
        elif isinstance(eventNum, list):
            df = self.events_df[self.events_df['event_num'].between(
                eventNum[0], eventNum[1])]
        return df
        # print(df)

    def getStats(self, queryName):
        s = self.events_df[queryName]
        return s.describe()
        # print(s.describe())

    def removeOutliers(self):
        for queryName in self.quant_query_terms:
            q_low = self.events_df[queryName].quantile(0.01)
            q_hi = self.events_df[queryName].quantile(0.99)
            self.events_df = self.events_df[
                (self.events_df[queryName] < q_hi)
                & (self.events_df[queryName] > q_low)]

    # @staticmethod

    def getTrimmedHistogram(self, queryName, numStd, nbins=100):
        df_filtered = scrubbedDataFrame(self.events_df, queryName, numStd)
        getHistogram(df_filtered, queryName, nbins,
                     "(Events within {} std dev)".format(numStd))

    def getTrimmed2DHistogram(df, queryName, numStd, nbins=100):
        pass

    def getTrimmedFilteredHistogram(self, queryName, numStd, nbins=100):
        df_filtered = scrubbedDataFrame(self.events_df, queryName, numStd)
        getFilteredHistogram(df_filtered,
                             queryName,
                             nbins,
                             title="(Events within {} std dev)".format(numStd))

    def getTrimmedComparableHistogram(self, queries, numStd, nbins=100):
        s = pd.DataFrame(columns=queries)
        s = s.fillna(0)  # with 0s rather than NaNs
        for query in queries:
            s[query] = scrubbedDataFrame(self.events_df, query, numStd)[query]
        ax = s.plot.hist(alpha=0.7, bins=nbins)
        plt.title("Histogram of {} (Events within {} std dev)".format(
            str(queries), numStd))
        plt.show()
