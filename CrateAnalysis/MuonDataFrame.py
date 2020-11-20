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
from matplotlib.backends.backend_pdf import PdfPages
import itertools
import datetime
from collections import Counter
from collections import OrderedDict
from collections import defaultdict
from multiprocessing import Pool
from pandas_profiling import ProfileReport
from Histo2d import Histo2D
#from muondataframegui import show
from PIL import Image
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
from multipledispatch import dispatch

np.warnings.filterwarnings('ignore')


# CODE FOR COUNTING
def append_pdf(input, output):
    [
        output.addPage(input.getPage(page_num))
        for page_num in range(input.numPages)
    ]


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


def getHistogram(df, queryName, title="", nbins=200):
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


def getFilteredHistogram(df, queryName, filter, nbins=200, title=""):
    df.hist(column=queryName, bins=nbins, by=filter, histtype='step')
    plt.suptitle("Histograms of {} grouped by {} {}".format(
        queryName, filter, title))
    plt.ylabel("Frequency")
    plt.show()


class MuonDataFrame:
    def __init__(self, path, isNew, d1="last"):
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
            'event_num', 'event_time', 'deadtime', 'ADC', 'TDC', 'SCh0',
            'SCh1', 'SCh2', 'SCh3', 'SCh4', 'SCh5', 'SCh6', 'SCh7', 'SCh8',
            'SCh9', 'SCh10', 'SCh11', 'l1hit', 'l2hit', 'l3hit', 'l4hit',
            'r1hit', 'r2hit', 'r3hit', 'r4hit'
        ]
        self.query_terms = self.default_query_terms + self.quant_query_terms
        self.d1 = d1
        self.pdfName = path.split(".")[0].split("/")[1] + ".pdf"
        self.pdfList = []
        self.runNum = self.pdfName.split(".")[0].split("_")[-1]
        self.imagelist = []
        self.newFileName = path.split(".")[0].split("/")[0] + "/" + path.split(
            ".")[0].split("/")[1] + "_analyzed.ftr"
        if isNew:
            self.events_df = self.getDataFrame(
                pd.read_feather(path, use_threads=True))
        else:
            self.events_df = pd.read_feather(self.newFileName,
                                             use_threads=True)

        self.og_df = self.events_df
        self.total = len(self.og_df.index)

    def reload(self):
        self.events_df = self.og_df

    def generateReport(self):
        profile = ProfileReport(self.events_df,
                                title='Prototype 1B Profiling Report',
                                explorative=True)
        profile.to_file("mdf.html")

    def generateAnaReport(self, pdfName=""):
        if pdfName == "":
            pdfName = self.pdfName
        with PdfPages(pdfName) as pdf:
            firstPage = plt.figure(figsize=(11.69, 8.27))
            firstPage.clf()
            txt = 'Analysis of Run: ' + self.runNum + '\n Time Created: ' + str(
                datetime.datetime.today())
            firstPage.text(0.5,
                           0.5,
                           txt,
                           transform=firstPage.transFigure,
                           size=24,
                           ha="center")
            pdf.savefig()
            plt.close()
            self.getDeadtimePlot(pdf=True)
            pdf.savefig()
            plt.close()
            self.getChannelStatusPlot(pdf=True)
            pdf.savefig()
            plt.close()
            self.getChannelPlots(pdf=True)
            pdf.savefig()
            plt.close()
            self.getChannelSumPlots(pdf=True)
            pdf.savefig()
            plt.close()
            self.getChannelDiffPlots(pdf=True)
            pdf.savefig()
            plt.close()
            self.getAsymmetry1DPlots(pdf=True)
            pdf.savefig()
            plt.close()
            self.getNumLayersHitPlot(pdf=True)
            pdf.savefig()
            plt.close()
            self.getScalerPlots_header(pdf=True)
            pdf.savefig()
            plt.close()
            self.getScalerPlots_channels(pdf=True)
            pdf.savefig()
            plt.close()

            d = pdf.infodict()
            d['Title'] = 'Prototype 1B Data Analysis'
            d['Author'] = 'Sadman Ahmed Shanto'
            d['Subject'] = 'Storing Analysis Results'
            d['Keywords'] = 'Muon APDL'
            d['CreationDate'] = datetime.datetime(2009, 11, 13)
            d['ModDate'] = datetime.datetime.today()

        self.allLayerCorrelationPlots(pdfv=True,
                                      nbins=1000,
                                      title="(High Binning)")
        self.getFingerPlots(pdfv=True)
        self.allLayerCorrelationPlots(pdfv=True, nbins=22, title="(Bins = 22)")
        self.convertPNG2PDF()
        self.createOnePDF(pdfName)
        # self.mergePDF(pdfName)
        print("The report file {} has been created.".format(pdfName))

    def mergePDF(self, pdfName):
        for i in self.pdfList:
            os.remove(i + ".png")
        self.pdfList = [i + ".pdf" for i in self.pdfList]
        self.pdfList.insert(0, pdfName)
        output = PdfFileWriter()
        for i in self.pdfList:
            append_pdf(PdfFileReader(file(i, "rb")), output)
        output.write(file(pdfName, "wb"))

    def createOnePDF(self, pdfName):
        for i in self.pdfList:
            os.remove(i + ".png")
        self.pdfList = [i + ".pdf" for i in self.pdfList]
        self.pdfList.insert(0, pdfName)

        merger = PdfFileMerger()
        for pdf in self.pdfList:
            merger.append(PdfFileReader(pdf), 'rb')
        with open(pdfName, 'wb') as new_file:
            merger.write(new_file)

        # with open(output, 'wb') as f:
        # merger.write(pdfName)
        merger.close()
        self.pdfList.pop(0)
        for i in self.pdfList:
            os.remove(i)

    def convertPNG2PDF(self):
        for i in self.pdfList:
            image1 = Image.open(i + ".png")
            im1 = image1.convert('RGB')
            im1.save(i + ".pdf")

    # def gui(self):
    # show(self.events_df, settings={'block': True})
    # show(self.events_df)

    def getAnaReport(self):
        self.getDeadtimePlot()
        self.getChannelPlots()
        self.getChannelSumPlots()
        self.getChannelDiffPlots()
        self.getAsymmetry1DPlots()
        self.getNumLayersHitPlot()
        self.allLayerCorrelationPlots(nbins=1000)
        self.allLayerCorrelationPlots(nbins=22)
        self.getScalerPlots_header()
        self.getScalerPlots_channels()

    def getScalerPlots_channels(self, pdf=False, amount=2):
        fig, axes = plt.subplots(nrows=4, ncols=2)
        plt.suptitle("Histogram of Scaler Readings (Ch 4 - 11)")
        ax0, ax1, ax2, ax3, ax4, ax5, ax6, ax7 = axes.flatten()
        s = self.events_df['SCh4']
        nbins = round(max(s.values) - min(s.values) // amount)
        ax0.hist(self.events_df['SCh4'], nbins, histtype='step')
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}".format(
            mean, std, count, nbins)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax0.text(0.80,
                 0.95,
                 textstr,
                 transform=ax0.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        ax0.set_title('Ch4 (1L)')
        s = self.events_df['SCh5']
        nbins = (max(s.values) - min(s.values)) // amount
        ax1.hist(self.events_df['SCh5'], nbins, histtype='step')
        ax1.set_title('Ch5 (1R)')
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}".format(
            mean, std, count, nbins)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax1.text(0.80,
                 0.95,
                 textstr,
                 transform=ax1.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        s = self.events_df['SCh6']
        nbins = (max(s.values) - min(s.values)) // amount
        ax2.hist(self.events_df['SCh6'], nbins, histtype='step')
        ax2.set_title('Ch6 (2L)')
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}".format(
            mean, std, count, nbins)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax2.text(0.80,
                 0.95,
                 textstr,
                 transform=ax2.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        s = self.events_df['SCh7']
        nbins = (max(s.values) - min(s.values)) // amount
        ax3.hist(self.events_df['SCh7'], nbins, histtype='step')
        ax3.set_title('Ch7 (2R)')
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}".format(
            mean, std, count, nbins)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax3.text(0.80,
                 0.95,
                 textstr,
                 transform=ax3.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        s = self.events_df['SCh8']
        nbins = (max(s.values) - min(s.values)) // amount
        ax4.hist(self.events_df['SCh8'], nbins, histtype='step')
        ax4.set_title('Ch8 (3L)')
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}".format(
            mean, std, count, nbins)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax4.text(0.80,
                 0.95,
                 textstr,
                 transform=ax4.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        s = self.events_df['SCh9']
        nbins = (max(s.values) - min(s.values)) // amount
        ax5.hist(self.events_df['SCh9'], nbins, histtype='step')
        ax5.set_title('Ch9 (3R)')
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}".format(
            mean, std, count, nbins)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax5.text(0.80,
                 0.95,
                 textstr,
                 transform=ax5.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        s = self.events_df['SCh10']
        nbins = (max(s.values) - min(s.values)) // amount
        ax6.hist(self.events_df['SCh10'], nbins, histtype='step')
        ax6.set_title('Ch10 (4L)')
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}".format(
            mean, std, count, nbins)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax6.text(0.80,
                 0.95,
                 textstr,
                 transform=ax6.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        s = self.events_df['SCh11']
        nbins = (max(s.values) - min(s.values)) // amount
        ax7.hist(self.events_df['SCh11'], nbins, histtype='step')
        ax7.set_title('Ch11 (4R)')
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}".format(
            mean, std, count, nbins)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax7.text(0.80,
                 0.95,
                 textstr,
                 transform=ax7.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        fig.tight_layout()
        if not pdf:
            plt.show()
        else:
            return fig

    def getScalerPlots_header(self, pdf=False, amount=3):
        fig, axes = plt.subplots(nrows=4, ncols=1)
        plt.suptitle("Histogram of Scaler Readings (Ch 0 - 3)")
        ax0, ax1, ax2, ax3 = axes.flatten()
        s = self.events_df['SCh0']
        ax0.hist(self.events_df['SCh0'], 200, histtype='step')
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\n".format(
            mean, std, count)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax0.text(0.80,
                 0.95,
                 textstr,
                 transform=ax0.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        ax0.set_title('Ch0')
        s = self.events_df['SCh1']
        nbins = (max(s.values) - min(s.values)) // amount
        ax1.hist(self.events_df['SCh1'], nbins, histtype='step')
        ax1.set_title('Ch1')
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}".format(
            mean, std, count, nbins)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax1.text(0.80,
                 0.95,
                 textstr,
                 transform=ax1.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        s = self.events_df['SCh2']
        nbins = (max(s.values) - min(s.values)) // amount
        ax2.hist(self.events_df['SCh2'], nbins, histtype='step')
        ax2.set_title('Ch2')
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}".format(
            mean, std, count, nbins)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax2.text(0.80,
                 0.95,
                 textstr,
                 transform=ax2.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        s = self.events_df['SCh3']
        ax3.hist(self.events_df['SCh3'], 200, histtype='step')
        ax3.set_title('Ch3')
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\n".format(
            mean, std, count)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax3.text(0.80,
                 0.95,
                 textstr,
                 transform=ax3.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        fig.tight_layout()
        if not pdf:
            plt.show()
        else:
            return fig

    def getAsymPlotFig(self, term1, term2):
        xmin = -0.65
        xmax = 0.65
        ymin = -0.65
        ymax = 0.65
        nbins = 1000
        x = self.get2DHistogram(self.events_df[term1].values,
                                self.events_df[term2].values, "L1 vs L2",
                                "Asymmetry in X", "Asymmetry in Y", xmin, xmax,
                                ymin, ymax, nbins, True)
        print(x)
        return x

    def allLayerCorrelationPlots(self, pdfv=False, nbins=1000, title=""):
        xmin = -0.65
        xmax = 0.65
        ymin = -0.65
        ymax = 0.65
        self.get2DHistogram(self.events_df['asymL1'].values,
                            self.events_df['asymL2'].values,
                            "{} Asymmetry: L1 vs L2".format(title),
                            "Asymmetry in X",
                            "Asymmetry in Y",
                            xmin,
                            xmax,
                            ymin,
                            ymax,
                            nbins,
                            pdf=pdfv)
        self.get2DHistogram(self.events_df['asymL3'].values,
                            self.events_df['asymL4'].values,
                            "{} Asymmetry: L3 vs L4".format(title),
                            "Asymmetry in X",
                            "Asymmetry in Y",
                            xmin,
                            xmax,
                            ymin,
                            ymax,
                            nbins,
                            pdf=pdfv)
        self.get2DHistogram(self.events_df['asymL1'].values,
                            self.events_df['asymL3'].values,
                            "{} Asymmetry: L1 vs L3".format(title),
                            "Asymmetry in X",
                            "Asymmetry in Y",
                            xmin,
                            xmax,
                            ymin,
                            ymax,
                            nbins,
                            pdf=pdfv)
        self.get2DHistogram(self.events_df['asymL2'].values,
                            self.events_df['asymL4'].values,
                            "{} Asymmetry: L2 vs L4".format(title),
                            "Asymmetry in X",
                            "Asymmetry in Y",
                            xmin,
                            xmax,
                            ymin,
                            ymax,
                            nbins,
                            pdf=pdfv)
        self.get2DHistogram(self.events_df['asymL1'].values,
                            self.events_df['asymL4'].values,
                            "{} Asymmetry: L1 vs L4".format(title),
                            "Asymmetry in X",
                            "Asymmetry in Y",
                            xmin,
                            xmax,
                            ymin,
                            ymax,
                            nbins,
                            pdf=pdfv)
        self.get2DHistogram(self.events_df['asymL2'].values,
                            self.events_df['asymL3'].values,
                            "{} Asymmetry: L2 vs L3".format(title),
                            "Asymmetry in X",
                            "Asymmetry in Y",
                            xmin,
                            xmax,
                            ymin,
                            ymax,
                            nbins,
                            pdf=pdfv)

    def getFingerPlots(self, pdfv=False):
        xmin = 0
        xmax = 300
        ymin = -0
        ymax = 300
        nbins = 250
        x = "L1"
        y = "R1"
        self.get2DHistogram(self.events_df[x].values,
                            self.events_df[y].values,
                            "{} vs {}".format(x, y),
                            x,
                            y,
                            xmin,
                            xmax,
                            ymin,
                            ymax,
                            nbins,
                            pdf=pdfv)
        x = "L2"
        y = "R2"
        self.get2DHistogram(self.events_df[x].values,
                            self.events_df[y].values,
                            "{} vs {}".format(x, y),
                            x,
                            y,
                            xmin,
                            xmax,
                            ymin,
                            ymax,
                            nbins,
                            pdf=pdfv)
        x = "L3"
        y = "R3"
        self.get2DHistogram(self.events_df[x].values,
                            self.events_df[y].values,
                            "{} vs {}".format(x, y),
                            x,
                            y,
                            xmin,
                            xmax,
                            ymin,
                            ymax,
                            nbins,
                            pdf=pdfv)
        x = "L4"
        y = "R4"
        self.get2DHistogram(self.events_df[x].values,
                            self.events_df[y].values,
                            "{} vs {}".format(x, y),
                            x,
                            y,
                            xmin,
                            xmax,
                            ymin,
                            ymax,
                            nbins,
                            pdf=pdfv)

    def getDeadtimePlot(self, pdf=False):
        x = self.getHistogram("deadtime", pdf=pdf)
        return x

    def getChannelStatusPlot(self, pdf=False):
        l1_p = list(self.og_df['l1hit'].values).count(1)
        l2_p = list(self.og_df['l2hit'].values).count(1)
        l3_p = list(self.og_df['l3hit'].values).count(1)
        l4_p = list(self.og_df['l4hit'].values).count(1)

        r1_p = list(self.og_df['r1hit'].values).count(1)
        r2_p = list(self.og_df['r2hit'].values).count(1)
        r3_p = list(self.og_df['r3hit'].values).count(1)
        r4_p = list(self.og_df['r4hit'].values).count(1)

        yvals = [
            l1_p / self.total, l2_p / self.total, l3_p / self.total,
            l4_p / self.total, r1_p / self.total, r2_p / self.total,
            r3_p / self.total, r4_p / self.total
        ]
        yvals = [i * 100 for i in yvals]
        xvals = [
            "Ch 0", "Ch 1", "Ch 3", "Ch 4", "Ch 6", "Ch 7", "Ch 9", "Ch 10"
        ]
        barlist = plt.bar(xvals, yvals)
        barlist[0].set_color('r')
        barlist[1].set_color('r')
        barlist[4].set_color('r')
        barlist[5].set_color('r')
        plt.title("Percentage of Good Events")
        ax = barlist
        if not pdf:
            plt.show()
        else:
            return ax

    def getADCPlot(self):
        pass

    def getNumLayersHitPlot(self, pdf=False):
        x = self.getHistogram("numLHit",
                              title="(Number of Layers Hit Per Event)",
                              pdf=pdf)
        return x

    def getChannelPlots(self, pdf=False, nbins=200):
        fig, axes = plt.subplots(nrows=2, ncols=4)
        plt.suptitle("Histogram of All Individual Channels")
        ax0, ax1, ax2, ax3, ax4, ax5, ax6, ax7 = axes.flatten()
        ax0.hist(self.events_df['L1'], nbins, histtype='step')
        ax0.set_xlim([0, 200])
        s = self.events_df['L1']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}".format(
            mean, std, count)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax0.text(0.80,
                 0.95,
                 textstr,
                 transform=ax0.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        ax0.set_title('Ch0')
        ax1.hist(self.events_df['R1'], nbins, histtype='step')
        ax1.set_xlim([0, 200])
        ax1.set_title('Ch1')
        s = self.events_df['R1']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}".format(
            mean, std, count)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax1.text(0.80,
                 0.95,
                 textstr,
                 transform=ax1.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        ax2.hist(self.events_df['L2'], nbins, histtype='step')
        ax2.set_title('Ch3')
        ax2.set_xlim([0, 200])
        s = self.events_df['L2']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}".format(
            mean, std, count)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax2.text(0.80,
                 0.95,
                 textstr,
                 transform=ax2.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        ax3.hist(self.events_df['R2'], nbins, histtype='step')
        ax3.set_xlim([0, 200])
        ax3.set_title('Ch4')
        s = self.events_df['R2']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}".format(
            mean, std, count)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax3.text(0.80,
                 0.95,
                 textstr,
                 transform=ax3.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        ax4.hist(self.events_df['L3'], nbins, histtype='step')
        ax4.set_xlim([0, 200])
        ax4.set_title('Ch6')
        s = self.events_df['L3']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}".format(
            mean, std, count)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax4.text(0.80,
                 0.95,
                 textstr,
                 transform=ax4.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        ax5.hist(self.events_df['R3'], nbins, histtype='step')
        ax5.set_xlim([0, 200])
        ax5.set_title('Ch7')
        s = self.events_df['R3']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}".format(
            mean, std, count)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax5.text(0.80,
                 0.95,
                 textstr,
                 transform=ax5.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        ax6.hist(self.events_df['L4'], nbins, histtype='step')
        ax6.set_xlim([0, 200])
        ax6.set_title('Ch9')
        s = self.events_df['L4']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}".format(
            mean, std, count)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax6.text(0.80,
                 0.95,
                 textstr,
                 transform=ax6.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        ax7.hist(self.events_df['R4'], nbins, histtype='step')
        ax7.set_xlim([0, 200])
        ax7.set_title('Ch10')
        s = self.events_df['L2']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}".format(
            mean, std, count)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax7.text(0.80,
                 0.95,
                 textstr,
                 transform=ax7.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        fig.tight_layout()
        if not pdf:
            plt.show()
        else:
            return fig

    def getChannelSumPlots(self, pdf=False, amount=5):
        fig, axes = plt.subplots(nrows=4, ncols=1)
        xmin, xmax = 150, 250
        plt.suptitle("Histogram of Sum of Channels in their Respective Trays")
        ax0, ax1, ax2, ax3 = axes.flatten()
        nbins = len(self.events_df['sumL1']) // amount
        ovflow = ((xmax < self.events_df['sumL1'].values) |
                  (self.events_df['sumL1'].values < xmin)).sum()
        ax0.hist(self.events_df['sumL1'], bins=nbins, histtype='step')
        ax0.set_xlim([xmin, xmax])
        s = self.events_df['sumL1']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
            mean, std, count, nbins, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax0.text(0.90,
                 0.95,
                 textstr,
                 transform=ax0.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        ax0.set_title('Tray 1')
        nbins = len(self.events_df['sumL2']) // amount
        ovflow = ((xmax < self.events_df['sumL2'].values) |
                  (self.events_df['sumL2'].values < xmin)).sum()
        ax1.hist(self.events_df['sumL2'], nbins, histtype='step')
        ax1.set_xlim([xmin, xmax])
        ax1.set_title('Tray 2')
        s = self.events_df['sumL2']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
            mean, std, count, nbins, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax1.text(0.90,
                 0.95,
                 textstr,
                 transform=ax1.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        nbins = len(self.events_df['sumL3']) // amount
        ovflow = ((xmax < self.events_df['sumL3'].values) |
                  (self.events_df['sumL3'].values < xmin)).sum()
        ax2.hist(self.events_df['sumL3'], nbins, histtype='step')
        ax2.set_xlim([xmin, xmax])
        ax2.set_title('Tray 3')
        s = self.events_df['sumL3']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
            mean, std, count, nbins, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax2.text(0.90,
                 0.95,
                 textstr,
                 transform=ax2.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        nbins = len(self.events_df['sumL4']) // amount
        ovflow = ((xmax < self.events_df['sumL4'].values) |
                  (self.events_df['sumL4'].values < xmin)).sum()
        ax3.hist(self.events_df['sumL4'], nbins, histtype='step')
        ax3.set_xlim([xmin, xmax])
        ax3.set_title('Tray 4')
        s = self.events_df['sumL4']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
            mean, std, count, nbins, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax3.text(0.90,
                 0.95,
                 textstr,
                 transform=ax3.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        fig.tight_layout()
        if not pdf:
            plt.show()
        else:
            return fig

    def getChannelDiffPlots(self, pdf=False, amount=5):
        fig, axes = plt.subplots(nrows=4, ncols=1)
        xmin = -100
        xmax = 100
        plt.suptitle(
            "Histogram of Difference of Channels in their Respective Trays")
        nbins = len(self.events_df['diffL1']) // amount
        ovflow = ((xmax < self.events_df['diffL1'].values) |
                  (self.events_df['diffL1'].values < xmin)).sum()
        ax0, ax1, ax2, ax3 = axes.flatten()
        ax0.hist(self.events_df['diffL1'], nbins, histtype='step')
        ax0.set_xlim([xmin, xmax])
        s = self.events_df['diffL1']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
            mean, std, count, nbins, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax0.text(0.90,
                 0.95,
                 textstr,
                 transform=ax0.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        ax0.set_title('Tray 1')
        nbins = len(self.events_df['diffL2']) // amount
        ovflow = ((xmax < self.events_df['diffL2'].values) |
                  (self.events_df['diffL2'].values < xmin)).sum()
        ax1.hist(self.events_df['diffL2'], nbins, histtype='step')
        ax1.set_xlim([xmin, xmax])
        ax1.set_title('Tray 2')
        s = self.events_df['diffL2']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
            mean, std, count, nbins, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax1.text(0.90,
                 0.95,
                 textstr,
                 transform=ax1.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        nbins = len(self.events_df['diffL3']) // amount
        ovflow = ((xmax < self.events_df['diffL3'].values) |
                  (self.events_df['diffL3'].values < xmin)).sum()
        ax2.hist(self.events_df['diffL3'], nbins, histtype='step')
        ax2.set_xlim([xmin, xmax])
        ax2.set_title('Tray 3')
        s = self.events_df['diffL3']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
            mean, std, count, nbins, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax2.text(0.90,
                 0.95,
                 textstr,
                 transform=ax2.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        nbins = len(self.events_df['diffL4']) // amount
        ovflow = ((xmax < self.events_df['diffL4'].values) |
                  (self.events_df['diffL4'].values < xmin)).sum()
        ax3.hist(self.events_df['diffL4'], nbins, histtype='step')
        ax3.set_xlim([xmin, xmax])
        ax3.set_title('Tray 4')
        s = self.events_df['diffL4']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
            mean, std, count, nbins, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax3.text(0.90,
                 0.95,
                 textstr,
                 transform=ax3.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        fig.tight_layout()
        if not pdf:
            plt.show()
        else:
            return fig

    def getAsymmetry1DPlots(self, pdf=False, amount=5):
        fig, axes = plt.subplots(nrows=4, ncols=1)
        plt.suptitle("Histogram of Asymmetry of each Tray")
        ax0, ax1, ax2, ax3 = axes.flatten()
        xmin, xmax = -0.25, 0.25
        nbins = len(self.events_df['asymL1']) // amount
        ovflow = ((xmax < self.events_df['asymL1'].values) |
                  (self.events_df['asymL1'].values < xmin)).sum()
        ax0.hist(self.events_df['asymL1'], nbins, histtype='step')
        s = self.events_df['asymL1']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
            mean, std, count, nbins, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax0.text(0.90,
                 0.95,
                 textstr,
                 transform=ax0.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        ax0.set_xlim([xmin, xmax])
        ax0.set_title('Tray 1')
        nbins = len(self.events_df['asymL2']) // amount
        ovflow = ((xmax < self.events_df['asymL2'].values) |
                  (self.events_df['asymL2'].values < xmin)).sum()
        ax1.hist(self.events_df['asymL2'], nbins, histtype='step')
        ax1.set_xlim([xmin, xmax])
        ax1.set_title('Tray 2')
        s = self.events_df['asymL2']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
            mean, std, count, nbins, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax1.text(0.90,
                 0.95,
                 textstr,
                 transform=ax1.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        nbins = len(self.events_df['asymL3']) // amount
        ovflow = ((xmax < self.events_df['asymL3'].values) |
                  (self.events_df['asymL3'].values < xmin)).sum()
        ax2.hist(self.events_df['asymL3'], nbins, histtype='step')
        ax2.set_xlim([xmin, xmax])
        ax2.set_title('Tray 3')
        s = self.events_df['asymL3']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
            mean, std, count, nbins, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax2.text(0.90,
                 0.95,
                 textstr,
                 transform=ax2.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        nbins = len(self.events_df['asymL4']) // amount
        ovflow = ((xmax < self.events_df['asymL4'].values) |
                  (self.events_df['asymL4'].values < xmin)).sum()
        ax3.hist(self.events_df['asymL4'], nbins, histtype='step')
        ax3.set_xlim([xmin, xmax])
        ax3.set_title('Tray 4')
        s = self.events_df['asymL4']
        mean, std, count = s.describe().values[1], s.describe(
        ).values[2], s.describe().values[0]
        textstr = "Mean: {:0.3f}\nStd: {:0.3f}\nCount: {}\nBin: {}\nOverflow: {}".format(
            mean, std, count, nbins, ovflow)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax3.text(0.90,
                 0.95,
                 textstr,
                 transform=ax3.transAxes,
                 fontsize=5,
                 verticalalignment='top',
                 bbox=props)
        fig.tight_layout()
        if not pdf:
            plt.show()
        else:
            return fig

    def getDataFrame(self, df):
        # return self.serialize_dataframe(df, self.newFileName)
        return parallelize_dataframe(df, self.completeDataFrame,
                                     self.newFileName)

    def serialize_dataframe(self, df, path):
        df = self.completeDataFrame(df)
        feather.write_dataframe(df, path)
        return df

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

    def getHistogram(self, queryName, title="", nbins=200, pdf=False):
        s = self.events_df[queryName]
        # plt.figure(figsize=(3, 3))
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
        if not pdf:
            plt.show()
        else:
            return ax

    def getKDE(self, queryName, nbins=200):
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

    def getFilteredHistogram(self, queryName, filter, nbins=200, title=""):
        self.events_df.hist(column=queryName, bins=nbins, by=filter)
        plt.suptitle("Histograms of {} grouped by {} {}".format(
            queryName, filter, title))
        plt.ylabel("Frequency")
        plt.show()

    def getComparableHistogram(self, queries, nbins=200, title=""):
        s = pd.DataFrame(columns=queries)
        s = s.fillna(0)  # with 0s rather than NaNs
        for query in queries:
            s[query] = self.events_df[query]
        ax = s.plot.hist(alpha=0.6, bins=nbins)
        plt.title("Histogram of {} {}".format(str(queries), title))
        plt.show()

    def get2DHistogram(self,
                       xvals,
                       yvals,
                       title,
                       xlabel,
                       ylabel,
                       xmin,
                       xmax,
                       ymin,
                       ymax,
                       nbins=150,
                       pdf=False):
        name = title.replace(" ", "") + "_run_" + self.runNum
        self.pdfList.append(name)
        if not pdf:
            Histo2D(name, title, xlabel, nbins, xmin, xmax, xvals, ylabel,
                    nbins, ymin, ymax, yvals, pdf)
        else:
            return Histo2D(name, title, xlabel, nbins, xmin, xmax, xvals,
                           ylabel, nbins, ymin, ymax, yvals, pdf)

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

    def getFilteredPlot(self, term, value, cond, title=""):
        self.keepEvents(term, value, cond)
        self.getPlot(term, title=title)
        self.reload()

    @dispatch(str)
    def getPlot(self, query):
        self.events_df[query].plot()
        plt.xlabel("Event Number")
        plt.ylabel(str(query))
        plt.title("Plot of {} event series ".format(query))
        plt.show()

    @dispatch(list)
    def getPlot(self, queries, title=""):
        plt.plot(self.events_df[queries[0]].values,
                 self.events_df[queries[1]].values)
        plt.xlabel(str(queries[0]))
        plt.ylabel(str(queries[1]))
        plt.title("Line Plot of {} against {} {}".format(
            queries[0], queries[1], title))
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

    def keepEvents(self, term, value, cond):
        if cond == "<":
            self.events_df = self.events_df[self.events_df[term] < value]
        elif cond == ">":
            self.events_df = self.events_df[self.events_df[term] > value]
        elif cond == "==":
            self.events_df = self.events_df[self.events_df[term] == value]
        elif cond == ">=":
            self.events_df = self.events_df[self.events_df[term] >= value]
        elif cond == "<=":
            self.events_df = self.events_df[self.events_df[term] <= value]
        elif cond == "!=":
            self.events_df = self.events_df[self.events_df[term] != value]

    # @staticmethod

    def getTrimmedHistogram(self, queryName, numStd, nbins=200):
        df_filtered = scrubbedDataFrame(self.events_df, queryName, numStd)
        getHistogram(df_filtered,
                     queryName,
                     title="(Events within {} std dev)".format(numStd),
                     nbins=nbins)

    def getTrimmed2DHistogram(df, queryName, numStd, nbins=200):
        pass

    def getTrimmedFilteredHistogram(self, queryName, numStd, nbins=200):
        df_filtered = scrubbedDataFrame(self.events_df, queryName, numStd)
        getFilteredHistogram(df_filtered,
                             queryName,
                             nbins,
                             title="(Events within {} std dev)".format(numStd))

    def getTrimmedComparableHistogram(self, queries, numStd, nbins=200):
        s = pd.DataFrame(columns=queries)
        s = s.fillna(0)  # with 0s rather than NaNs
        for query in queries:
            s[query] = scrubbedDataFrame(self.events_df, query, numStd)[query]
        ax = s.plot.hist(alpha=0.7, bins=nbins, histtype='step')
        plt.title("Histogram of {} (Events within {} std dev)".format(
            str(queries), numStd))
        plt.show()
