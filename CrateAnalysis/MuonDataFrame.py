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
    - Methods for generating report (pdf)
    - pd.HDFStore method
    - Vectorize all DF columns
    - Use of numba
    - Use of evals when possible
        - Methods for all Plots
            - histo of layers hit
            - histo of tdc hits per event
            - ADC
            - add histo info on graph
            - method for histo individual layer operations/assymetry
            - scaler histo of all elements in the list
    - Parallelize the following tasks:
        - Generate Report
        - Make a copy of this new DF and save it as a .ftr with new name corresponding to decision D1
    - Event Display/Tracking
    - Imaging
"""

import feather
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
import os
# import numba
import itertools
from collections import Counter
from collections import OrderedDict
from collections import defaultdict
from multiprocessing import Pool
from pandas_profiling import ProfileReport
from Histo2d import Histo2D
"""
# Default Query Terms:
'event_num', 'event_time', 'deadtime', 'ADC', 'TDC', 'Scaler'
"""


def parallelize_dataframe(df, func, path, n_cores=2):
    df_split = np.array_split(df, n_cores)
    pool = Pool(n_cores)
    df = pd.concat(pool.map(func, df_split))
    pool.close()
    pool.join()
    feather.write_dataframe(df, path)
    return df


def remove_if_first_index(l):
    return [
        item for index, item in enumerate(l)
        if item[0] not in [value[0] for value in l[0:index]]
    ]


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
        try:
            df = df[df[qt] == float(val)]
            print(df[df[qt] == float(val)])
        except:
            df = df[df[qt] == val]
            print(df[df[qt] == val])
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


def getHistogram(df, queryName, title="", nbins=100):
    s = df[queryName]
    ax = s.plot.hist(alpha=0.7, bins=nbins, histtype='step')
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
    df.hist(column=queryName, bins=nbins, by=filter, histtype='step')
    plt.suptitle("Histograms of {} grouped by {} {}".format(
        queryName, filter, title))
    plt.ylabel("Frequency")
    plt.show()


class MuonDataFrame:
    def __init__(self, path, d1="last", isNew=True):
        """
        Initialize the MuonDataFrame

        :param path [string]: path to the data file
        :param d1 [string]: type of decision to be made on multiTDC events (acceptable terms are "last", "first", "min", and "max")
                            default value = last
        """

        self.events_df = pd.read_feather(path, use_threads=True)
        self.nbins = 150
        self.quant_query_terms = []
        self.default_query_terms = [
            'event_num', 'event_time', 'deadtime', 'ADC', 'TDC', 'Scaler'
        ]
        self.query_terms = self.default_query_terms + self.quant_query_terms
        self.d1 = d1
        self.newFileName = path.split(".")[0].split("/")[0] + "/" + path.split(
            ".")[0].split("/")[1] + "_analyzed.ftr"
        if isNew:
            self.events_df = self.getDataFrame(
                pd.read_feather(path, use_threads=True))
        else:
            self.events_df = pd.read_feather(self.newFileName,
                                             use_threads=True)

    def generateReport(self):
        profile = ProfileReport(self.events_df,
                                title='Prototype 1B Profiling Report',
                                explorative=True)
        profile.to_file("mdf.html")

    def getAnaReport(self):
        # self.getDeadtimePlot()
        # self.getChannelPlots()
        # self.getChannelSumPlots()
        # self.getChannelDiffPlots()
        # self.getAssymetry1DPlots()
        # self.getNumLayersHitPlot()
        self.get2DHistogram()

    def getDeadtimePlot(self):
        self.getHistogram("deadtime")

    def getADCPlot(self):
        pass

    def getNumLayersHitPlot(self):
        self.getHistogram("numLHit", title="(Number of Layers Hit Per Event)")

    def getChannelPlots(self):
        fig, axes = plt.subplots(nrows=2, ncols=4)
        self.events_df['L1'].plot(ax=axes[0, 0],
                                  title="Ch0",
                                  kind="hist",
                                  histtype='step')
        self.events_df['R1'].plot(ax=axes[1, 0],
                                  title="Ch1",
                                  kind="hist",
                                  histtype='step')
        self.events_df['L2'].plot(ax=axes[0, 1],
                                  title="Ch3",
                                  kind="hist",
                                  histtype='step')
        self.events_df['R2'].plot(ax=axes[1, 1],
                                  title="Ch4",
                                  kind="hist",
                                  histtype='step')
        self.events_df['L3'].plot(ax=axes[0, 2],
                                  title="Ch6",
                                  kind="hist",
                                  histtype='step')
        self.events_df['R3'].plot(ax=axes[1, 2],
                                  title="Ch7",
                                  kind="hist",
                                  histtype='step')
        self.events_df['L4'].plot(ax=axes[0, 3],
                                  title="Ch9",
                                  kind="hist",
                                  histtype='step')
        self.events_df['R4'].plot(ax=axes[1, 3],
                                  title="Ch10",
                                  kind="hist",
                                  histtype='step')
        plt.show()

    def getChannelSumPlots(self):
        df = pd.DataFrame()
        fig, axes = plt.subplots(nrows=1, ncols=4)
        self.events_df['sumL1'].plot(ax=axes[0], title="L1+R1", kind="hist")
        self.events_df['sumL2'].plot(ax=axes[1], title="L2+R2", kind="hist")
        self.events_df['sumL3'].plot(ax=axes[2], title="L3+R3", kind="hist")
        self.events_df['sumL4'].plot(ax=axes[3], title="L4+R4", kind="hist")
        plt.show()

    def getChannelDiffPlots(self):
        df = pd.DataFrame()
        fig, axes = plt.subplots(nrows=1, ncols=4)
        self.events_df['diffL1'].plot(ax=axes[0], title="L1-R1", kind="hist")
        self.events_df['diffL2'].plot(ax=axes[1], title="L2-R2", kind="hist")
        self.events_df['diffL3'].plot(ax=axes[2], title="L3-R3", kind="hist")
        self.events_df['diffL4'].plot(ax=axes[3], title="L4-R4", kind="hist")
        plt.show()

    def getAssymetry1DPlots(self):
        df = pd.DataFrame()
        fig, axes = plt.subplots(nrows=4, ncols=1)
        self.events_df['asymL1'].plot(ax=axes[0], title="L1_asym", kind="hist")
        self.events_df['asymL2'].plot(ax=axes[1], title="L2_asym", kind="hist")
        self.events_df['asymL3'].plot(ax=axes[2], title="L3_asym", kind="hist")
        self.events_df['asymL4'].plot(ax=axes[3], title="L4_asym", kind="hist")
        plt.show()

    def getDataFrame(self, df):
        return parallelize_dataframe(df, self.completeDataFrame,
                                     self.newFileName)

    def completeDataFrame(self, df):
        df['L1'] = self.getTDC(df['TDC'].to_numpy(), 0)
        df['R1'] = self.getTDC(df['TDC'].values, 1)
        df['L2'] = self.getTDC(df['TDC'].values, 3)
        df['R2'] = self.getTDC(df['TDC'].values, 4)
        df['L3'] = self.getTDC(df['TDC'].values, 6)
        df['R3'] = self.getTDC(df['TDC'].values, 7)
        df['L4'] = self.getTDC(df['TDC'].values, 9)
        df['R4'] = self.getTDC(df['TDC'].values, 10)
        df['sumL1'] = df.eval('L1 + R1')
        df['sumL2'] = df.eval('L2 + R2')
        df['sumL3'] = df.eval('L3 + R3')
        df['sumL4'] = df.eval('L4 + R4')
        df['diffL1'] = df.eval('L1 - R1')
        df['diffL2'] = df.eval('L2 - R2')
        df['diffL3'] = df.eval('L3 - R3')
        df['diffL4'] = df.eval('L4 - R4')
        df['asymL1'] = df.eval('diffL1 / sumL1')
        df['asymL2'] = df.eval('diffL2 / sumL2')
        df['asymL3'] = df.eval('diffL3 / sumL3')
        df['asymL4'] = df.eval('diffL4 / sumL4')
        df['numLHit'] = self.removeMultiHits(df['TDC'].values)
        return df

    def getTDC(self, event, chNum):
        tdcs = []
        for ev in event:
            tdc = 0
            tdcVals = []
            if ev != None:
                for i in ev:
                    if chNum in i:
                        tdcVals.append(i[1])
                tdc = self.getCorrectTDC(tdcVals)
            else:
                tdc = None
            tdcs.append(tdc)
        return tdcs

    def removeMultiHits(self, event):
        counts = []
        for ev in event:
            if ev != None:
                counts.append(
                    len([
                        next(t)
                        for _, t in itertools.groupby(ev, lambda x: x[0])
                    ]))
            else:
                counts.append(0)
        return counts

    def getCorrectTDC(self, tdcs):
        if len(tdcs) == 1:
            return tdcs[0]
        elif len(tdcs) == 0:
            return None
        else:
            if self.d1 == "last":
                # print("len(tdcs) : {}".format(len(tdcs)))
                return tdcs[-1]
            elif self.d1 == "first":
                return tdcs[0]
            elif self.d1 == "min":
                return min(tdcs)
            elif self.d1 == "max":
                return max(tdcs)

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
        criteria = self.d1
        num_tdc_read = self.events_df["TDC"].values
        tdc_hits = []
        tdc_event = []
        for event in num_tdc_read:
            if event == None:
                tdc_hits.append([0, 0, 0, 0])
                tdc_event.append(None)
            else:
                tdc_list, ev_list = self.calculateTDCHits(event, criteria)
                tdc_event.append(ev_list)
                tdc_hits.append(tdc_list)
        self.events_df["TDC_hit_num"] = tdc_hits
        self.events_df["TDC_Ana"] = tdc_event
        # self.generateNumChannelsReadData()
        # self.generateTDCAnalyzedData()

    def createTDCValues(self, tdc_hits, event, criteria):
        if criteria == "last":
            ev = list(OrderedDict(event).items())
        elif criteria == "first":
            ev = remove_if_first_index(event)
        elif criteria == "max":
            ev = list(dict(list(event), key=lambda v: int(v[1])).items())
            ev.pop()
        elif criteria == "min":
            d = defaultdict(list)
            for name, num in event:
                d[name].append(num)
            ev = list(zip(d, map(min, d.values())))
        return ev

    def calculateTDCHits(self, event, criteria):
        zero_c = 0
        one_c = 0
        three_c = 0
        four_c = 0
        tdc_event = []
        for i in event:
            if i[0] == 0:
                zero_c += 1
            elif i[0] == 1:
                one_c += 1
            elif i[0] == 3:
                three_c += 1
            elif i[0] == 4:
                four_c += 1
        tdc_hit = [zero_c, one_c, three_c, four_c]
        ev = self.createTDCValues(tdc_hit, event, criteria)
        return tdc_hit, ev

    def getHistogram(
        self,
        queryName,
        title="",
        nbins=100,
    ):
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

    def get2DHistogram(self, nbins=250):
        # L1asym = lambda eventRecord: eventRecord["L2_asym"]
        # L2asym = lambda eventRecord: eventRecord["L4_asym"]
        L1asym = lambda eventRecord: eventRecord["L2"]
        L2asym = lambda eventRecord: eventRecord["R2"]
        hitMap = Histo2D("hitMap", "Hit Map", "Asymmetry in X", nbins, -160.0,
                         160.0, L1asym, "Asymmetry in Y", nbins, -160.0, 160.0,
                         L2asym)
        for index, row in self.events_df.iterrows():
            hitMap.processEvent(row)
        hitMap.endjob()

    # def get2DHistogram(df, queries, nbibs=1000, title=""):
    # x = df[queries[0]].to_numpy()
    # y = df[queries[1]].to_numpy()
    # x = dropna(x)
    # y = dropna(y)
    # while (len(x) != len(y)):
    # if (len(x) > len(y)):
    # x = x[:-1]
    # else:
    # y = y[:-1]
    # plt.hist2d(x, y)
    # plt.title("2D Histogram of {} against {} {}".format(
    # queries[0], queries[1], title))
    # plt.show()

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
        ax = s.plot.hist(alpha=0.7, bins=nbins, histtype='step')
        plt.title("Histogram of {} (Events within {} std dev)".format(
            str(queries), numStd))
        plt.show()
